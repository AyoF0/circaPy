import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import circaPy.preprocessing as prep

data = pd.read_csv(
    "/Users/ayobamifawole/Desktop/Home Cage Data Analysis Python/Test Data/LTC_7c_2025-04-25T_modified.csv", 
    index_col = 'Time', 
    parse_dates = True)

data.columns = [x.strip() for x in data.columns]
# Delete device column 
data.pop('Device')
data.fillna(0, inplace=True)
# set 10s index frequency
data_resample = data.resample('10s').mean()
# Fill NaNs with 0
data_resample.fillna(0, inplace=True)

print(data.head())

prep.set_circadian_time(data, period = '24h')

print(data.head())