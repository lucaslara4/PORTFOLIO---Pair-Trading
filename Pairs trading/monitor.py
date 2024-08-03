import pandas as pd
import matplotlib.pyplot as plt
import tkinter
from tkinter import Tk, Label, OptionMenu, Button, StringVar, Frame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from adjustText import adjust_text  # Asegúrate de tener instalado adjustText

# Ejemplo de datos, deberías cargar tu DataFrame desde algún archivo o base de datos
df_monitorhoy = pd.DataFrame({
    'Emisor': ['Emisor1', 'Emisor2', 'Emisor3', 'Emisor4'],
    'Nemo': ['Nemo1', 'Nemo2', 'Nemo3', 'Nemo4'],
    'Duracion': [10, 20, 15, 25],
    'SPREAD_BASE': [0.5, 0.8, 1.2, 0.9],
    'Sector': ['Sector1', 'Sector2', 'Sector1', 'Sector2']
})

def top_n_by_column(df, column, n=5):
    """
    Devuelve los top n valores de una columna específica y los correspondientes valores de la columna 'Nemo'.
    
    Parameters:
    df (pd.DataFrame): DataFrame que contiene los datos.
    column (str): Nombre de la columna sobre la cual se desea ordenar y seleccionar los top n valores.
    n (int): Número de top valores a seleccionar (por defecto es 5).
    
    Returns:
    pd.DataFrame: DataFrame con los top n registros ordenados por la columna especificada.
    """
    # Verificar que la columna existe en el DataFrame
    if column not in df.columns:
        raise ValueError(f"La columna '{column}' no existe en el DataFrame.")
    
    # Ordenar el DataFrame por la columna especificada en orden descendente
    df_sorted = df.sort_values(by=column, ascending=False)
    
    # Seleccionar los top n registros
    top_n = df_sorted.head(n)
    
    return top_n

def top_n_by_ratio(df, column1, column2, n=5):
    """
    Devuelve los top n valores de la relación entre dos columnas específicas y los correspondientes valores de la columna 'Nemo'.
    
    Parameters:
    df (pd.DataFrame): DataFrame que contiene los datos.
    column1 (str): Nombre de la primera columna (numerador de la relación).
    column2 (str): Nombre de la segunda columna (denominador de la relación).
    n (int): Número de top valores a seleccionar (por defecto es 5).
    
    Returns:
    pd.DataFrame: DataFrame con los top n registros ordenados por la relación especificada.
    """
    # Verificar que las columnas existen en el DataFrame
    if column1 not in df.columns or column2 not in df.columns:
        raise ValueError(f"Las columnas '{column1}' y/o '{column2}' no existen en el DataFrame.")
    
    # Calcular la relación
    df['RATIO'] = df[column1] / df[column2]
    
    # Ordenar el DataFrame por la relación en orden descendente
    df_sorted = df.sort_values(by='RATIO', ascending=False)
    
    # Seleccionar los top n registros
    top_n = df_sorted.head(n)
    
    return top_n

def update_recommendations(df, recommendations_frame):
    column_recs = top_n_by_column(df, 'SPREAD_BASE', 5)
    ratio_recs = top_n_by_ratio(df, 'Duracion', 'SPREAD_BASE', 5)

    for widget in recommendations_frame.winfo_children():
        widget.destroy()

    label_column_recs = Label(recommendations_frame, text="Top 5 por SPREAD_BASE", font=("Arial", 12, "bold"))
    label_column_recs.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

    for i, row in column_recs.iterrows():
        sector = row['Sector']
        emisor = row['Emisor']
        nemo = row['Nemo']
        duracion = row['Duracion']
        spread_base = row['SPREAD_BASE']
        Label(recommendations_frame, text=f"Sector: {sector}, Emisor: {emisor}, Nemo: {nemo}, Duración: {duracion}, SPREAD_BASE: {spread_base}").grid(row=i+1, column=0, padx=10, pady=2)

    label_ratio_recs = Label(recommendations_frame, text="Top 5 por Relación Duración/SPREAD_BASE", font=("Arial", 12, "bold"))
    label_ratio_recs.grid(row=0, column=2, columnspan=2, padx=10, pady=5)

    for i, row in ratio_recs.iterrows():
        sector = row['Sector']
        nemo = row['Nemo']
        duracion = row['Duracion']
        spread_base = row['SPREAD_BASE']
        Label(recommendations_frame, text=f"Sector: {sector}, Nemo: {nemo}, Duración: {duracion}, SPREAD_BASE: {spread_base}").grid(row=i+1, column=2, padx=10, pady=2)

