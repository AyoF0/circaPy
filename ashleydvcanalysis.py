import re
import pdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import circaPy.preprocessing as prep
import circaPy.plots as cplt
import circaPy.activity as act



### BL Data
'''
'''
bl_data = pd.read_csv(
    '/Volumes/AF SSD/Ashley DVC/Baseline WOHT LPS Raw locomotive data 7 am/animal_locomotion_index.csv',
    index_col = 'WOHT_Hom_Male_TIMESTAMP',
    parse_dates = True)


### Remove whitespace from all headers
bl_data.columns = [x.strip() for x in bl_data.columns]
#print(bl_data.columns.tolist())

### Make new df from activity data only
bl_keep_cols = ['WOHT_Hom_Male_AVG', 
             'WOHT_WT_Female_AVG', 
             'WOHT_WT_Male_AVG', 
             'WOHT_Hom_Female_AVG']


bl_data_filterd = bl_data[bl_keep_cols].copy()
#print(bl_data.columns.tolist())


bl_data_resample = bl_data_filterd.resample('1min').mean()

bl_repeat_sch = np.repeat([300, 0], 720)
mask = int(np.ceil(len(bl_data_resample) / len(bl_repeat_sch)))
bl_data_resample['LD'] = np.tile(bl_repeat_sch, mask)[:len(bl_data_resample)]

#print(bl_data_filterd.columns.tolist())
#bl_data_resample.to_csv("bltestingtesting.csv")

bl_data_resample.fillna(0, inplace=True)

#print(bl_data_resample.max())

#cplt.plot_actogram(bl_data_resample, col = 0, ylim=[0, 10], showfig = True)
cplt.plot_activity_profile(bl_data_resample)


### W1 Data

'''
w1_data = pd.read_csv(
    '/Volumes/AF SSD/Ashley DVC/Week 1 WOHT LPS Raw locomotive data 7am Tuesday/animal_locomotion_index.csv',
    index_col = 'WOHT_Hom_Male_B_TIMESTAMP',
    parse_dates = True)

w1_data.columns = [x.strip() for x in w1_data.columns]
#print(w1_data.columns.tolist())

w1_keep_cols = ['WOHT_Hom_Male_B_AVG', 
             'WOHT_WT_Female_LPS_A_AVG', 
             'WOHT_WT_Female_LPS_B_AVG', 
             'WOHT_WT_Male_A_AVG',
             'WOHT_Hom_Male_A_AVG',
             'WOHT_Hom_Female_LPS_A_AVG',
             'WOHT_Hom_Female_LPS_B_AVG',
             'WOHT_WT_Male_B_AVG']


w1_data_filterd = w1_data[w1_keep_cols].copy()
w1_data_resample = w1_data_filterd.resample('1min').mean()


w1_repeat_sch = np.repeat([300, 0], 720)
mask = int(np.ceil(len(w1_data_resample) / len(w1_repeat_sch)))
w1_data_resample['LD'] = np.tile(w1_repeat_sch, mask)[:len(w1_data_resample)]

#print(w1_data_filterd.head())
#print(w1_data_filterd.columns.tolist())

#w1_data_resample.to_csv("w1testingtesting.csv")

w1_data_resample.fillna(0, inplace=True)
w1_data_resample2 = w1_data_resample.resample('1min').mean()
w1_data_resample2.fillna(0, inplace=True)

#print(w1_data_resample2.max())

cplt.plot_actogram(w1_data_resample2, linewidth = 1, col = 7, ylim=[0, 5], showfig = True)
'''


### W2 Data

'''
w2_data = pd.read_csv(
    '/Volumes/AF SSD/Ashley DVC/Week 2 WOHT LPS Raw locomotive data 7am Tuesday/animal_locomotion_index.csv',
    index_col = 'WOHT_WT_Female_LPS_A_TIMESTAMP',
    parse_dates = True)

print(w2_data.index.dtype)
w2_data.columns = [x.strip() for x in w2_data.columns]

w2_data.index = pd.to_datetime(w2_data.index, utc=True)

w2_keep_cols = ['WOHT_WT_Female_LPS_A_AVG', 
             'WOHT_WT_Male_B_AVG', 
             'WOHT_WT_Female_LPS_B_AVG', 
             'WOHT_Hom_Male_A_AVG',
             'WOHT_Hom_Male_B_AVG',
             'WOHT_Hom_Female_LPS_B_AVG',
             'WOHT_Hom_Female_LPS_A_AVG',
             'WOHT_WT_Male_A_AVG']


w2_data_filterd = w2_data[w2_keep_cols].copy()
#print(w2_data_filterd.columns.tolist())

w2_data_resample = w2_data_filterd.resample('1min').mean()

w2_repeat_sch = np.repeat([300, 0], 720)
mask = int(np.ceil(len(w2_data_resample) / len(w2_repeat_sch)))
w2_data_resample['LD'] = np.tile(w2_repeat_sch, mask)[:len(w2_data_resample)]

#w2_data_resample.to_csv("w2testingtesting.csv")
w2_data_resample.fillna(0, inplace=True)

#print(w2_data_resample.max())

#cplt.plot_actogram(w2_data_resample, col = 2, ylim=[0, 10], showfig = True)
'''