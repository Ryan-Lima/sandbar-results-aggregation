#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 11:07:11 2016

@author: danielhamill
"""

import pandas as pd
import platform
import numpy as np
import matplotlib.pyplot as plt
import pytablewriter
from matplotlib import dates
import os

def markdown_df(df):
    writer = pytablewriter.MarkdownTableWriter()
    writer.table_name = "example_table"
    writer.header_list = list(df.columns.values)
    writer.value_matrix = df.values.tolist()
    writer.write_table()
    
    
def query_df(df):
    '''
    Functon to subset data dataframe to Marble Canyon Sediment Enricnment Period
    '''
    tmp = df
    mc_query = 'Segment == ["1_UMC","2_LMC"]'
    tmp = tmp.query(mc_query)
    tmp['TripDate'] = pd.to_datetime(tmp['TripDate'], format='%Y-%m-%d')
    tmp = tmp[tmp['TripDate'] >= '2002-01-01']
    tmp = tmp[(tmp['Time_Series']== 'long') & (tmp['SitePart'] == 'Eddy')]
    tmp = tmp[tmp['Plane_Height'] != 'eddyminto8k']
    return tmp

def vol_norm_data(df,section=None):
    if section is not None:
        df=df.query(section)
    df = pd.pivot_table(df,index=['Site','SurveyDate','SitePart','TripDate','SiteRange','Segment','Bar_type','Time_Series','Period'],values=['Area_2D','Area_3D','Volume','Errors','MaxVol','Max_Area'],aggfunc=np.sum).reset_index()
    df['Norm_Vol'] = df['Volume']/df['MaxVol']
    tmp_pvt = pd.pivot_table(df, values=['Norm_Vol'], index=['TripDate'], aggfunc=np.std)
    tmp_pvt = tmp_pvt.rename(columns={'Norm_Vol':'std_dev'})
    tmp_count = pd.pivot_table(df,values=['Norm_Vol'], index=['TripDate'], aggfunc='count')
    tmp_count = tmp_count.rename(columns={'Norm_Vol':'count'})
    tmp_pvt['std_error'] = tmp_pvt['std_dev']/np.sqrt(tmp_count['count'])
    yerr = tmp_pvt[['std_error']]
    del tmp_count, tmp_pvt
    tmp_pvt = pd.pivot_table(df, values=['Norm_Vol'], index=['TripDate'], aggfunc=np.average)
    tmp_2 = pd.pivot_table(df, values=['Norm_Vol'], index=['TripDate'], aggfunc=[len,np.mean,np.std,np.min,np.max])
    
    tmp_pvt['y_err']=yerr
    return tmp_pvt, tmp_2
    
def pivot_df(df):
    lt_pvt = pd.pivot_table(df, values=['Volume','MaxVol','Area_2D','Max_Area'],index=['TripDate'],aggfunc=np.sum)
    lt_pvt['Norm_Vol'] = lt_pvt['Volume']/lt_pvt['MaxVol']
    lt_pvt['Norm_Error'] = lt_pvt['Area_2D']/lt_pvt['Max_Area']
    lt_pvt = lt_pvt[['Norm_Vol','Norm_Error']]
    return lt_pvt
    


def change_finder(extra_sites,long_term, all_sites):
    '''
    Function to calculate % difference between long term site time series 
    and bootstrapped all sties time series
    '''
    for n in xrange(len(extra_sites)):
        
        #subset all sites to drop one value
        drop_site = extra_sites.iloc[n][0]
        sites2test =all_sites[all_sites.Site != drop_site]
    
        #Find normal Volumes 
        long_t = pivot_df(long_term)
        all_s = pivot_df(sites2test)
        date_influence = (all_s['Norm_Vol'] - long_t['Norm_Vol'])/(all_s['Norm_Vol'])
        date_influence = date_influence.rename('Pct_Change')
        long_t= pd.pivot_table(long_t.reset_index(), index=['TripDate'], values=['Norm_Vol'])
        all_s = pd.pivot_table(all_s.reset_index(), index=['TripDate'], values=['Norm_Vol'])
        
        if n == 0:
            in_df=None
            in_df2 = None
            df_back, df2_back = merge_df(long_t,all_s,drop_site,in_df,date_influence,in_df2)
        else:
            df_back, df2_back = merge_df(long_t,all_s,drop_site,df_back,date_influence,df2_back)
        
    return df_back, df2_back
        
def merge_df(long_t,all_s, drop_site,in_df,date_influence,in_df2):
    if in_df is None:
        vol_diff = (-long_t['Norm_Vol'].sum(axis=0)+all_s['Norm_Vol'].sum(axis=0))/(all_s['Norm_Vol'].sum(axis=0))
        out_df = pd.DataFrame(data=[vol_diff], columns=['Vol_Change'],index=[drop_site])
        date_influence_out = pd.DataFrame({'Pct_Change':date_influence, 'Site':drop_site})
        return out_df, date_influence_out
    elif in_df is not None:
        vol_diff = (-long_t['Norm_Vol'].sum(axis=0)+all_s['Norm_Vol'].sum(axis=0))/(all_s['Norm_Vol'].sum(axis=0))
        out_df = pd.concat([in_df,pd.DataFrame(data=[vol_diff], columns=['Vol_Change'],index=[drop_site])])
        date_influence_out = pd.concat([in_df2,pd.DataFrame({'Pct_Change':date_influence, 'Site':drop_site})])
        return out_df, date_influence_out

def add_vlines(fig):
    hfe_dates = [pd.datetime(1996,4,1),pd.datetime(2004,11,22),pd.datetime(2008,3,8),pd.datetime(2012,11,20),pd.datetime(2013,11,11),pd.datetime(2014,11,11)]
    for i in fig.axes:
        
        for d in hfe_dates:
            i.axvline(d,color='k',linestyle='-',zorder=1)
            
    
    
def format_xaxis(fig):
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
             
             
if __name__ == '__main__':
    if platform.system() == 'Darwin':
        sandbar_root = '/~/git_clones/sandbar-results-aggregation/Time_Series_Analysis/input'
        time_root = '/~/git_clones/sandbar-results-aggregation/Time_Series_Analysis'
        out_root = time_root + os.sep + 'Output'
    elif platform.system() == 'Windows':
        sandbar_root = r'C:\workspace\sandbar-results-aggregation\Time_Series_Analysis\input'
        time_root = r'C:\workspace\sandbar-results-aggregation\Time_Series_Analysis'
        out_root = time_root + os.sep + r'Output'
        
    
    lt_sitecode = ['003l','008l','016l','022r','030r','032r','043l', '044l',  '047r', '050r',   '051l']
    new_sitecode =['024l','029l','033l','035l',  '041r', '055r','056r']
    #Load Database    
    db_file = sandbar_root + os.sep + 'Merged_Sandbar_data.csv'
    data = pd.read_csv(db_file,sep=',')    
    
    
    #Subset long term monitoring sites
    long_term = data[data['Site'].isin(np.array(lt_sitecode))]
    all_sites1 = data[data['Site'].isin(np.array(lt_sitecode+new_sitecode))]
    
    #Get data for plotting
    long_term = query_df(long_term)
    all_sites = query_df(all_sites1)

    
    #Data to plot                 
    long_term_plt,long_term_tbl = vol_norm_data(long_term)
    all_sites_plt,all_sites_tbl = vol_norm_data(all_sites)
    
    label_mc = 'Mable Canyon: N=' + str(len(long_term['Site'].unique()))
    label_mc1 ='Marble Canyon: N=' + str(len(all_sites['Site'].unique()))
    
    fig,ax = plt.subplots(figsize=(7.5,3.33))
    long_term_plt.plot(y = 'Norm_Vol', yerr='y_err',ax = ax, label = label_mc, color='blue',marker='o')
    all_sites_plt.plot(y = 'Norm_Vol', yerr='y_err',ax = ax, label = label_mc1, color='green',linestyle='--',marker='x')
    ax.set_ylabel('Normalized Sandbar Volume')
    ax.set_xlabel('Date')
    ax.set_xlim(pd.Timestamp('2002-01-01'), pd.Timestamp('2018-01-01'))
    ax.set_ylim(0.2,0.7)
    ax.legend(loc=9, ncol=2,fontsize=10)
    add_vlines(fig)
    format_xaxis(fig)
    plt.tight_layout()
    oName = out_root + os.sep + 'MC_Sample_Size_Time_Series.png'
    plt.savefig(oName)
    

    
    


