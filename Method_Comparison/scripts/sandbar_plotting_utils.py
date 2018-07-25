# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 17:18:14 2018

@author: dan
"""
import matplotlib.pyplot as plt
from matplotlib import dates


def format_xaxis(fig):
    '''
    Function to format x-axis of a Time series plot spanning mutiple decades
    Input: Matplotlib figure object
    Notes: 
        Assumes empty subplots will be at the bottom right of figure,
        typically a result of plotting large number of subplots
    '''
    
     dead = len(fig.axes) -sum([ax.has_data() for ax in fig.axes])
     years = dates.YearLocator(10,month=1,day=1)
     years1=dates.YearLocator(2,month=1,day=1)
     dfmt = dates.DateFormatter('%Y')
     dfmt1 = dates.DateFormatter('%y')
    
     [i.xaxis.set_major_locator(years) for i in fig.axes[:dead]]
     [i.xaxis.set_minor_locator(years1) for i in fig.axes[:dead]]
     [i.xaxis.set_major_formatter(dfmt) for i in fig.axes[:dead]]
     [i.xaxis.set_minor_formatter(dfmt1) for i in fig.axes[:dead]]
     [i.get_xaxis().set_tick_params(which='major', pad=15) for i in fig.axes[:dead]]
    
     for t in fig.axes[:-2]:
         for tick in t.xaxis.get_major_ticks():
             tick.label1.set_horizontalalignment('center')
         for label in t.get_xmajorticklabels() :
             label.set_rotation(0)
             label.set_weight('bold')
         for label in t.xaxis.get_minorticklabels():
             label.set_fontsize('small')
         for label in t.xaxis.get_minorticklabels()[::5]:
             label.set_visible(False)