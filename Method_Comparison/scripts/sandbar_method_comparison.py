# -*- coding: utf-8 -*-
"""
Created on Thu Jan 04 13:11:53 2018

@author: dan
"""
from sandbar_mysql_data_formatter import data_formatter
import platform
import os
import pandas as pd
import pytablewriter
import matplotlib.pyplot as plt
from matplotlib import dates
import numpy as np

def make_markdown(df, title):
    writer = pytablewriter.MarkdownTableWriter()
    writer.table_name =  title
    writer.header_list = list(df.columns.values)
    writer.value_matrix = df.values.tolist()
    writer.write_table()


def format_xaxis(fig):
     years = dates.YearLocator(10,month=1,day=1)
     years1=dates.YearLocator(2,month=1,day=1)
     dfmt = dates.DateFormatter('%Y')
     dfmt1 = dates.DateFormatter('%y')
    
     [i.xaxis.set_major_locator(years) for i in fig.axes[:-2]]
     [i.xaxis.set_minor_locator(years1) for i in fig.axes[:-2]]
     [i.xaxis.set_major_formatter(dfmt) for i in fig.axes[:-2]]
     [i.xaxis.set_minor_formatter(dfmt1) for i in fig.axes[:-2]]
     [i.get_xaxis().set_tick_params(which='major', pad=15) for i in fig.axes[:-2]]
    
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
             
             
             
def check4missing_surveys(c_ts, t_ts,sites2checkfor):
    '''
    Function to compare two dataframes for missing records
    Inputs: 
        c_ts - Dataframe containing data from the mysql database
        t_ts = Dataframe containing data from Merged_Sandbar_data
    Outputs:
        Dataframe with conflicting dates
    '''
    
        

    
    c_ts = c_ts[c_ts['SiteCode'].isin(sites2checkfor)]
    t_ts = t_ts[t_ts['SiteCode'].isin(sites2checkfor)]
    
    
    c_ts = c_ts[['SiteCode','SurveyDate','TripDate','Plane_Height']]
    t_ts = t_ts[['SiteCode','SurveyDate','TripDate','Plane_Height']]
    

    c_ts = c_ts.drop_duplicates()
    
    df_all = c_ts.merge(t_ts, on=['SiteCode','TripDate','Plane_Height','SurveyDate'],how='left', indicator=True)
    df_all = df_all[df_all['_merge'] == 'left_only']
    return df_all[['SiteCode','SurveyDate','TripDate']].drop_duplicates()
    
    
def get_mysql_data(in_file):
    '''
    Function to retreive formated data from the MySQL database
    Input:File path to csv export from the database
    Output: Dataframe with sandbar data
    Notes:
        see data_formatter? for info on MySQL export
    
    '''
    
    result = data_formatter(in_file)
    result['TripDate'] = pd.to_datetime(result['TripDate'], format='%Y-%m-%d')
    result['SurveyDate'] = pd.to_datetime(result['SurveyDate'], format='%Y-%m-%d')    
    return result

def find_eddymin8k_nobath(c_ts):
    no_bath_sites = ['008L','009L','024L','029L','033L','056R','070R','084R','167L']
    df = c_ts[c_ts['SiteCode'].isin(no_bath_sites)]
    df = df[df['Plane_Height']=='eddyminto8k']
    make_markdown(df,'Bathymetry mesurements at sites without bathymetry')
    
def get_tin_data(in_file):
    df = pd.read_csv(in_file, sep =',')
    df.Site = df.Site.str.upper()
    df['TripDate'] = pd.to_datetime(df['TripDate'], format='%Y-%m-%d')
    df['SurveyDate'] = pd.to_datetime(df['SurveyDate'], format='%Y-%m-%d')
    df = df.rename(columns={'Area_2D':'Area','MaxVol':'Max_Vol','Site':'SiteCode'})
    df = df[df['Plane_Height'] != 'chanminto8k']
    df = df[df['Plane_Height'] != 'eddyminto8k']
    return df[['SiteCode', 'SurveyDate', 'TripDate', 'Plane_Height', 'Area', 'Volume', 'Time_Series','Max_Area', 'Max_Vol']]


