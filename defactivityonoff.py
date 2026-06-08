import os
import re
import pdb
import pandas as pd
import numpy as np
import matplotlib.mlab as ml
import matplotlib.pyplot as plt
import circaPy.activity as act
import scipy.signal as sig
#from scipy.signal import detrend
import circaPy.preprocessing as prep

data = pd.read_csv(
   '/Users/ayobamifawole/Desktop/Home Cage Data Analysis Python/Test Data/LTC_7b_2025-04-25T_modified.csv', 
    index_col = 'Time', 
    parse_dates = True)

# Remove whitespace from all headers
data.columns = [x.strip() for x in data.columns]
# Delete device column 
data.pop('Device')

#print(data.head())


# set 10s index frequency
data_resample10s = data.resample('10s').mean()
data_resample10s.fillna(0, inplace=True)


#Check any missing PIR data ~ will check LDR too
#print(data.isnull().sum())

def mean_activity(data, 
                   col = 0,
                   mean1 = 3,
                   mean2 = 24,
                   **kwargs):
    
    '''
    This works to plot mean1 against mean2 as long as mean1 is < mean2
    
    data : pd.DataFrame
        Input DataFrame with time-series data. The index represents time, and
        the columns contain observations.
    col: int
        automatically sets 0 for column 1 of df
    mean1: int
        first rolling average to calculate
    mean2: int
        2nd rolling average to calculate

    Next Step:
        figure out how to pull where the overlap occurs as this is the time of activity onset/offset respectively
            or
        figure out how to pull where the difference between mean1-mean2
        transitions + to - (offset ~ lights on) or - to + (onset ~ lights off)

        issue is... this transition also happen during dark period where bouts end/begin
            so how to diffrentiate between begining of dark period vs end
        
    '''

    #resample df to 1hr bins
    data_resample1h = data.resample('1h').mean()
        #col_data = data_resample1h.columns[col]
    #PIR column selection
    curr_data = data_resample1h.iloc[:, col]
        #pir = data_resample1h.iloc[col]

    #raise error for selected bin values, mean2 had to be > mean1
    if mean2 <= mean1:
        raise ValueError (
            f"mean1 must be less than mean2."
        )

    #calculate the rolling averages
    avg1 = curr_data.rolling(window=f'{mean1}h', min_periods = mean1).mean()
    avg2 = curr_data.rolling(window=f'{mean2}h', min_periods = mean2).mean()
    
    #difference between mean2 and mean1 avgs
    dif = avg1 - avg2

    new_df = [avg1, avg2]

    #where dif = 0 is overlap
        #would pos be onset and neg be offset?
    #if dif < 1:
       #overlap = 

    fig, ax = plt.subplots(figsize = (16, 4))
    ax.plot(avg1)
    ax.plot(avg2)
    #ax.plot(dif) # 3rd line to visually rep the differnece 
    ax.set_xlabel("Time (hr)")
    ax.set_ylabel("Freq")
    plt.show()

    if kwargs.get('to_csv'):
        new_df.to_csv("activityavgs.csv")


    return fig, ax


#mean_activity(sp_linear_data_resample10s, mean1 = 3, mean2 = 24)


