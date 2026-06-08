import re
import pdb
import pandas as pd
import numpy as np
# Import the circaPy functions you want to use
#import circaPy.___ as ___
import circaPy.plots as plots


# This uploads the data set you want to use, copy and paste file pathname inside the ' ' 
# index_col = ' ' ~ use this to assign the index column of your dataset
data = pd.read_csv(
    '/Users/ayobamifawole/Desktop/Home Cage Data Analysis Python/AFclone/copy6C, PIR3, ZT3 copy.csv', 
    index_col = 'Time', 
    parse_dates = True)

# Clear whitespace in data headers
data.columns = [x.strip() for x in data.columns]


# The remove = variable and .drop function allows you to remove any columns you don't want to analyze in your data set
remove = ['Device', 'Unnamed: 9','Unnamed: 10', 'Unnamed: 11', 'Unnamed: 12', 'Unnamed: 13', 'Unnamed: 14', 'Unnamed: 15', 'Unnamed: 16']
data = data.drop(columns = remove)

# Fill NaNs with 0, can change the numerical value to what you want
data.fillna(0, inplace=True)


# This checks your PIR data is a float64 dtype which is needed for circaPy funcitons
data = data.astype(({'PIR1': 'float64', 
                     'PIR2': 'float64', 
                     'PIR3': 'float64', 
                     'PIR4': 'float64', 
                     'PIR5': 'float64', 
                     'PIR6': 'float64', 
                     'LDR': 'int64'}))





# Resample your data to the wanted evenly spaced bins
data_resample10s = data.resample('10s').mean()

# You might need to refill NaNs after resampling
#data_resample10s.fillna(0, inplace=True)


plots.plot_actogram(data_resample10s, showfig = True)


