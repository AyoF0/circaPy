import re
import pdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import circaPy.preprocessing as prep
import circaPy.plots as cplt
import circaPy.preprocessing as pre
import circaPy.activity as act



@prep.validate_input
@prep.invert_light_values
@prep.plot_kwarg_decorator
def plot_activity_profile(data,
                          col = [0],
                          lights_on = 0,
                          light_col=-1,
                          subplot=None,
                          resample=False,
                          resample_freq="h",
                          *args,
                          **kwargs):
    """
    Plot the activity profile with mean and SEM (Standard Error of the Mean).
    Optionally resample the data before plotting.

    Parameters
    ----------
    data : pd.DataFrame or pd.Series
        Activity data indexed by time. If `data` is a DataFrame, the
        function uses the column specified by `col` (default is the
        first column).
    col : int, optional
        The index of the column to plot, used when `data` is a
        DataFrame (default is 0).
    lights_on : int, optional
        Light onset will be set at ZT0
        If parameter is not included in the funtion call, the plot will generate set to CT time
     light_col : int
        which columns contains light information, defaults to -1
    subplot : matplotlib.axes._axes.Axes, optional
        Subplot to plot on. If None, a new figure and axis are
        created (default is None).
    resample : bool, optional
        Whether to resample the data before plotting.
        If `True`, the data will be resampled to the frequency
        specified by `resample_freq` (default is `False`).
    resample_freq : str, optional
        The frequency to resample the data to.
        This can be any valid pandas offset string
        (e.g., "h" for hourly, "min" for minutely).
        The default is "h" (hourly).
    *args, **kwargs : additional arguments
        These are passed to the plotting function,
        such as `timeaxis` to control the appearance of the x-axis.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure containing the plot.
    ax : matplotlib.axes._axes.Axes
        The axis with the plot.
    params_dict : dict
        A dictionary containing the plot's parameters,
        including labels, title, and xlim.
    """

    # Set ZT0 for light onset
    # This only sets for st
    if lights_on > 0:
            data = data.shift(-lights_on, freq = 'h')
            ### considerations
                # this only considers the 1st light onset for the df
                # this does not work for visualizing a df with jetlag timeseries
                # assumes you're "-" time, idk what context someone would need to + but this should be added i suppose
                # shift still works for when multiple PIRs are selected to plot...but, if PIRs have dif onset this doesnt work
    
    # Select the LDR column 
    light_data = data.iloc[:, light_col]

    # Calculate mean activity and SEM for LDR
    light_mean = act.calculate_mean_activity(light_data)

    # Convert the index of mean and sem to a DatetimeIndex starting 2001-01-01
    start_date = "2001-01-01"
    freq = pd.infer_freq(data.index)
    datetime_index = pd.date_range(
        start=start_date, periods=len(light_mean), freq=freq)
    light_mean.index = datetime_index

    # Ensure freq has a numeric component
    if not any(char.isdigit() for char in freq):
        freq = pd.Timedelta('1' + freq)  # Prepend '1' if missing
    # Extend the light_mean data by one extra period and forward fill
    light_mean = pd.concat([light_mean, pd.Series(
        [light_mean.iloc[-1]], index=[light_mean.index[-1] + pd.Timedelta(freq)])])
    light_mean.ffill(inplace=True)

    num_cols = len(col)
    fig, axes = plt.subplots(nrows=num_cols, ncols=1, figsize=(10, 4 * num_cols), sharex=True)

    if num_cols == 1:
        axes = [axes]

    # Loop to plot multiple PIRs if needed
    for i, col_idx in enumerate(col):
        ax = axes[i]
        # Select the PIR Columns you want to plot as indecies (PIR1 = 0, PIR2 = 1, etc.)
        curr_data = data.iloc[:, col_idx]
        col_name = data.columns[col_idx]

        # Calculate mean activity and SEM for PIR data
        mean, sem = act.calculate_mean_activity(curr_data, sem=True)
        mean.index = datetime_index
        sem.index = datetime_index

        # Offset the mean and sem data to plot in the middle of the hour
        offset_time = 0.5 * pd.Timedelta(freq)
        mean.index += offset_time
        sem.index += offset_time
        light_mean.index += offset_time

        # Plot mean line
        ax.plot(mean.index, mean, label=f"{col_name}", color="blue", linewidth=2)

        # Plot SEM shading
        ax.fill_between(
        mean.index,
        mean - sem,
        mean + sem,
        color="blue",
        alpha=0.3,
        label="± SEM")

        xlim = [mean.index[0], (mean.index[0] + pd.Timedelta("24h"))]

        # Get ylims to set at this level later
        ylim = ax.get_ylim()
        # Find the min and max of light_mean
        min_light_mean = light_mean.min()
        max_light_mean = light_mean.max()

        # Define the target range
        target_max = 1000 * ylim[1]
        target_min = -1 * target_max

        # Scale the light_mean values to the target range
        # The formula to scale the values is:
        # scaled_value = (value - min_value) / (max_value - min_value)
        # * (target_max - target_min) + target_min
        scaled_light_mean = (light_mean - min_light_mean
                         ) / (max_light_mean - min_light_mean
                              ) * (target_max - target_min) + target_min
        

        # Add lights region
        ax.fill_between(
            scaled_light_mean.index,
            scaled_light_mean,
            color='grey',
            alpha=0.2
        )
        
        ax.set_xlabel("Time")
        #ax.set_ylabel("Activity")
        ax.set_title(f"Activity Profile with Mean and SEM: {col_name}")
        ax.set_ylim([0, ylim[1]]) # Auto-scale max, but start at 0
        ax.legend()
    
    # Return objects (the decorator will use these)
    xlim = [mean.index[0], (mean.index[0] + pd.Timedelta("24h"))]
    params_dict = {
        "xlabel": "Time(hr)",
        "ylabel": "Activity",
        "interval": 2,
        "timeaxis": True,
        "xlim": xlim,
    }

    if kwargs.get('showfig'):
         plt.show()

    return fig, ax, params_dict



data = pd.read_csv(
    '/Users/ayobamifawole/Desktop/Home Cage Data Analysis Python/Test Data/DVC Test DA.csv',
    index_col = 'WOHT_Hom_Male_TIMESTAMP',
    parse_dates = True)


# Remove whitespace from all headers
data.columns = [x.strip() for x in data.columns]
# Delete device column 
#data.pop('Device')
activity_col = data[['WOHT_Hom_Male_AVG']]
df_index = data.index
#print(activity_col)
#print(df_index)


# Need to add column with LD data, numeric_only = True
data_resample = activity_col.resample('1min').mean()


#print(data_resample.isnull().sum())
data_resample.fillna(0, inplace=True)
#data_resample.to_csv("testdvcreformat.csv")


L = 12
D = 12

schedule = np.concatenate([
    np.full(L, 300), 
    np.full(D, 0)])


repeat_sch = np.repeat([300, 0], 720)
mask = int(np.ceil(len(data_resample) / len(repeat_sch)))
data_resample['LD'] = np.tile(repeat_sch, mask)[:len(data_resample)]
#print(data_resample.columns)


#data_resample.loc[data_resample['WOHT_Hom_Male_AVG'] > 0, data_resample['WOHT_Hom_Male_AVG'] * 100, 0]

data_resample.loc[data_resample['WOHT_Hom_Male_AVG'] > 0, 'WOHT_Hom_Male_AVG'] *= 50
#print(data_resample.head())
#data_resample.to_csv("testdvcreformat.csv")


#cplt.plot_actogram(data_resample, showfig = True)
plot_activity_profile(data_resample, showfig = True)
