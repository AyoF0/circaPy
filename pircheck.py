import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.signal as sig
import circaPy.preprocessing as prep


def dailyactivity_counts(data):
    '''
    This function works to quantify how may rows of data were collected for each day in the dataset
    '''

    top = data.index.min() #lable begining of index
    bottom = data.index.max()

    values = []
    
    startdate = top
    #start_new = data.loc['2026-05-21T00:00:02.970Z']

    while startdate < bottom:
        nextday = startdate + pd.Timedelta(hours = 24) #add 24hrs from start
        #count = len(data.loc[startdate : nextday]) #produces row count between start date - 24hr variables
        count = ((data.index >= startdate) & (data.index < nextday)).sum()

        values.append({
            "Date": startdate,
            "Daily Counts": count
        })

        startdate = nextday

    final_counts = pd.DataFrame(values)
    #final_counts.index.name = "Day"
    final_counts.set_index('Date', inplace = True)
    #final_counts['Reading_Number'] = range(1, len(final_counts) + 1) "Date": startdate.strftime('%Y-%m-%d %H:%M:%S'),
    return final_counts



### Read data
data = pd.read_csv(
    '/Users/ayobamifawole/Desktop/Home Cage Data Analysis Python/Test Data/LTC_7c_2025-04-25T_modified.csv', 
    index_col = 'Time', 
    parse_dates = True)

### Remove whitespace from all headers
data.columns = [x.strip() for x in data.columns]
### Delete column(s) you don't need from the dataset
data.pop('Device')

### Count the amount of data and NaNs for the read data
#print('Raw Counts:\n', dailyactivity_counts(data))
#print('NaN Counts:\n', data.isnull().sum())


### Resample timedate index so everything is properly binned, can change frequency
#data_resample = data.resample('10s').mean()

### Export resampled data as csv,  if you want to check it
#data_resample.to_csv("reasample_nancheck.csv")

'''
### Count the amount of data and NaNs for the resampeled data
print('Resample Raw Counts:\n', dailyactivity_counts(data_resample))
print('Resample NaN Counts:\n', data_resample.isnull().sum())


### Check what timestamps are left as NaNs after resampling the index
location_nan = data_resample[data_resample.isnull().any(axis = 1)].index.tolist()
print(location_nan)
'''

### Fill the NaN rows of data with previous rows data
#data_resample_fill = data_resample.ffill()

'''
### Export filled data as csv,  if you want to check it
data_resample_fill.to_csv("fill_nancheck.csv")

### Check amount of counted data and NaNs for the NaN filled data
print('Fill Raw Counts:\n', dailyactivity_counts(data_resample_fill))
print('Fill NaN Counts:\n', data_resample_fill.isnull().sum())
'''

def cleanup(data, freq = '10s', to_csv = False, **kwargs):

    '''
    create a function to forward fill NaN rows of data

    data: pd.DataFrame
    Input DataFrame with time-series data. The index represents time, and
    the columns contain observations.
    freq:
    set bin to resample timedate index to
    default resample freq is 10 seconds

    '''

    data_resample = data.resample(freq).mean()
    data_resample_fill = data_resample.ffill()

    if to_csv == True:
        data_resample_fill.to_csv("cleanedDF.csv")

    return


df_clean = cleanup(data, to_csv = True)

data_clean = pd.read_csv(
    '/Users/ayobamifawole/Desktop/Home Cage Data Analysis Python/AFclone/cleanedDF.csv', 
    index_col = 'Time', 
    parse_dates = True)

print(data_clean.head())

print(dailyactivity_counts(data_clean))
print('NaN Counts:\n', data_clean.isnull().sum())