def onset_offset(data, 
                   col = 0,
                   mean1 = 3,
                   mean2 = 24,
                   **kwargs):
   
    '''
    This works to plot mean1 against mean2 as long as mean1 is < mean2
    
    data : pd.DataFrame
        Input DataFrame with time-series data. The index represents time, and
        the columns contain observations.
    col: int
        automatically sets 0 for column 1 of df
    mean1: int
        first rolling average to calculate
    mean2: int
        2nd rolling average to calculate
        
    '''

    #raise error for selected bin values, mean2 had to be > mean1
    if mean2 <= mean1:
        raise ValueError (
            f"mean1 must be less than mean2."
        )
        
        #resample df to 1hr bins
    data_resample1h = data.resample('1h').mean()
        #col_data = data_resample1h.columns[col]
    #PIR column selection
    curr_data = data_resample1h.iloc[:, col]
        #pir = data_resample1h.iloc[col]
    col_name = data_resample1h.columns[col]

    my_i = data_resample1h.index
    new_df = pd.DataFrame(curr_data).set_index(my_i)


        #calculate the rolling averages
    new_df['Avg1'] = curr_data.rolling(window = f'{mean1}h', min_periods = mean1).mean()
    new_df['Avg2'] = curr_data.rolling(window = f'{mean2}h', min_periods = mean2).mean()
        #difference between mean2 and mean1 avgs
    new_df['Dif'] = new_df['Avg1'] - new_df['Avg2']

    # make a mask to mark + and - values (boolean)
    pos_mask = (new_df['Dif'] > 0) & (new_df['Dif'].shift(1) < 0)
    neg_mask = (new_df['Dif'] < 0) & (new_df['Dif'].shift(1) > 0)


    if kwargs.get('to_csv'):
        new_df.to_csv("activitydif.csv")

    if kwargs.get('showfig'):
        fig, ax = plt.subplots(figsize = (16, 4))
        line1 = plt.plot(new_df.index, new_df['Dif'], color = 'black')
        line2 = plt.scatter(new_df.index[pos_mask], new_df.loc[pos_mask, 'Dif'], color = 'green')
        line3 = plt.scatter(new_df.index[neg_mask], new_df.loc[neg_mask, 'Dif'], color = 'red')
        ax.set_xlabel('Time')
        ax.set_ylabel('Frequency')
        ax.set_title(f'{mean1} vs {mean2} Activity Frequency {col_name}')
        plt.legend(['PIR Mean Difference', 'Activity Onset', 'Activity Offset'])
        plt.show()
        return fig, ax

    return new_df


onset_offset(data_resample10s, col = 1, mean1 = 3, mean2 = 24, showfig = True, to_csv = False)
#onset_offset(dt_data_resample10s, col = 1, mean1 = 3, mean2 = 24, to_csv = True)


def clocklab_onoff(data,
                   col = 0,
                   m_hours = 6,
                   n_hours = 6,
                   **kwargs):

    '''
    Clocklab Method Implementation

    1. determine 20th percentile of overall activity ~ activity level the exceeds 20% of all non-0 cts
    2. convert data into -1 (below percentile) and +1 (above percentile) ~ threshold
    3. N hours of -1s and M hours of +1s
        N = 6 (inactivity), M = 6 (activity)
    4. Onset is the max of this convolution

    '''
    
        ##does this work without resampling to 1hr?
    #resample df to 1hr bins
    data_resample1h = data.resample('1h').mean()

    #PIR column selection
    curr_data = data_resample1h.iloc[:, col]
    col_name = data_resample1h.columns[col]

    #format new df with selected PIR column
    my_i = data_resample1h.index
    new_df = pd.DataFrame(curr_data).set_index(my_i)

        ##do i need to fill NaNs?


    #filter out 0s
    filtered_data = new_df.loc[new_df[col_name] > 0]
    #Calculate threshold ~ 20%
        # need count of data points
    n = len(filtered_data)
    index_rank = int((20/100) * n)

    #create mask of the threshold value +1/-1 for given activity data
    mask = filtered_data.iat[index_rank, 0] # works but needs row and column parameter

    threshold = [
    (new_df[col_name] >= mask),
    (new_df[col_name] < mask)
             ]

    condition = [1, -1]

    new_df[col_name] = np.select(threshold, condition)
    ldr = data_resample1h['LDR'] / 100 # divided by 100 so we can see on same scale as the mask

    #make the templates to convolve with the threshold activity
    on_template = np.concatenate([np.full(n_hours, -1),
                           np.full(m_hours, 1)
                           ])

    off_template = np.concatenate([np.full(m_hours, 1),
                            np.full(n_hours, -1)
                            ])

    # convolve
    compare1 = sig.correlate(new_df[col_name], on_template, mode = 'same')
    compare2 = sig.correlate(new_df[col_name], off_template, mode = 'same')

    new_df['Comparison N-M'] = compare1
    new_df['Comparison M-N'] = compare2

    # Need to get table of all the max/min values
    match_index_max1 = new_df['Comparison N-M'].idxmax()
    match_index_max2= new_df['Comparison M-N'].idxmax()
    match_value_max1 = new_df.loc[match_index_max1, 'Comparison N-M']
    match_value_max2 = new_df.loc[match_index_max2, 'Comparison M-N']

    if kwargs.get('showfig'):
        fig, ax = plt.subplots(figsize = (16, 4))
        line1 = plt.plot(new_df.index, new_df['Comparison N-M'], color = 'black')
        ax.set_xlabel('Time')
        ax.set_ylabel('Frequency')
        ax.set_title(f'{n_hours} vs {m_hours} Activity Frequency {col_name}')
        #plt.legend(['PIR Mean Difference', 'Activity Onset', 'Activity Offset'])
        plt.show()
        return fig, ax

    if kwargs.get('to_csv'):
        new_df.to_csv("CL onoff.csv")


    return new_df