def compare_metrics(p_ts, t_ts,plane_height, metric):
    '''
    Funcition to create site plots of specified metrics and bins
    Inputs:
        p_ts: Dataframe containg data from the mysql database
        t_ts: Dataframe containg data from the TIN method
    Outputs:
        Matplotlib figure and axes objects
    Notes:
        Any above 8k metrics will have the added column thinkness. 
        I dont think thickness is a very robuse metric for the indivudal computaion bins, since we dont have indivdual computaitonal bin max area numbers
    
    '''
    
    fig, axes = plt.subplots(nrows=6, ncols=6, figsize=(18,10))

    
    if plane_height != 'eddyabove8k':
        axes_list = [item for sublist in axes for item in sublist] 
        for sitecode, selection in p_ts[['SiteCode','TripDate','Plane_Height','Time_Series', 'Area', 'Volume',]][(p_ts['Plane_Height'] == plane_height)&(p_ts['Time_Series'] == 'long')].groupby(['SiteCode']):
            ax = axes_list.pop(0)
            ax.plot_date(selection['TripDate'], selection[metric], 'k-', label='Raster', marker = 'x')
            ax.set_title(sitecode)
        
        axes_list = [item for sublist in axes for item in sublist] 
        
        for sitecode, selection in t_ts[['SiteCode','TripDate','Plane_Height','Time_Series', 'Area', 'Volume',]][(t_ts['Plane_Height'] == plane_height)&(t_ts['Time_Series'] == 'long')].groupby(['SiteCode']):
            ax = axes_list.pop(0)
            ax.plot_date(selection['TripDate'], selection[metric], 'r-', label='Tin', marker = '+')
    else:
        axes_list = [item for sublist in axes for item in sublist] 
        
        for sitecode, selection in p_ts[['SiteCode','TripDate','Time_Series', 'Area', 'Volume','Thickness']][(p_ts['Time_Series'] == 'long')].groupby(['SiteCode']):
            ax = axes_list.pop(0)
            ax.plot_date(selection['TripDate'], selection[metric], 'k-', label='Raster', marker = 'x')
            ax.set_title(sitecode)
        
        axes_list = [item for sublist in axes for item in sublist] 
        
        for sitecode, selection in t_ts[['SiteCode','TripDate','Time_Series', 'Area', 'Volume','Thickness']][(t_ts['Time_Series'] == 'long')].groupby(['SiteCode']):
            ax = axes_list.pop(0)
            ax.plot_date(selection['TripDate'], selection[metric], 'r-', label='Tin', marker = '+')
            
            
    plt.suptitle(metric + ':' + plane_height)
    format_xaxis(fig)
    fig.tight_layout()
    fig.subplots_adjust(top=0.920)
    fig.axes[0].legend(loc='center left', bbox_to_anchor=(1.2, 1.5)) 
    fig.savefig(out_root + os.sep + metric + '_' + plane_height +'.png')
    return fig, axes

def thick_calc(df):
    
    df.loc[:,'Thickness'] = df.loc[:,'Volume']/df.loc[:,'Max_Area']
    return df

def std_err_calc(df,metric):
        mc_std = pd.pivot_table(df, values=[metric], index=['TripDate'], aggfunc=np.std)
        mc_std = mc_std.rename(columns={metric:'std_dev'})
        mc_count = pd.pivot_table(df, values=[metric], index=['TripDate'], aggfunc='count')
        mc_count = mc_count.rename(columns={metric:'count'})    
        return mc_std.std_dev/np.sqrt(mc_count['count'])
    
    
def aggregrate_above8k_data(df):
    '''
    Function to aggregrate FZ and HE bins for time series analysis
    Inputs:
    '''
    
    tmp = pd.pivot_table(df,index=['SiteCode', 'SurveyDate', 'TripDate','Time_Series'],values=['Area','Volume','Max_Vol'],aggfunc=np.sum)
    tmp1 = pd.pivot_table(df,index=['SiteCode', 'SurveyDate', 'TripDate','Time_Series'],values=['Max_Area'],aggfunc=np.average)
    
    return thick_calc(tmp.combine_first(tmp1).reset_index())
