# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 12:17:41 2016

@author: dan
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import platform
import os



def bin_me(row):
    if row['pct_change']<=-0.05:
        return 'Loss'
    if row['pct_change']>-0.05 and row['Volume']<0.05:
        return 'Same'
    if row['pct_change']>=0.05:
        return "Gain"
        
def sort_hack(row):
    if row['Volume']<=-500:
        return 1
    if row['Volume']>-500 and row['Volume']<500:
        return 2
    if row['Volume']>=500:
        return 3
        
def volume_data(df,section=None):
    if section is not None:
        df=df.query(section)
    tmp_pvt = pd.pivot_table(df, values=['Volume'], index=['TripDate'], aggfunc=np.std)
    tmp_pvt = tmp_pvt.rename(columns={'Volume':'std_dev'})
    tmp_count = pd.pivot_table(df,values=['Volume'], index=['TripDate'], aggfunc='count')
    tmp_count = tmp_count.rename(columns={'Volume':'count'})
    tmp_pvt['std_error'] = tmp_pvt['std_dev']/np.sqrt(tmp_count['count'])
    yerr = tmp_pvt[['std_error']]
    del tmp_count, tmp_pvt
    tmp_pvt = pd.pivot_table(df, values=['Volume'], index=['TripDate'], aggfunc=np.average)
    tmp_pvt['y_err']=yerr
    return tmp_pvt

def area_data(df,section=None):
    if section is not None:
        df=df.query(section)
    tmp_pvt = pd.pivot_table(df, values=['Area_2D'], index=['TripDate'], aggfunc=np.std)
    tmp_pvt = tmp_pvt.rename(columns={'Area_2D':'std_dev'})
    tmp_count = pd.pivot_table(df,values=['Area_2D'], index=['TripDate'], aggfunc='count')
    tmp_count = tmp_count.rename(columns={'Area_2D':'count'})
    tmp_pvt['std_error'] = tmp_pvt['std_dev']/np.sqrt(tmp_count['count'])
    yerr = tmp_pvt[['std_error']]
    tmp_pvt = pd.pivot_table(df, values=['Area_2D'], index=['TripDate'], aggfunc=np.average)
    tmp_pvt['y_err']=yerr
    return tmp_pvt
    
def merge_area_vol(df,section=None):
    vol = volume_data(df,section)
    area = area_data(df,section)
    merged = vol.merge(area, left_index=True, right_index=True, how='left')
    return merged


def pct_change(row):
    try:
        vol_15 = float(row['Volume'])
        vol_90 = float(row['Volume_90'])
        change = (vol_15-vol_90)/vol_90
        return change
    except:
        return 0

def return_plot_series_med(df):
    temp = df
    temp['NormVol'] = temp['Volume']/temp['MaxVol']
    tmp_pvt = pd.pivot_table(temp, values=['NormVol'], index=['TripDate'], aggfunc=np.std)
    tmp_pvt = tmp_pvt.rename(columns={'NormVol':'std_dev'})
    tmp_count = pd.pivot_table(temp,values=['NormVol'], index=['TripDate'], aggfunc='count')
    tmp_count = tmp_count.rename(columns={'NormVol':'count'})
    tmp_pvt['std_error'] = tmp_pvt['std_dev']/np.sqrt(tmp_count['count'])
    tmp_pvt = tmp_pvt[['std_error']]

    
    table1 = df
    table1['NormVol']= table1['Volume']/table1['MaxVol']
    table1 = pd.pivot_table(table1, values=['NormVol'], index=['TripDate'], aggfunc=np.median)
    table1 = table1[['NormVol']]
    table1 = table1.merge(tmp_pvt, left_index=True, right_index=True, how='left')
    return table1

