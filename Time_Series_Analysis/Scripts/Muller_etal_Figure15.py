# -*- coding: utf-8 -*-
"""
Created on Sun Sep 03 16:37:41 2017

@author: dan
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import platform
import os
from matplotlib import dates

def std_err_calc(df,metric):
        mc_std = pd.pivot_table(df, values=[metric], index=['TripDate'], aggfunc=np.std)
        mc_std = mc_std.rename(columns={metric:'std_dev'})
        mc_count = pd.pivot_table(df, values=[metric], index=['TripDate'], aggfunc='count')
        mc_count = mc_count.rename(columns={metric:'count'})    
        return mc_std.std_dev/np.sqrt(mc_count['count'])
    
    

if __name__ =='__main__':
    
    if platform.system() == 'Darwin':
        sandbar_root = '/~/git_clones/sandbar-results-aggregation/Time_Series_Analysis/input'
        time_root = '/~/git_clones/sandbar-results-aggregation/Time_Series_Analysis'
        out_root = time_root + os.sep + 'Output'
    elif platform.system() == 'Windows':
        sandbar_root = r'C:\workspace\sandbar-results-aggregation\Time_Series_Analysis\input'
        time_root = r'C:\workspace\sandbar-results-aggregation\Time_Series_Analysis'
        out_root = time_root + os.sep + r'Output'
        
    #designate groups       
    g_1a = np.array(['145l','022r','213l','084r','030r','081l','137l','119r','122r'])
    g_1b = np.array(['123l','172l','041r','044l','183r','220r','050r','065r','047r','009l'])  #'009l' dropped because it was added in 2008,-'045l' dropped 045L because sep and reatt bar wasnt surveyed each time
    g_1c = np.array(['194l','068r','051l','055r','070r'])
    g_2 = np.array(['008l','024l','029l','032r','056r'])# ,'167l' removed because it is a technical outlier
    g_3 = np.array(['043l','087l','093l','139r','225r','104r'])
    g_4 = np.array(['016l','033l','035l','062r','091r','202r'])  
    
     
    
    
    #pre allocate figure
    fig, ((ax_0,ax_1,ax_2),(ax1_0,ax1_1,ax1_2),(ax2_0,ax2_1,ax2_2)) = plt.subplots(figsize=(10,7),nrows=3,ncols=3,sharey=True)
    
    
    axes=[[ax_0,ax1_0,ax2_0],
          [ax_1,ax1_1,ax2_1],
          [ax_2,ax1_2,ax2_2]]
    #Read Data File
    data_file = sandbar_root + os.sep + 'Merged_Sandbar_data.csv'
    data = pd.read_csv(data_file, sep =',')
    
    data['TripDate'] = pd.to_datetime(data['TripDate'], format='%Y-%m-%d')
    data = data[(data.Time_Series == 'long') & (data.SitePart == 'Eddy')] 
    ls = ['','','']
    m=['o','o','o']
    n=0
    r=['g_1a','g_1b','g_1c']
    m_size=4
    c_size=2
    for group1 in [g_1a,g_1b,g_1c,g_2,g_3,g_4][0:3]:
        a = axes[n]
        name = r[n] + ': N=' + str(len(group1))
        #Total High Elevation Zone
        subset = data[data['Site'].isin(group1)]
        subset = subset[subset.Plane_Height != 'eddyminto8k']        
        date_fz = subset[(subset['Volume']>0) & (subset['Plane_Height'] == 'eddy8kto25k') ].SurveyDate.unique()
        date_he = subset[(subset['Volume']>0) & (subset['Plane_Height'] == 'eddyabove25k') ].SurveyDate.unique()
        common_dates = np.intersect1d(date_fz,date_he)
        subset = subset[subset['SurveyDate'].isin(common_dates)]
        subset =  pd.pivot_table(subset,index=['TripDate','SitePart','Site'],values=['Area_2D','Area_3D','Volume','Errors','MaxVol','Max_Area'],aggfunc=np.sum).reset_index()
        subset.loc[:,'Norm_Area']=subset.loc[:,'Area_2D']/subset.loc[:,'Max_Area']
        subset.loc[:,'Norm_Vol'] = subset.loc[:,'Volume']/subset.loc[:,'MaxVol']
        tmp = pd.pivot_table(subset, index=['TripDate','SitePart'], values=['Norm_Vol','Norm_Area'],aggfunc=np.average).reset_index()
        tmp[tmp['SitePart'] == 'Eddy'].plot(linestyle=ls[n],marker=m[n], x='TripDate',y='Norm_Vol',
            yerr=std_err_calc(subset,'Norm_Vol'), ax=a[0],label=name,sharey=ax_0,ms=m_size,c='k',capsize=c_size,zorder=10)
        
        #controlled flood zone
        subset = data[data['Site'].isin(group1)]
        subset.loc[:,'Norm_Area']=subset.loc[:,'Area_2D']/subset.loc[:,'Max_Area']
        subset.loc[:,'Norm_Vol'] = subset.loc[:,'Volume']/subset.loc[:,'MaxVol']
        tmp = pd.pivot_table(subset, index=['TripDate','Plane_Height'], values=['Norm_Vol','Area_2D'],aggfunc=np.average).reset_index()

        tmp[(tmp['Plane_Height'] == 'eddy8kto25k') & (tmp['Norm_Vol'] >0)].plot(linestyle=ls[n],marker=m[n], x='TripDate',y='Norm_Vol',
            yerr=std_err_calc(subset[(subset['Plane_Height'] == 'eddy8kto25k') & (subset['Norm_Vol'] >0)],'Norm_Vol'), 
            ax=a[2],label=name,sharey=ax_1,ms=m_size,c='k',capsize=c_size,zorder=10)
        
        
        #High Elevaton
        tmp[(tmp['Plane_Height'] == 'eddyabove25k') & (tmp['Norm_Vol'] >0)].plot(linestyle=ls[n],marker=m[n], x='TripDate',y='Norm_Vol', 
            yerr=std_err_calc(subset[(subset['Plane_Height'] == 'eddyabove25k') & (subset['Norm_Vol'] >0)],'Norm_Vol'), 
            ax=a[1],label=name,sharey=ax_2,ms=m_size,c='k',capsize=c_size,zorder=10)
        
        n+=1
    
    [i.set_ylim(0,1) for i in fig.axes]
    [i.set_xlim(pd.datetime(1990,01,01), pd.datetime(2018,01,01)) for i in fig.axes]
    [i.legend_.remove() for i in fig.axes]
    [i.set_xlabel('') for i in fig.axes]
    
    hfe_dates = [pd.datetime(1996,4,1),pd.datetime(2004,11,22),pd.datetime(2008,3,8),pd.datetime(2012,11,20),pd.datetime(2013,11,11),pd.datetime(2014,11,11)]
    other_flow = [pd.datetime(1997,11,1),pd.datetime(2000,4,1),pd.datetime(2000,11,1)]
    for i in fig.axes:
        for d in hfe_dates:
            i.axvline(d,color='grey',linestyle='-',zorder=1)
        for d in other_flow:
            i.axvline(d,color='grey',linestyle='--',zorder=1)
    ax_1.set_title('Total High Elevation Zone: >227 m$^3$/s')
    ax1_1.set_title('Controlled Flood Zone: >708 m$^3$/s')
    ax2_1.set_title('Fluctuating Flow Zone: 227-708 m$^3$/s')
    
    ax_0.set_ylabel('Normalized Volume')
    ax1_0.set_ylabel('Normalized Volume')
    ax2_0.set_ylabel('Normalized Volume')
    years = dates.YearLocator(10,month=1,day=1)
    years1=dates.YearLocator(2,month=1,day=1)
    dfmt = dates.DateFormatter('%Y')
    dfmt1 = dates.DateFormatter('%y')
    
    [i.xaxis.set_major_locator(years) for i in fig.axes]
    [i.xaxis.set_minor_locator(years1) for i in fig.axes]
    [i.xaxis.set_major_formatter(dfmt) for i in fig.axes]
    [i.xaxis.set_minor_formatter(dfmt1) for i in fig.axes]
    
    [i.get_xaxis().set_tick_params(which='major', pad=15) for i in fig.axes]
    
    for t in fig.axes:
        for tick in t.xaxis.get_major_ticks():
            tick.label1.set_horizontalalignment('center')
        for label in t.get_xmajorticklabels() :
            label.set_rotation(0)
            label.set_weight('bold')
        for label in t.xaxis.get_minorticklabels():
            label.set_fontsize('small')
        for label in t.xaxis.get_minorticklabels()[::5]:
            label.set_visible(False)
    fig.tight_layout()
    fig.subplots_adjust(wspace=0.05)
    plt.savefig(out_root + os.sep + 'Muller_Figure15__all_data_group1.png')

####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################

    #pre allocate figure
    fig, ((ax_0,ax_1,ax_2),(ax1_0,ax1_1,ax1_2),(ax2_0,ax2_1,ax2_2)) = plt.subplots(figsize=(10,7),nrows=3,ncols=3,sharey=True)
    
    
    axes=[[ax_0,ax1_0,ax2_0],
          [ax_1,ax1_1,ax2_1],
          [ax_2,ax1_2,ax2_2]]
    #Read Data File
    data_file = sandbar_root + os.sep + 'Merged_Sandbar_data.csv'
    data = pd.read_csv(data_file, sep =',')
    
    data['TripDate'] = pd.to_datetime(data['TripDate'], format='%Y-%m-%d')
    data = data[(data.Time_Series == 'long') & (data.SitePart == 'Eddy')] 

    n=0
    r=['g_2','g_3','g_4']

    for group1 in [g_1a,g_1b,g_1c,g_2,g_3,g_4][3:]:
        a = axes[n]
        name = r[n] + ': N=' + str(len(group1))
        #Total High Elevation Zone
        subset = data[data['Site'].isin(group1)]
        subset = subset[subset.Plane_Height != 'eddyminto8k']        
        date_fz = subset[(subset['Volume']>0) & (subset['Plane_Height'] == 'eddy8kto25k') ].SurveyDate.unique()
        date_he = subset[(subset['Volume']>0) & (subset['Plane_Height'] == 'eddyabove25k') ].SurveyDate.unique()
        common_dates = np.intersect1d(date_fz,date_he)
        subset = subset[subset['SurveyDate'].isin(common_dates)]
        subset =  pd.pivot_table(subset,index=['TripDate','SitePart','Site'],values=['Area_2D','Area_3D','Volume','Errors','MaxVol','Max_Area'],aggfunc=np.sum).reset_index()
        subset.loc[:,'Norm_Area']=subset.loc[:,'Area_2D']/subset.loc[:,'Max_Area']
        subset.loc[:,'Norm_Vol'] = subset.loc[:,'Volume']/subset.loc[:,'MaxVol']
        tmp = pd.pivot_table(subset, index=['TripDate','SitePart'], values=['Norm_Vol','Norm_Area'],aggfunc=np.average).reset_index()
        tmp[tmp['SitePart'] == 'Eddy'].plot(linestyle=ls[n],marker=m[n], x='TripDate',y='Norm_Vol',
            yerr=std_err_calc(subset,'Norm_Vol'), ax=a[0],label=name,sharey=ax_0,ms=m_size,c='k',capsize=c_size,zorder=10)
        
        #controlled flood zone
        subset = data[data['Site'].isin(group1)]
        subset.loc[:,'Norm_Area']=subset.loc[:,'Area_2D']/subset.loc[:,'Max_Area']
        subset.loc[:,'Norm_Vol'] = subset.loc[:,'Volume']/subset.loc[:,'MaxVol']
        tmp = pd.pivot_table(subset, index=['TripDate','Plane_Height'], values=['Norm_Vol','Area_2D'],aggfunc=np.average).reset_index()

        tmp[(tmp['Plane_Height'] == 'eddy8kto25k') & (tmp['Norm_Vol'] >0)].plot(linestyle=ls[n],marker=m[n], x='TripDate',y='Norm_Vol',
            yerr=std_err_calc(subset[(subset['Plane_Height'] == 'eddy8kto25k') & (subset['Norm_Vol'] >0)],'Norm_Vol'), 
            ax=a[2],label=name,sharey=ax_1,ms=m_size,c='k',capsize=c_size,zorder=10)
        
        
        #High Elevaton
        tmp[(tmp['Plane_Height'] == 'eddyabove25k') & (tmp['Norm_Vol'] >0)].plot(linestyle=ls[n],marker=m[n], x='TripDate',y='Norm_Vol', 
            yerr=std_err_calc(subset[(subset['Plane_Height'] == 'eddyabove25k') & (subset['Norm_Vol'] >0)],'Norm_Vol'), 
            ax=a[1],label=name,sharey=ax_2,ms=m_size,c='k',capsize=c_size,zorder=10)
        
        n+=1
    
    [i.set_ylim(0,1) for i in fig.axes]
    [i.set_xlim(pd.datetime(1990,01,01), pd.datetime(2018,01,01)) for i in fig.axes]
    [i.legend_.remove() for i in fig.axes]
    [i.set_xlabel('') for i in fig.axes]
    
    hfe_dates = [pd.datetime(1996,4,1),pd.datetime(2004,11,22),pd.datetime(2008,3,8),pd.datetime(2012,11,20),pd.datetime(2013,11,11),pd.datetime(2014,11,11)]
    other_flow = [pd.datetime(1997,11,1),pd.datetime(2000,4,1),pd.datetime(2000,11,1)]
    for i in fig.axes:
        for d in hfe_dates:
            i.axvline(d,color='grey',linestyle='-',zorder=1)
        for d in other_flow:
            i.axvline(d,color='grey',linestyle='--',zorder=1)
    ax_1.set_title('Total High Elevation Zone: >227 m$^3$/s')
    ax1_1.set_title('Controlled Flood Zone: >708 m$^3$/s')
    ax2_1.set_title('Fluctuating Flow Zone: 227-708 m$^3$/s')
    
    ax_0.set_ylabel('Normalized Volume')
    ax1_0.set_ylabel('Normalized Volume')
    ax2_0.set_ylabel('Normalized Volume')
    years = dates.YearLocator(10,month=1,day=1)
    years1=dates.YearLocator(2,month=1,day=1)
    dfmt = dates.DateFormatter('%Y')
    dfmt1 = dates.DateFormatter('%y')
    
    [i.xaxis.set_major_locator(years) for i in fig.axes]
    [i.xaxis.set_minor_locator(years1) for i in fig.axes]
    [i.xaxis.set_major_formatter(dfmt) for i in fig.axes]
    [i.xaxis.set_minor_formatter(dfmt1) for i in fig.axes]
    
    [i.get_xaxis().set_tick_params(which='major', pad=15) for i in fig.axes]
    
    for t in fig.axes:
        for tick in t.xaxis.get_major_ticks():
            tick.label1.set_horizontalalignment('center')
        for label in t.get_xmajorticklabels() :
            label.set_rotation(0)
            label.set_weight('bold')
        for label in t.xaxis.get_minorticklabels():
            label.set_fontsize('small')
        for label in t.xaxis.get_minorticklabels()[::5]:
            label.set_visible(False)
    fig.tight_layout()
    fig.subplots_adjust(wspace=0.05)
    plt.savefig(out_root + os.sep + 'Muller_Figure15_all_data_group2.png')
    