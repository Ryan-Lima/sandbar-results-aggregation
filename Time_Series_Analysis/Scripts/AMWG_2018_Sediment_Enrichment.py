# -*- coding: utf-8 -*-
"""
Created on Fri Sep 08 12:46:44 2017

@author: dan
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import platform
import os
from matplotlib import dates
import matplotlib.ticker as tkr


class OffsetYearLocator(dates.YearLocator):
    def __init__(self, *args, **kwargs):
        self.offset = kwargs.pop("offset", 0)
        dates.YearLocator.__init__(self,*args, **kwargs)
    def tick_values(self, vmin, vmax):
        ymin = self.base.le(vmin.year)-self.offset
        ymax = self.base.ge(vmax.year)+(self.base._base-self.offset)
        ticks = [vmin.replace(year=ymin, **self.replaced)]
        while True:
            dt = ticks[-1]
            if dt.year >= ymax:
                return dates.date2num(ticks)
            year = dt.year + self.base.get_base()
            ticks.append(dt.replace(year=year, **self.replaced))

def format_xaxis(ax):

    years = OffsetYearLocator(10,month=1,day=1, offset=7)
    years1=OffsetYearLocator(2,month=1,day=1, offset=1)
    dfmt = dates.DateFormatter('%Y')
    dfmt1 = dates.DateFormatter('%y')

    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_minor_locator(years1)
    ax.xaxis.set_major_formatter(dfmt)
    ax.xaxis.set_minor_formatter(dfmt1)
    for label in ax.xaxis.get_minorticklabels()[1::5]:
        label.set_visible(False)
    ax.get_xaxis().set_tick_params(which='major', pad=15)

    plt.setp(ax.get_xmajorticklabels(), rotation=0, weight="bold", ha="center")
             
def std_err_calc(df,metric):
        mc_std = pd.pivot_table(df, values=[metric], index=['TripDate'], aggfunc=np.std)
        mc_std = mc_std.rename(columns={metric:'std_dev'})
        mc_count = pd.pivot_table(df, values=[metric], index=['TripDate'], aggfunc='count')
        mc_count = mc_count.rename(columns={metric:'count'})    
        return mc_std.std_dev/np.sqrt(mc_count['count'])
    
def add_vlines(fig):
    hfe_dates = [pd.datetime(1996,4,1),pd.datetime(2004,11,22),pd.datetime(2008,3,8),pd.datetime(2012,11,20),pd.datetime(2013,11,11),pd.datetime(2014,11,11),pd.datetime(2016,11,7)]
    other_flow = [pd.datetime(1997,11,1),pd.datetime(2000,4,1),pd.datetime(2000,11,1)]
    for i in fig.axes:
        for d in hfe_dates:
            i.axvline(d,color='grey',linestyle='-',zorder=1)
        for d in other_flow:
            i.axvline(d,color='grey',linestyle='--',zorder=1)
    [i.set_xlim(pd.datetime(2003,01,01), pd.datetime(2019,01,01)) for i in fig.axes]

def excel_group(writer,tmp,tmp1,group):
    tmp.to_excel(writer, sheet_name=group,startcol=0,index=False)
    tmp1.to_excel(writer,sheet_name=group,startcol=6,index=False)
    
def get_measurment_errors(subset, group1, sandbar_root):
    tmp_df = pd.read_csv(sandbar_root + os.sep + 'Merged_Sandbar_Data.csv', sep =',')
    tmp_df['TripDate'] = pd.to_datetime(tmp_df['TripDate'], format='%Y-%m-%d')
    tmp_df = tmp_df[(tmp_df.Time_Series == 'long') & (tmp_df.SitePart == 'Eddy')] 
    tmp_df = tmp_df[tmp_df['Site'].isin(np.char.lower(group1))]
    tmp_df = tmp_df[tmp_df.Plane_Height != 'eddyminto8k']    
    tmp_df =  pd.pivot_table(tmp_df,index=['Site','SurveyDate','TripDate'],values=['Errors'],aggfunc=np.sum).reset_index()
    
    tmp_df = tmp_df.rename(columns={'Site':'SiteCode'})
    tmp_df.SiteCode = tmp_df.SiteCode.str.upper()
    subset = subset.set_index(['SiteCode','SurveyDate','TripDate']).combine_first(tmp_df.set_index(['SiteCode','SurveyDate','TripDate'])).reset_index()
    return subset[['SiteCode', 'SurveyDate', 'TripDate', 'Area', 'Volume', 'Errors', 'Max_Area', 'Max_Vol', 'Norm_Area', 'Norm_Vol', 'Time_Series']]
    
    
    
if __name__ =='__main__':
    if platform.system() == 'Darwin':
        sandbar_root = '/~/git_clones/sandbar-results-aggregation/Time_Series_Analysis/input'
        time_root = '/~/git_clones/sandbar-results-aggregation/Time_Series_Analysis'
        out_root = time_root + os.sep + 'Output'
    elif platform.system() == 'Windows':
        sandbar_root = r'C:\workspace\sandbar-results-aggregation\Time_Series_Analysis\input'
        time_root = r'C:\workspace\sandbar-results-aggregation\Time_Series_Analysis'
        out_root = time_root + os.sep + r'Output'
        
    
    #Sediment Deficit Sites
    
    lu_sites = pd.read_csv(r"C:\vbox_share\Sites.csv",sep=',')
    lu_sites = lu_sites[['SiteCode','InitialSurvey']]
    lu_sites = lu_sites[lu_sites['InitialSurvey'] <'2003-01-01']
    lu_sites = lu_sites[['SiteCode']]
    lu_sites = lu_sites[lu_sites['SiteCode'] != 'M006R']
    
    
    #designate groups       
    g_1a = np.char.upper(np.array(['145l','022r','213l','084r','030r','081l','137l','119r','122r']))
    g_1b = np.char.upper(np.array(['123l','172l','041r','044l','183r','220r','050r','065r','047r']))  #'009l' dropped because it was added in 2008,-'045l' dropped 045L because sep and reatt bar wasnt surveyed each time
    g_1c = np.char.upper(np.array(['194l','068r','051l','055r'])) # '070r' dropped because it was added in 2008
    g_2 = np.char.upper(np.array(['008l','024l','029l','032r','056r']))# ,'167l' removed because it is a technical outlier
    g_3 = np.char.upper(np.array(['043l','087l','093l','139r','225r','104r']))
    g_4 = np.char.upper(np.array(['016l','033l','035l','062r','091r','202r']) ) 
    
    data_file = sandbar_root + os.sep + 'Complete_TimeSeries.csv'
    data = pd.read_csv(data_file, sep =',')
    
    data['TripDate'] = pd.to_datetime(data['TripDate'], format='%Y-%m-%d')
    data = data[data['TripDate']>='2003-09-20']
    
    data['Time_Series'] = data['Time_Series'].fillna(value='long')
    data = data[(data.Time_Series == 'long')] 
    
    fig , (ax_0,ax_1) = plt.subplots(figsize=(7.5,6),nrows=2,sharex=True)
    fig1 , (ax1_0,ax1_1) = plt.subplots(figsize=(7.5,6),nrows=2,sharex=True)
    r=['Group 1a','Group 1b','Group 1c','Group 2','Group 3','Group 4']
    n=0
    m = ['o','x','d','^','*','s']
    m_size=4
    ls = ['-','--','-.',':','-','--']
    colors=['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c']
    writer = pd.ExcelWriter(out_root + os.sep + 'AMWG_2018_SE_Sandbar_Plot_Data.xlsx',engine='xlsxwriter')
    
    for group1 in [g_1a,g_1b,g_1c]:
        
        #print group1
        subset = data[data['SiteCode'].isin(group1)]
        
        #Find Common dates
        subset = subset[subset.Plane_Height != 'eddyminto8k']     
        date_fz = subset[(subset['Volume']>0) & (subset['Plane_Height'] == 'eddy8kto25k') ].SurveyDate.unique()
        date_he = subset[(subset['Volume']>0) & (subset['Plane_Height'] == 'eddyabove25k') ].SurveyDate.unique()
        common_dates = np.intersect1d(date_fz,date_he)
        subset = subset[subset['SurveyDate'].isin(common_dates)]
        
        
        
        #calculate above 8k metrics
        subset =  pd.pivot_table(subset,index=['SiteCode','SurveyDate','TripDate','Time_Series'],values=['Area','Volume','Max_Vol'],aggfunc=np.sum).reset_index()
        
        
        subset1 = data[data['SiteCode'].isin(group1)]
        subset1 = pd.pivot_table(subset1,index=['SiteCode','SurveyDate','TripDate','Time_Series'],values=['Max_Area'],aggfunc=np.average).reset_index()
        subset = subset.merge(subset1, on=['SiteCode','SurveyDate','TripDate','Time_Series'],how='left')

        
        subset.loc[:,'Norm_Area']=subset.loc[:,'Area']/subset.loc[:,'Max_Area']
        subset.loc[:,'Norm_Vol'] = subset.loc[:,'Volume']/subset.loc[:,'Max_Vol']
        
        subset = get_measurment_errors(subset, group1,sandbar_root)
        subset['Errors'] = subset['Errors'].fillna(subset['Area']*0.04)
        subset = subset[(subset.Time_Series == 'long')]
        #only sediment deficit sites for the sediment deficit periods
        subset = subset[(subset['SiteCode'].isin(set(lu_sites['SiteCode'].str.upper())))]
        print r[n] + ' contains ' + str(subset.SiteCode.unique())
                
        #summation metrics for plotting
        tmp = pd.pivot_table(subset, index='TripDate',values=['Volume', 'Area', 'Errors'],aggfunc=[np.sum,len]).reset_index()
        tmp = tmp.iloc[:,0:-2]
        tmp.columns = tmp.columns.droplevel(0)
        tmp.columns = ['TripDate','Area','Errors','Volume','N']
        
        #average normalized metrics for plotting
        tmp1 = pd.pivot_table(subset, index=['TripDate'], values=['Norm_Vol','Norm_Area'],aggfunc=np.average).reset_index()
        

        #Volume Plot
        tmp.plot(x='TripDate',y='Volume',yerr='Errors',ax=ax_0,label=r[n],sharex=ax_0,capsize=2,zorder=10,marker=m[n],ms=m_size,c=colors[n],linestyle=ls[n])
        tmp1.plot(x='TripDate',y='Norm_Vol', yerr=std_err_calc(subset,'Norm_Vol'),ax=ax1_0,label=r[n],marker=m[n],capsize=2,zorder=10,ms=m_size,c=colors[n],linestyle=ls[n])
        excel_group(writer,tmp,tmp1,r[n])
        n+=1
     
        
        
    for group1 in [g_2,g_3,g_4]:
        #print group1
        subset = data[data['SiteCode'].isin(group1)]
        
        #Find Common dates
        subset = subset[subset.Plane_Height != 'eddyminto8k']     
        date_fz = subset[(subset['Plane_Height'] == 'eddy8kto25k') ].SurveyDate.unique()
        date_he = subset[ (subset['Plane_Height'] == 'eddyabove25k') ].SurveyDate.unique()
        common_dates = np.intersect1d(date_fz,date_he)
        subset = subset[subset['SurveyDate'].isin(common_dates)]
        
        
        
        #calculate above 8k metrics
        subset =  pd.pivot_table(subset,index=['SiteCode','SurveyDate','TripDate','Time_Series'],values=['Area','Volume','Max_Vol'],aggfunc=np.sum).reset_index()
        
        
        subset1 = data[data['SiteCode'].isin(group1)]
        
        subset1 = pd.pivot_table(subset1,index=['SiteCode','SurveyDate','TripDate','Time_Series'],values=['Max_Area'],aggfunc=np.average).reset_index()
        subset = subset.merge(subset1, on=['SiteCode','SurveyDate','TripDate','Time_Series'],how='left')

        
        subset.loc[:,'Norm_Area']=subset.loc[:,'Area']/subset.loc[:,'Max_Area']
        subset.loc[:,'Norm_Vol'] = subset.loc[:,'Volume']/subset.loc[:,'Max_Vol']
        
        subset = get_measurment_errors(subset, group1,sandbar_root)
        subset['Errors'] = subset['Errors'].fillna(subset['Area']*0.04)
        subset = subset[(subset.Time_Series == 'long')]
        
        #only sediment deficit sites for the sediment deficit periods
        subset = subset[(subset['SiteCode'].isin(set(lu_sites['SiteCode'].str.upper())))]
        print r[n] + ' contains  ' + str(subset.SiteCode.unique())
        
        #summation metrics for plotting
        tmp = pd.pivot_table(subset, index='TripDate',values=['Volume', 'Area', 'Errors'],aggfunc=[np.sum,len]).reset_index()
        tmp = tmp.iloc[:,0:-2]
        tmp.columns = tmp.columns.droplevel(0)
        tmp.columns = ['TripDate','Area','Errors','Volume','N']
        
        #average normalized metrics for plotting
        tmp1 = pd.pivot_table(subset, index=['TripDate'], values=['Norm_Vol','Norm_Area'],aggfunc=np.average).reset_index()
        

        #Volume Plot
        tmp.plot(x='TripDate',y='Volume',yerr='Errors',ax=ax_1,label=r[n],sharex=ax_0,capsize=2,zorder=10,marker=m[n],ms=m_size,c=colors[n],linestyle=ls[n])
        tmp1.plot(x='TripDate',y='Norm_Vol', yerr=std_err_calc(subset,'Norm_Vol'),ax=ax1_1,label=r[n],marker=m[n],capsize=2,zorder=10,ms=m_size,c=colors[n],linestyle=ls[n])
        excel_group(writer,tmp,tmp1,r[n])
        n+=1       
        
        

    [i.set_xlabel('DATE') for i in fig.axes]
    [i.set_xlabel('DATE') for i in fig1.axes]
    
    add_vlines(fig)
    add_vlines(fig1)

    ax_0.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x), ',')))

    ax_1.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    [i.legend(loc='upper center',bbox_to_anchor=(0.5,1.15),ncol=3, fancybox=True, shadow=True) for i in fig.axes]
    [i.legend(loc='upper center',bbox_to_anchor=(0.5,1.15),ncol=3, fancybox=True, shadow=True) for i in fig1.axes]

    #Format Axis Options
    [format_xaxis(i) for i in fig.axes]
    [format_xaxis(i) for i in fig1.axes]  
        
    fig.axes[0].set_ylim(0,70000)  
    fig.axes[1].set_ylim(0,17500)  
    fig1.axes[0].set_ylim(0,1)  
    fig1.axes[1].set_ylim(0,1)
    #fig1.axes[2].set_ylim(0,1.0)
    
    fig1.axes[0].set_ylabel('NORMALIZED VOLUME')
    fig1.axes[1].set_ylabel('NORMALIZED VOLUME')
    
    fig.axes[0].set_ylabel('VOLUME, IN CUBIC METERS')
    fig.axes[1].set_ylabel('VOLUME, IN CUBIC METERS')

    
    [i.tight_layout() for i in [fig,fig1]]
    [i.subplots_adjust(top=0.926) for i in [fig,fig1]]  
    fig.savefig(out_root + os.sep + '2018_AMWG_SE_Cumlative_Volume.png')
    fig1.savefig(out_root + os.sep +'2018_AMWG_SE_Normalized_Volume.png')

    writer.save()