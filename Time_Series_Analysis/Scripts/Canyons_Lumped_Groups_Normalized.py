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
    g_1ab = np.char.upper(np.array(['145l','022r','213l','084r','030r','137l','119r','122r','123l','172l','041r','044l','183r','220r','050r','065r','047r','009l']))
    g_1c_3 = np.char.upper(np.array(['194l','068r','051l','055r','043l','087l','093l','139r','225r','104r','070r'])) # '070r' dropped because it was added in 2008
    g_24 = np.char.upper(np.array(['008l','024l','029l','032r','056r','016l','033l','035l','062r','091r','202r','081l']))# ,'167l' removed because it is a technical outlier

    data_file = sandbar_root + os.sep + 'Complete_TimeSeries.csv'
    data = pd.read_csv(data_file, sep =',')
    
    data['TripDate'] = pd.to_datetime(data['TripDate'], format='%Y-%m-%d')
    data = data[data['TripDate']>='2003-09-20']
    
    data['Time_Series'] = data['Time_Series'].fillna(value='long')
    data = data[(data.Time_Series == 'long')] 
    data['RM'] = pd.to_numeric(data['SiteCode'].str.slice(0,3,1), errors='coerce')
    fig , axes = plt.subplots(figsize=(7.5,9),nrows=3,sharex=True)
    axes_list = [item for item in axes]
    r=['Groups 1a and 1b','Groups 1c and 3','Groups 2 and 4']
    n=0
    m = ['o','x','d','^','*','s']
    m_size=4
    ls = ['-','--','-.',':','-','--']
    colors=['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c']
    #writer = pd.ExcelWriter(out_root + os.sep + 'Lumped_Groups_SE_Sandbar_Plot_Data.xlsx',engine='xlsxwriter')

    for group1 in [g_1ab,g_1c_3,g_24]:
        ax = axes_list.pop(0)
        #print group1
        subset = data[(data['SiteCode'].isin(group1)) &(data['RM'] < 60)]
        
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
        #subset = subset[(subset['SiteCode'].isin(set(lu_sites['SiteCode'].str.upper())))]
        print r[n] + ' contains ' + str(subset.SiteCode.unique())
                
        #summation metrics for plotting
        tmp = pd.pivot_table(subset, index='TripDate',values=['Volume', 'Area', 'Errors'],aggfunc=[np.sum,len]).reset_index()
        tmp = tmp.iloc[:,0:-2]
        tmp.columns = tmp.columns.droplevel(0)
        tmp.columns = ['TripDate','Area','Errors','Volume','N']
        
        #average normalized metrics for plotting
        tmp1 = pd.pivot_table(subset, index=['TripDate'], values=['Norm_Vol','Norm_Area'],aggfunc=np.average).reset_index()
        

        #Volume Plot

        tmp1.plot(x='TripDate',y='Norm_Vol', yerr=std_err_calc(subset,'Norm_Vol'),ax=ax,label=r[n],marker=m[n],capsize=2,zorder=10,ms=m_size,c=colors[n],linestyle=ls[n])
        #excel_group(writer,tmp,tmp1,r[n])
        n+=1
        

    [i.set_xlabel('DATE') for i in fig.axes]
    
    add_vlines(fig)
    [format_xaxis(i) for i in fig.axes]

    ax_0.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x), ',')))

    ax_1.legend_.remove()
    ax_0.legend(loc = 'lower center', bbox_to_anchor = (0,0.005,1,1),ncol=3, bbox_transform = fig.transFigure,fancybox=True, shadow=True)
    #Format Axis Options
    [format_xaxis(i) for i in fig.axes]

        
    fig.axes[0].set_ylim(0,60000)  
    fig.axes[1].set_ylim(0,1)    

    
    fig.axes[0].set_ylabel('VOLUME, IN CUBIC METERS')
    fig.axes[1].set_ylabel('NORMALIZED VOLUME')

    
    fig.tight_layout() 
    fig.suptitle('Marble Canyon')
    fig.subplots_adjust(bottom=0.164, top = 0.951) 

    fig.savefig(out_root + os.sep + 'Marble_Canyon_SE_allData_Lumped_Groups_Volume.png')
#================================================================================================================================================================
    fig , (ax_0,ax_1) = plt.subplots(figsize=(7.5,6),nrows=2,sharex=True)
    r=['Groups 1a and 1b','Groups 1c and 3','Groups 2 and 4']
    n=0
    m = ['o','x','d','^','*','s']
    m_size=4
    ls = ['-','--','-.',':','-','--']
    colors=['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c']
    

    for group1 in [g_1ab,g_1c_3,g_24]:
        
        #print group1
        subset = data[(data['SiteCode'].isin(group1)) & (data['RM'] > 60)]
        
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
        #subset = subset[(subset['SiteCode'].isin(set(lu_sites['SiteCode'].str.upper())))]
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
        tmp1.plot(x='TripDate',y='Norm_Vol', yerr=std_err_calc(subset,'Norm_Vol'),ax=ax_1,label=r[n],marker=m[n],capsize=2,zorder=10,ms=m_size,c=colors[n],linestyle=ls[n])
        #excel_group(writer,tmp,tmp1,r[n])
        n+=1
        

    [i.set_xlabel('DATE') for i in fig.axes]
    
    add_vlines(fig)
    [format_xaxis(i) for i in fig.axes]

    ax_0.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x), ',')))

    ax_1.legend_.remove()
    ax_0.legend(loc = 'lower center', bbox_to_anchor = (0,0.005,1,1),ncol=3, bbox_transform = fig.transFigure,fancybox=True, shadow=True)
    #Format Axis Options
    [format_xaxis(i) for i in fig.axes]

        
    fig.axes[0].set_ylim(0,60000)  
    fig.axes[1].set_ylim(0,1)    

    
    fig.axes[0].set_ylabel('VOLUME, IN CUBIC METERS')
    fig.axes[1].set_ylabel('NORMALIZED VOLUME')

    
    fig.tight_layout() 
    fig.suptitle('Grand Canyon')
    fig.subplots_adjust(bottom=0.164, top = 0.951) 
    fig.savefig(out_root + os.sep + 'Grand_Canyon_SE_alldata_Lumped_Groups_Volume.png')
