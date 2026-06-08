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

# set 10s index frequency
data_resample10s = data.resample('10s').mean()
data_resample10s.fillna(0, inplace=True)


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
    new_df['Detrend'] = new_df[col_name] - new_df['Avg2']

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


#onset_offset(data_resample10s, col = 1, mean1 = 3, mean2 = 24, to_csv = True)
#onset_offset(dt_data_resample10s, col = 1, mean1 = 3, mean2 = 24, to_csv = True)




def sp_detrend_linear(data, 
                   col = 0,
                   mean1 = 3,
                   mean2 = 24,
                   **kwargs):
    
    '''
    This works to plot mean1 against mean2 as long as mean1 is < mean2
    sciPy detrend funciton can handle 2D arrays
    
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
    # sp_linear_data_resample10s = sig.detrend(data_resample1h, type = 'linear')
    #resample df to 1hr bins
    data_resample1h = data.resample('1h').mean()
    pir = data_resample1h.iloc[:, col]
        #col_data = data_resample1h.columns[col]
    #PIR column selection
    detrend = sig.detrend(data_resample1h, type = 'linear')
    ddata = pd.DataFrame(detrend)
    my_i = data_resample1h.index
    ddata.index = my_i

    curr_data = ddata.iloc[:, col]
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

    table = pd.concat([pir, curr_data, avg1, avg2], axis = 1)
    table.columns = ['OG Pir', 'Detrended PIR', '3hr Avg', '24hr Avg']

    #where dif = 0 is overlap
        #would pos be onset and neg be offset?
    #if dif < 1:
       #overlap = 

    fig, ax = plt.subplots(figsize = (16, 4))
    #ax.plot(curr_data)
    ax.plot(avg1)
    ax.plot(avg2)
    #ax.plot(pir)
    #ax.plot(dif) # 3rd line to visually rep the differnece 
    ax.set_xlabel("Time (hr)")
    ax.set_ylabel("Freq")
    plt.show()

    if kwargs.get('to_csv'):
        table.to_csv("sp_detrend_linear.csv")


    return fig, ax

#sp_detrend_linear(data, col = 0, mean1 = 3, mean2 = 24, to_csv = True)


def sp_detrend_constant(data, 
                   col = 0,
                   mean1 = 3,
                   mean2 = 24,
                   **kwargs):
    
    '''
    This works to plot mean1 against mean2 as long as mean1 is < mean2
    sciPy detrend funciton can handle 2D arrays
    
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
    # sp_linear_data_resample10s = sig.detrend(data_resample1h, type = 'linear')
    #resample df to 1hr bins
    data_resample1h = data.resample('1h').mean()
    pir = data_resample1h.iloc[:, col]
        #col_data = data_resample1h.columns[col]
    #PIR column selection
    detrend = sig.detrend(data_resample1h, type = 'constant')
    ddata = pd.DataFrame(detrend)
    my_i = data_resample1h.index
    ddata.index = my_i

    curr_data = ddata.iloc[:, col]
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

    table = pd.concat([pir, curr_data, avg1, avg2], axis = 1)
    table.columns = ['OG Pir', 'Detrended PIR', '3hr Avg', '24hr Avg']

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
        table.to_csv("sp_detrend_constant.csv")


    return fig, ax

#sp_detrend_constant(data, col = 0, mean1 = 3, mean2 = 24, to_csv = True)


def mp_detrend_linear(data, 
                   col = 0,
                   mean1 = 3,
                   mean2 = 24,
                   **kwargs):
    
    '''
    This works to plot mean1 against mean2 as long as mean1 is < mean2
    matplotlib.mlab detrend funciton can only handle 1D arrays
    
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
    # sp_linear_data_resample10s = sig.detrend(data_resample1h, type = 'linear')
    #resample df to 1hr bins
    data_resample1h = data.resample('1h').mean()
    pir = data_resample1h.iloc[:, col]
        #col_data = data_resample1h.columns[col]
    #PIR column selection
    curr_data = data_resample1h.iloc[:, col]
        #pir = data_resample1h.iloc[col]

    detrend = ml.detrend_linear(curr_data)
    ddata = pd.DataFrame(detrend)
    my_i = data_resample1h.index
    ddata.index = my_i
    
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

    table = pd.concat([pir, curr_data, avg1, avg2], axis = 1)
    table.columns = ['OG Pir', 'Detrended PIR', '3hr Avg', '24hr Avg']

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
        table.to_csv("mp_detrend_linear.csv")


    return fig, ax

#mp_detrend_linear(data, col = 0, mean1 = 3, mean2 = 24, to_csv = True)


def mp_detrend_mean(data, 
                   col = 0,
                   mean1 = 3,
                   mean2 = 24,
                   **kwargs):
    
    '''
    This works to plot mean1 against mean2 as long as mean1 is < mean2
    matplotlib.mlab detrend funciton can only handle 1D arrays
    
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
    # sp_linear_data_resample10s = sig.detrend(data_resample1h, type = 'linear')
    #resample df to 1hr bins
    data_resample1h = data.resample('1h').mean()
    pir = data_resample1h.iloc[:, col]
        #col_data = data_resample1h.columns[col]
    #PIR column selection
    curr_data = data_resample1h.iloc[:, col]
        #pir = data_resample1h.iloc[col]

    detrend = ml.detrend_mean(curr_data)
    ddata = pd.DataFrame(detrend)
    my_i = data_resample1h.index
    ddata.index = my_i
    
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

    table = pd.concat([pir, curr_data, avg1, avg2], axis = 1)
    table.columns = ['OG Pir', 'Detrended PIR', '3hr Avg', '24hr Avg']

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
        table.to_csv("mp_detrend_mean.csv")


    return fig, ax

mp_detrend_mean(data, col = 0, mean1 = 3, mean2 = 24, to_csv = True)
