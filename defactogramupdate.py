import re
import pdb
import pandas as pd
import numpy as np
import matplotlib.gridspec as gs
from matplotlib.transforms import Bbox
import matplotlib.pyplot as plt
import circaPy.activity as act
import circaPy.preprocessing as prep
import circaPy.periodogram as period




data = pd.read_csv(
    '/Users/ayobamifawole/Desktop/Home Cage Data Analysis Python/Test Data/LTC_7b_2025-04-25T_modified.csv',
   index_col = 'Time', 
   parse_dates = True)


# Remove whitespace from all headers
data.columns = [x.strip() for x in data.columns]
# Delete device column 
data.pop('Device')

#print(data.head())

data.fillna(0, inplace=True)
# set 10s index frequency
data_resample = data.resample('10s').mean()
#Check any missing PIR data ~ will check LDR too
#print(data.isnull().sum())
data_resample.fillna(0, inplace=True)




@prep.validate_input
@prep.invert_light_values
@prep.plot_kwarg_decorator
def plot_actogram(
    data,
    subject_no=0,
    lights_on = 0,
    light_col=-1,
    ylim=[0, 120],
    fig=False,
    subplot=False,
    ldralpha=0.5,
    start_day=0,
    day_label_size=5,
    linewidth=0.5,
    extra_day_limit="6h",
    **kwargs,
):
    """
    Plot an double plotted actogram of activity data over several days
    with background shading set by the lights

    Parameters:
    ----------
    data : (pd.DataFrame)
        time-indexed pandas dataframe with activity values in
        columns for each subject and one column for the light levels.
        WRONG - currently expecting list of dataframes, one for each animal
        and single column for each day
    subject_no : int
        which column number to plot, defaults to 0
    lights_on : int, optional
        Light onset will be set at ZT0
        If parameter is not included in the funtion call, the plot will generate set to CT time
    light_col : int
        which columns contains light information, defaults to -1
    ylim : list of two ints
        set the minimum and maximum values to plot
    fig : matplotlib figure object
        Figure to create plot on, if not passed defaults to false and
        new figure is passed
    subplot : matplotlib subplotspec object
        Subplotspec from larger figure on which to draw actogram.
        Must be created from gridspec
        If not passed
        defaults to False, which requires a fig object to be provided
    ldralpha : float
        Set the alpha level for how opaque to have the light shading,
        defaults to 0.5
    startday : int
        sets which day to start as day 0 in plot, defaults to 0
    day_label_size : int
        sets size of labels on bottom x axis, defaults to 5
    extra_day_limit : str
        sets the threshold at which an extra day of values is added to start
        and end of the actogram. In Timedelta string values. Default is "6H"

    Returns
    -------
    matplotlib.pyplot.figure
        instance containing overall figure
    matplotlib.pyplot.subplot
        the final subplot so can manipulate for xaxis
    dict
        dict containing plotting kwargs
    """
    # grab line plot constant
    if "linewidth" in kwargs:
        linewidth = kwargs["linewidth"]


    # Set ZT0 for light onset
    if lights_on > 0:
        data = data.shift(-lights_on, freq = 'h')   
        ### considerations
            # this only considers the 1st light onset for the df
            # may need to have a filter for what days of data you want plotted
            # assumes you're "-" time, idk what context someone would need to + but this should be added i suppose
    
    
    # check if data is empty
    if data.empty:
        raise ValueError("Input Dataframe is empty. Cannot plot actogram")

    # select the correct data to plot for activity and light
    col_data = data.columns[subject_no]
    ldr_col = data.columns[light_col]
    data_plot = data.loc[:, col_data].copy()
    data_light = data.loc[:, ldr_col].copy()

    # add entire day of 0s at start and end by extending index
    # grab values from current index
    freq = pd.infer_freq(data_plot.index)
    start = data_plot.index.min()
    end = data_plot.index.max()

    # check frequency works
    try:
        pd.Timedelta(freq)
    except BaseException:
        freq = pd.Timedelta(f"1{freq}")

    # Extend the range by 1 day but make sure lines up with original index
    extended_start = data_plot.index.min().normalize()
    extended_end = (
        data_plot.index.max().normalize()
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

    # Check how close data is to new start, and add extra day if so
    if abs(extended_start - data_plot.index.min()) <= pd.Timedelta(extra_day_limit):
        extended_start = extended_start - pd.Timedelta(days=1)
    if abs(extended_end - data_plot.index.max()) <= pd.Timedelta(extra_day_limit):
        extended_end = extended_end + pd.Timedelta(days=1)

    # create new index and set data to it
    extended_index = pd.date_range(start=extended_start, end=extended_end, freq=freq)
    data_plot = data_plot.reindex(extended_index, fill_value=-100)

    # select just the days
    days = data_plot.index.normalize().unique()

    # set all 0 values to be very low so not showing on y index starting at 0
    for mask in data_plot, data_light:
        mask[mask == 0] = -100

    # Create figure and subplot for every day
    # create a new figure if not passed one when called
    if not fig:
        fig, ax = plt.subplots(nrows=(len(days) - 1))
        fig.subplots_adjust(hspace=0)

    # add subplots to figure if passed when called
    else:
        # remove ticks so don't draw over when we add later
        subplot.set(yticks=[], xticks=[])

        # draw subplots for each day on the subplot given
        subplot_spec = subplot.get_subplotspec()
        subplot_grid = gs.GridSpecFromSubplotSpec(
            nrows=(len(days) - 1),
            ncols=1,
            subplot_spec=subplot_spec,
            wspace=0,
            hspace=0,
        )
        ax = []
        for grid in subplot_grid:
            sub_ax = plt.Subplot(fig, grid)
            fig.add_subplot(sub_ax)
            ax.append(sub_ax)

    # select each day to then plot on separate axis
    # plot two days on each row
    for day_label, axis in zip(days, ax):
        # get two days of data to plot
        curr_day = str(day_label.date())
        next_day = str(day_label.date() + pd.Timedelta("1d"))
        curr_data = data_plot.loc[curr_day:next_day]
        tcurr_data = data_plot.loc[curr_day]
        curr_data_light = data_light.loc[curr_day:next_day]

        ### fill activity on/off scripts
        mean1 = 3
        mean2 = 24
        m1_avg = tcurr_data.rolling(window = f'{mean1}h', min_periods = mean1).mean()
        m2_avg = tcurr_data.rolling(window = f'{mean2}h', min_periods = mean2).mean()

        m_dif = m1_avg - m2_avg

        pos_mask = (m_dif > 0) & (m_dif.shift(1) < 0)

        # create masked data for fill between to avoid horizontal lines
        fill_data = curr_data.where(curr_data > 0)
        fill_ldr = curr_data_light.where(curr_data_light > 0)

        # plot the data and light_col
        axis.fill_between(fill_ldr.index, fill_ldr, alpha=ldralpha, facecolor="grey")
        axis.plot(curr_data, linewidth=linewidth)
        axis.scatter(curr_data.index, pos_mask)
        axis.fill_between(fill_data.index, fill_data)

        # need to hide all the axis to make visible
        axis.set(
            xticks=[],
            xlim=[curr_data.index[0], curr_data.index[-1]],
            yticks=[],
            ylim=ylim,
        )
        spines = ["left", "right", "top", "bottom"]
        for pos in spines:
            axis.spines[pos].set_visible(False)

    # create the y labels for every 10th row
    day_markers = np.arange(0, len(days), 10)
    day_markers = day_markers + start_day
    for axis, day in zip(ax[::10], day_markers):
        axis.set_ylabel(
            day, rotation=0, va="center", ha="right", fontsize=day_label_size
        )

    # create defaults dict
    params_dict = {
        "xlabel": "Time",
        "ylabel": "Days",
        "interval": 6,
        "title": "Double Plotted Actogram",
        "timeaxis": True,
        "subplot": subplot,
    }

    '''
    implement the activity on/off parameter to compare across activity patterns

    how is the best way to do this, after all teh actogram script bc the act. on/off transforms the data
        unless new variables are made then it doesnt matter where in the code it is @
    
    dont necessarily want to add in the entire raw script for the def on/off function
        can it be made into a decorator to apply to other functions?
        it should be lwk, if these quantifications need to be used for other circadian measures, this


    '''

    # put axis as a controllable parameter
    if "timeaxis" in kwargs:
        params_dict["timeaxis"] = kwargs["timeaxis"]

    return fig, ax, params_dict



# Plot the actogram
plot_actogram(data_resample, showfig = True)

'''
Trying to figure out how to put activity markers over cp actogram

Need to pull marker mask from activityon/off def function
    call 1st and last row for each day?
    make that its own stand alone table as on/off output
    see if you can get that plotted alone on def function with dif plotted

Insert the script to the actogram def function 
    make parameter for applying markers
    could apply all to see bouts n whatnot
    but can set the begining and end of dark period as filter
'''


