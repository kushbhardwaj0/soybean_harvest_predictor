# -*- coding: utf-8 -*-
"""Soybean_Harvesting_Rate.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ei-xZIb7T0wPBhbDkrF6wYP3uwaCNZHM
"""

#total runtime is about 2 minutes

#importing necessary stuff
#!pip install anvil-uplink
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

#stuff for the website to work
import anvil.server

anvil.server.connect("server_GECNSTZJHSMQ3XDGIFVNHQN3-HFCC7QLCLAZM5MPJ")

from google.colab import drive
drive.mount('/content/drive')

#load the data
weather_data = pd.read_csv('/content/drive/MyDrive/Louisiana_Data/Alexandria.csv')
soybean_data = pd.read_csv('/content/drive/MyDrive/soybean.csv')

# making sure year is machine readable
weather_data['Year'] = pd.to_datetime(weather_data['Year'], format='%Y')
if soybean_data['Year'].dtype == 'object': # Only apply if the column is of type object (string)
    soybean_data['Year'] = pd.to_numeric(soybean_data['Year'].str.replace(',', ''), errors='coerce')
soybean_data['Year'] = pd.to_datetime(soybean_data['Year'], format='%Y', errors='coerce') # Handle potential errors

#removing commas and making it numbers
if soybean_data['acres harvested'].dtype == 'object':
    soybean_data['acres harvested'] = pd.to_numeric(soybean_data['acres harvested'].str.replace(',', '').str.strip(), errors='coerce')
if soybean_data['acres planted'].dtype == 'object':
    soybean_data['acres planted'] = pd.to_numeric(soybean_data['acres planted'].str.replace(',', '').str.strip(), errors='coerce')

#merging files
data = pd.merge(weather_data, soybean_data, on='Year')

#making data numerical
if soybean_data['acres harvested'].dtype == 'object':
    soybean_data['acres harvested'] = pd.to_numeric(soybean_data['acres harvested'].str.replace(',', '').str.strip(), errors='coerce')
if soybean_data['acres planted'].dtype == 'object':
    soybean_data['acres planted'] = pd.to_numeric(soybean_data['acres planted'].str.replace(',', '').str.strip(), errors='coerce')

#merging sheets
data = pd.merge(weather_data, soybean_data, on='Year')

#calculate harveting rates: harvested / planted
data['harvesting_rate'] = data['acres harvested'] / data['acres planted']
#any random columns in data are removed as not to mess up the model
data.drop(columns=['Filename', 'Unnamed: 12', 'Location_x', 'Location_y'], inplace=True)
#removing rows with any nil values
data.dropna(inplace=True)

#dropping any useless columns that are not needed
features = data.drop(columns=['Year', 'harvesting_rate', 'acres harvested', 'acres planted'])
print(features.head())
target = data['harvesting_rate']

#splittin the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

#actually training the model :D
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

#making the predictions
y_pred = model.predict(X_test)

#checking the accuracy of the model - lower the number the better
#last checked error: 0.050984 --> VERY GOOD
mae = mean_absolute_error(y_test, y_pred)
print(f'Mean Absolute Error: {mae}')

#setting up the website
@anvil.server.callable
def predict_harvesting_rate(high_temp, low_temp, max_wind, min_wind, wind_direction, max_humid,
                            min_humid, solar_rad, max_soil_temp, min_soil_temp, rain):
    """
    Predict the harvesting rate based on user input features.

    Parameters:
    user_input (dict): Dictionary with keys as feature names and values as feature values.

    Returns:
    float: Predicted harvesting rate.
    """
    user_input = {
      'Max Air Temp (°F)': high_temp,
      'Min Air Temp (°F)': low_temp,
      'Rain (in)': rain,
      'Max Wind Speed (mph)': max_wind,
      'Avg Wind Speed (mph)': min_wind,
      'Avg Wind Direction (°)': wind_direction,
      'Max Rel Humid': max_humid,
      'Min Rel Humid': min_humid,
      'Solar Rad': solar_rad,
      'Max Soil Temp (°F)': max_soil_temp,
      'Min Soil Temp (°F)': min_soil_temp
    }




    input_df = pd.DataFrame(user_input, index=[0])
    prediction = model.predict(input_df)
    return prediction[0]

anvil.server.wait_forever()