#clocklab_onoff(data_resample10s, col = 1, n_hours = 6, m_hours = 6, to_csv = True)




'''

data_resample1h = data.resample('1h').mean()
data = data_resample1h['PIR2']

data_resample1h.drop(columns = ['PIR2', 'PIR3', 'PIR3', 'PIR4', 'PIR5', 'PIR6',], inplace = True)
data_resample1h.fillna(0, inplace=True)

day_data = data_resample1h.loc['2025-04-28': '2025-04-30']


# filter out 0s, make new DF with selected PIR
filtered_data = day_data.loc[day_data['PIR1'] > 0]

# Convert dtpye
#filtered_data = filtered_data.astype({'PIR1': 'int64'})

n = len(filtered_data)

rank = (0.2 * n) # gives straight numerical value, not rlyyy the index
index_rank = int((20/100) * n) # use this one, gives integer


mask = filtered_data.index[index_rank]
percent = filtered_data.loc[mask]
value = filtered_data.iat[index_rank, 0] # works but needs row and column parameter

threshold = [
    (day_data['PIR1'] >= value),
    (day_data['PIR1'] < value)
             ]

condition = [1, -1]

day_data['PIR1'] = np.select(threshold, condition)
ldr = day_data['LDR'] / 100

# need to make the N and M template
#21,600 ~ 10sbins in 6hrs
on = 2 #hours
off = 6 #hours

n_segment = off 
m_segment = on 

on_template = np.concatenate([np.full(n_segment, -1),
                           np.full(m_segment, 1)
                           ])

off_template = np.concatenate([np.full(m_segment, 1),
                           np.full(n_segment, -1)
                           ])

    # ValueError: Acceptable mode flags are 'valid', 'same', or 'full'.
compare1 = sig.correlate(day_data['PIR1'], on_template, mode = 'same')
compare2 = sig.correlate(day_data['PIR1'], off_template, mode = 'same')

day_data['Comparison 1'] = compare1
day_data['Comparison 2'] = compare2
day_data['PIR1.'] = data.loc['2025-04-28': '2025-04-30']

match_index_max1 = day_data['Comparison 1'].idxmax()
match_index_max2= day_data['Comparison 2'].idxmax()
match_index_min1 = day_data['Comparison 1'].idxmin()
match_index_min2 = day_data['Comparison 2'].idxmin()
match_value_max1 = day_data.loc[match_index_max1, 'Comparison 1']
match_value_max2 = day_data.loc[match_index_max2, 'Comparison 2']
match_value_min1 = day_data.loc[match_index_min1, 'Comparison 1']
match_value_min2 = day_data.loc[match_index_min2, 'Comparison 2']

#print("Max Comparison 1:", match_index_max1, match_value_max1)
#print("Max Comparison 2:", match_index_max2, match_value_max2)
#print("Min Comparison 1:",match_index_min1, match_value_min1)
#print("Min Comparison 2:",match_index_min2, match_value_min2)

day_data.to_csv("compare2.csv")
'''


'''
print(day_data['Comparison 1'].head())
ldr.plot(figsize = (16, 4))
day_data['Comparison 1'].plot(figsize = (16, 4))
plt.show()
'''



