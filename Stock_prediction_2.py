# Import libraries
import pandas as pd
import yfinance as yf
from neuralprophet import NeuralProphet
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Function to get business dates
def get_business_dates():
    today = pd.to_datetime("today").normalize()
    
    if today.weekday() >= 5:  # if today is Saturday (5) or Sunday (6)
        today -= pd.offsets.BDay()  # move to the previous business day
    
    start_date = pd.Timestamp(year=today.year - 6, month=1, day=1)
    return start_date, today

# Get the business dates
start_date, end_date = get_business_dates()

# Download the USDCLP data from Yahoo Finance
currency_pair = 'USDCLP=X'
currency_data = yf.download(currency_pair, start=start_date, end=end_date)

# Data preparation
currency_data.reset_index(inplace=True)
currency_data = currency_data[['Date', 'Close']]
currency_data.columns = ['ds', 'y']

# Check for missing data
currency_data = currency_data.dropna()

# Plot actual data
plt.figure(figsize=(12, 6))
plt.plot(currency_data['ds'], currency_data['y'], label='Actual', color='green')
plt.title('USDCLP Historical Data')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

# Initialize and fit the NeuralProphet model
model = NeuralProphet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
model.fit(currency_data, freq='D')

# Create future dataframe
future = model.make_future_dataframe(df=currency_data, periods=60)  # Predict for the next 60 days
forecast = model.predict(future)

# Plot forecast
plt.figure(figsize=(12, 6))
plt.plot(currency_data['ds'], currency_data['y'], label='Actual', color='green')
plt.plot(forecast['ds'], forecast['yhat1'], label='Forecast', color='blue')
plt.fill_between(forecast['ds'], forecast['yhat1_lower'], forecast['yhat1_upper'], color='blue', alpha=0.2)
plt.title('USDCLP Forecast')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

# Plot forecast components
model.plot_components(forecast)
plt.show()

# Model evaluation
# Split the data into training and test sets
train_size = int(len(currency_data) * 0.8)
train_data = currency_data[:train_size]
test_data = currency_data[train_size:]

# Train the model on training data
model = NeuralProphet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
model.fit(train_data, freq='D')

# Predict on test data
future_test = model.make_future_dataframe(df=train_data, periods=len(test_data))
forecast_test = model.predict(future_test)

# Calculate evaluation metrics
y_true = test_data['y'].values
y_pred = forecast_test['yhat1'][-len(test_data):].values

mae = mean_absolute_error(y_true, y_pred)
mse = mean_squared_error(y_true, y_pred)
rmse = mse ** 0.5

print(f"Mean Absolute Error: {mae}")
print(f"Mean Squared Error: {mse}")
print(f"Root Mean Squared Error: {rmse}")

# Plot the actual vs. predicted values
plt.figure(figsize=(12, 6))
plt.plot(test_data['ds'], y_true, label='Actual', color='green')
plt.plot(test_data['ds'], y_pred, label='Predicted', color='blue')
plt.title('USDCLP Actual vs Predicted')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()