def return_plot_series_mean(df):
    temp = df
    temp['NormVol'] = temp['Volume']/temp['MaxVol']
    tmp_pvt = pd.pivot_table(temp, values=['NormVol'], index=['TripDate'], aggfunc=np.std)
    tmp_pvt = tmp_pvt.rename(columns={'NormVol':'std_dev'})
    tmp_count = pd.pivot_table(temp,values=['NormVol'], index=['TripDate'], aggfunc='count')
    tmp_count = tmp_count.rename(columns={'NormVol':'count'})
    tmp_pvt['std_error'] = tmp_pvt['std_dev']/np.sqrt(tmp_count['count'])
    tmp_pvt = tmp_pvt[['std_error']]    
    table1 = df
    table1['NormVol']= table1['Volume']/table1['MaxVol']
    table1 = pd.pivot_table(table1, values=['NormVol'], index=['TripDate'], aggfunc=np.mean)
    table1 = table1[['NormVol']]
    table1 = table1.merge(tmp_pvt, left_index=True, right_index=True, how='left')
    return table1
    
if __name__ =='__main__':
    if platform.system() == 'Darwin':
        sandbar_root = '/~/git_clones/sandbar-results-aggregation/Time_Series_Analysis/input'
        time_root = '/~/git_clones/sandbar-results-aggregation/Time_Series_Analysis'
        out_root = time_root + os.sep + 'Output'
    elif platform.system() == 'Windows':
        sandbar_root = r'C:\workspace\sandbar-results-aggregation\Time_Series_Analysis\input'
        time_root = r'C:\workspace\sandbar-results-aggregation\Time_Series_Analysis'
        out_root = time_root + os.sep + r'Output'
        
    
    lt_sites = {u'Sediment Deficit Sites': {0: u'003l', 1: u'008l', 2: u'016l', 3: u'022r', 6: u'030r', 7: u'032r', 11: u'043l', 13: u'044l_s', 16: u'047r', 17: u'050r_r', 18: u'050r_s', 19: u'051l', 24: u'065r_r', 25: u'065r_s', 26: u'081l', 27: u'087l', 28: u'091r', 29: u'093l', 30: u'104r', 31: u'119r', 32: u'122r', 33: u'123l', 34: u'137l', 35: u'139r', 37: u'145l', 38: u'172l', 39: u'183r', 40: u'194l', 41: u'202r_s', 42: u'213l', 43: u'220r', 44: u'225r'}}
    lu_sites = pd.DataFrame(lt_sites)
    
    
    #Read Data from file
    data_file = sandbar_root + os.sep + 'Merged_Sandbar_data.csv'
    data = pd.read_csv(data_file, sep =',')

    query_90 = (data.Time_Series == 'long')& (data.Site !='m006r')& (data.Site !='033l')& (data.Site !='068r')
    
    #Set Trip dates to pandas datetime
    data['TripDate'] = pd.to_datetime(data['TripDate'], format='%Y-%m-%d')
    
    mc_query = 'Segment == ["1_UMC","2_LMC"]'
    gc_query = 'Segment != ["1_UMC","2_LMC"]'
    
    subset = data[(data.Time_Series == 'long') & (data.Site !='m006r')& (data.Site !='033l') & (data.Site !='062r') & (data.Site !='068r') & (data.Site !='167l') & (data.SitePart == 'Eddy') & (data.Plane_Height != 'eddyminto8k')]   
    subset = subset[subset['Site'].str.len() == 4]
                    
    early = subset[subset['Period'] == 'Sediment_Deficit']
    mc_early = early.query(mc_query)
    gc_early = early.query(gc_query)
    mc_early = mc_early[mc_early['Site'].isin(set(lu_sites['Sediment Deficit Sites']))]
    gc_early = gc_early[gc_early['Site'].isin(set(lu_sites['Sediment Deficit Sites']))]
    
    subset1 = data[(data.Time_Series == 'long') & (data.Site !='m006r')& (data.Site !='033l') & (data.Site !='062r') & (data.Site !='068r') & (data.Site !='167l') & (data.SitePart == 'Eddy') & (data.Plane_Height != 'eddyminto8k')]   
    subset1 = subset1[subset1['Site'].str.len() == 4]
    
    late = subset1[subset1['Period'] == 'Sediment_Enrichment']
    mc_late = late.query(mc_query)
    gc_late = late.query(gc_query)
    
    gc_early_plot_mean = return_plot_series_mean(gc_early)
    mc_early_plot_mean = return_plot_series_mean(mc_early)
    
    mc_late_plot_mean = return_plot_series_mean(mc_late)
    gc_late_plot_mean = return_plot_series_mean(gc_late)
    
    
    mc_early_total = pd.pivot_table(mc_early, index=['TripDate'], values=['Volume','Errors'],aggfunc=np.sum)
    gc_early_total = pd.pivot_table(gc_early, index=['TripDate'], values=['Volume','Errors'],aggfunc=np.sum)
    
    mc_late_total = pd.pivot_table(mc_late, index=['TripDate'], values=['Volume','Errors'],aggfunc=np.sum)
    gc_late_total = pd.pivot_table(gc_late, index=['TripDate'], values=['Volume','Errors'],aggfunc=np.sum)
    
    
    fig, (ax) = plt.subplots(nrows=1)
    gc_early_plot_mean.plot(y = 'NormVol', yerr='std_error', ax = ax, label = 'Grand Canyon: N=17',linestyle='-',color='blue',marker='o' )
    mc_early_plot_mean.plot(y = 'NormVol', yerr='std_error',ax = ax, label = 'Marble Canyon: N=9',linestyle='--',color='green',marker='x')
    ax.set_xlim(pd.Timestamp('1990-01-01'), pd.Timestamp('2004-01-01'))
    ax.set_ylabel('Normalized Sandbar Volume [m$^3$/m$^3$]')
    ax.set_xlabel('Date')
    plt.tight_layout()
    plt.savefig(r"C:\workspace\Time_Series\Output\sediment_deficit_Norm_Vol_AMWG.png",dpi=600)
    
    fig, (ax) = plt.subplots(nrows=1)
    gc_early_total.plot(y = 'Volume', yerr='Errors', ax = ax, label = 'Grand Canyon: N=17',linestyle='-',color='blue',marker='o' )
    mc_early_total.plot(y = 'Volume', yerr='Errors',ax = ax, label = 'Marble Canyon: N=9',linestyle='--',color='green',marker='x')
    ax.set_xlim(pd.Timestamp('1990-01-01'), pd.Timestamp('2004-01-01'))
    ax.set_ylabel('Total Sandbar Volume [m$^3$]')
    ax.set_xlabel('Date')
    plt.tight_layout()
    plt.savefig(r"C:\workspace\Time_Series\Output\sediment_deficit_total_Vol_AMWG.png",dpi=600)
    
    fig, (ax1) = plt.subplots(nrows=1)
    gc_late_plot_mean.plot(y = 'NormVol', yerr='std_error', ax = ax1, label = 'Grand Canyon: N=22',linestyle='-',color='blue' ,marker='o')
    mc_late_plot_mean.plot(y = 'NormVol', yerr='std_error',ax = ax1, label = 'Marble Canyon: N=19',linestyle='--',color='green',marker='x')
    ax1.set_xlim(pd.Timestamp('2004-01-01'), pd.Timestamp('2017-01-01'))
    ax1.set_ylabel('Normalized Sandbar Volume [m$^3$/m$^3$]')
    ax1.set_xlabel('Date')
    ax1.set_ylim(0.2,0.7)
    plt.tight_layout()
    plt.savefig(r"C:\workspace\Time_Series\Output\sediment_enrichment_Norm_Vol_AMWG.png",dpi=600)
    
    fig, (ax) = plt.subplots(nrows=1)
    gc_late_total.plot(y = 'Volume', yerr='Errors', ax = ax, label = 'Grand Canyon: N=22',linestyle='-',color='blue',marker='o' )
    mc_late_total.plot(y = 'Volume', yerr='Errors',ax = ax, label = 'Marble Canyon: N=19',linestyle='--',color='green',marker='x')
    ax.set_xlim(pd.Timestamp('2004-01-01'), pd.Timestamp('2017-01-01'))
    ax.set_ylabel('Total Sandbar Volume [m$^3$]')
    ax.set_xlabel('Date')
    plt.tight_layout()
    plt.savefig(r"C:\workspace\Time_Series\Output\sediment_enrichment_total_Vol_AMWG.png",dpi=600)






 
 
 
 
 