def min_surface_comparison(p_ts, t_ts):
    
    sites2checkfor = ['003L', '008L', '016L', '022R', '030R',
       '032R', '043L', '044L', '047R', '050R',  '051L', '055R',
        '062R',  '065R', '068R', '081L', '087L', '091R', '093L',
       '104R', '119R', '122R', '123L', '137L', '139R', '145L',
       '172L', '183R', '194L', '202R', '213L', '220R',
       '225R', 'M006R']
    
    p_ts = p_ts[p_ts['SiteCode'].isin(sites2checkfor)]

    t_ts = t_ts[t_ts['SiteCode'].isin(sites2checkfor)]
    
    p_ts = p_ts[(p_ts['TripDate']>pd.datetime(1995,1,1)) &(p_ts['TripDate']<'2015-01-01')]
    t_ts = t_ts[(t_ts['TripDate']>pd.datetime(1995,1,1)) &(t_ts['TripDate']<'2015-01-01')]

    missing_surveys = check4missing_surveys(p_ts,t_ts,sites2checkfor).sort_values(['SiteCode','SurveyDate'])    
    
    fig,axes = compare_metrics(p_ts, t_ts, 'eddy8kto25k','Area')

    fig1, axes1 = compare_metrics(p_ts, t_ts, 'eddy8kto25k','Volume')
    
    fig2,axes2 = compare_metrics(p_ts, t_ts, 'eddyabove25k','Area')

    fig3, axes3 = compare_metrics(p_ts, t_ts, 'eddyabove25k','Volume')
    
    #get above 8k data
    p_ts = aggregrate_above8k_data(p_ts)
    t_ts = aggregrate_above8k_data(t_ts)
    
    fig4,axes4 = compare_metrics(p_ts,t_ts,'eddyabove8k','Area')
    fig5,axes5 = compare_metrics(p_ts,t_ts,'eddyabove8k','Volume')
    fig6,axes6 = compare_metrics(p_ts,t_ts,'eddyabove8k','Thickness')

    
    p_ts[['SiteCode','TripDate', 'Area', 'Volume',]].groupby('SiteCode').plot(kind='line',x='TripDate',y='Area',subplots=True)
if __name__ == '__main__':
    
    
    if platform.system() == 'Darwin':
        sandbar_root = '/~/git_clones/sandbar-results-aggregation/Method_Comparison/input'
        time_root = '/~/git_clones/sandbar-results-aggregation/Method_Comparison'
        out_root = time_root + os.sep + 'Output'
    elif platform.system() == 'Windows':
        sandbar_root = r'C:\workspace\sandbar-results-aggregation\Method_Comparison\input'
        time_root = r'C:\workspace\sandbar-results-aggregation\Method_Comparison'
        out_root = time_root + os.sep + r'Output'
    
    c_ts = get_mysql_data(sandbar_root + os.sep + 'Complete_TimeSeries.csv')
    c_ts = c_ts[c_ts['Plane_Height'] != 'eddyminto8k']
    p_ts = get_mysql_data(sandbar_root + os.sep + 'MinSurface_time_series.csv')
    p_ts = p_ts[p_ts['Plane_Height'] != 'eddyminto8k']
    t_ts = get_tin_data(sandbar_root + os.sep + "Merged_Sandbar_data.csv")
    t_ts = t_ts[t_ts['Plane_Height'] != 'eddyminto8k']
    
    
    
    sites2checkfor = ['003L', '008L', '016L', '022R', '030R',
       '032R', '043L', '044L', '047R', '050R',  '051L', '055R',
        '062R',  '065R', '068R', '081L', '087L', '091R', '093L',
       '104R', '119R', '122R', '123L', '137L', '139R', '145L',
       '172L', '183R', '194L', '202R', '213L', '220R',
       '225R', 'M006R']
    #check for date issues
    missing_surveys = check4missing_surveys(p_ts,t_ts, )
    
    df_all.merge(t_ts[['SiteCode','SurveyDate','TripDate']], on=['SiteCode','SurveyDate'],how='left').drop_duplicates()
    df_all = c_ts[['SiteCode','TripDate','Plane_Height','SurveyDate']].merge(t_ts[['SiteCode','TripDate','Plane_Height','Area','Volume']], on=['SiteCode','TripDate','Plane_Height'], how='left', indicator=True)
    df_all = c_ts[['SiteCode','TripDate','Plane_Height','Area','Volume']].merge(t_ts[['SiteCode','TripDate','Plane_Height','Area','Volume']], on=['SiteCode','TripDate','Plane_Height'], how='left', indicator=True)
    
#    missing_surveys = check4missing_surveys(c_ts,p_ts)
#    
#    no_bath_sites = ['008L','009L','024L','029L','033L','056R','070R','084R','167L']