def plot_sector(df, sector, popup):
    try:
        if sector != 'Todos':
            filtered_df = df[df['Sector'] == sector].copy()  # Filtra los datos por el sector seleccionado
            fig_size = (12, 8)  # Tamaño de la figura para un sector específico
        else:
            filtered_df = df.copy()  # No filtra, usa todos los datos
            fig_size = (30, 20)  # Tamaño de la figura cuando se seleccionan "Todos"
        
        # Ajustar dinámicamente el tamaño de la figura según la cantidad de datos
        if len(filtered_df) > 50:
            fig_size = (30, 20)
        elif len(filtered_df) > 20:
            fig_size = (20, 12)
        
        # Crear la figura y el eje
        fig, ax = plt.subplots(figsize=fig_size)
        
        # Crear el gráfico de dispersión
        ax.scatter(filtered_df['Duracion'], filtered_df['SPREAD_BASE'])

        # Añadir etiquetas para cada punto con desplazamiento para evitar sobreposición
        texts = []
        for i in range(len(filtered_df)):
            emisor = filtered_df['Emisor'].iloc[i]  # Obtener el emisor
            nemo = filtered_df['Nemo'].iloc[i]
            duracion = filtered_df['Duracion'].iloc[i]
            spread_base = filtered_df['SPREAD_BASE'].iloc[i]
            texts.append(ax.annotate(f'{emisor}\n{nemo}\nD: {duracion}\nS: {spread_base}', 
                        (duracion, spread_base),
                        textcoords="offset points", 
                        xytext=(5, 5), 
                        ha='center', fontsize=9, bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="yellow")))

        # Ajustar las etiquetas para minimizar la sobreposición
        adjust_text(texts, arrowprops=dict(arrowstyle='->', color='red'))

        # Configurar el tamaño de las fuentes para el título y los labels
        ax.set_xlabel('Duración', fontsize=14)
        ax.set_ylabel('SPREAD_BASE', fontsize=14)
        ax.set_title(f'Gráfico de Dispersión entre SPREAD_BASE y Duración\nSector: {sector}', fontsize=16)
        ax.grid(True)

        # Ajustar el tamaño de las etiquetas de los ejes
        ax.tick_params(axis='both', which='major', labelsize=12)

        # Incrustar el gráfico en el popup
        canvas = FigureCanvasTkAgg(fig, master=popup)
        canvas.draw()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

    except Exception as e:
        print(f"Ocurrió un error: {e}")

def select_sector_popup(df):
    popup = Tk()
    popup.wm_title("Seleccionar Sector")
    
    label = Label(popup, text="Seleccione un sector:")
    label.pack(pady=10)
    
    sectores = ['Todos'] + df['Sector'].unique().tolist()  # Incluye "Todos" en la lista de sectores
    
    sector_var = StringVar()
    sector_var.set('Todos')  # Valor por defecto es "Todos"
    
    sector_menu = OptionMenu(popup, sector_var, *sectores)
    sector_menu.pack(pady=10)
    
    recommendations_frame = Frame(popup)
    recommendations_frame.pack(pady=10)

    update_recommendations(df, recommendations_frame)

    def apply_selection():
        selected_sector = sector_var.get()
        popup.destroy()  # Cerrar la ventana emergente
        plot_sector(df, selected_sector, popup)
    
    btn_apply = Button(popup, text="Aplicar Selección", command=apply_selection)
    btn_apply.pack(pady=10)

    return_to_main_button = Button(popup, text="Volver al Menú Principal", command=lambda: [popup.destroy()])
    return_to_main_button.pack(pady=10)
    
    popup.mainloop()

def main_menu():
    select_sector_popup(df_monitorhoy)

# Ejemplo de uso
main_menu()
