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
from scipy.stats import linregress

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
    g_1b = np.array(['009l','123l','172l','044l','045l','044l','183r','220r','050r','065r','047r'])
    g_1c = np.array(['070r','194l','068r','051l','055r'])
    g_2 = np.array(['008l','024l','029l','032r','056r'])# ,'167l' removed because it is a technical outlier
    g_3 = np.array(['043l','087l','093l','139r','225r','104r'])
    g_4 = np.array(['016l','033l','035l','091r','202r'])  #'062r' removed because it is a tecnical outlier


    
    data_file = sandbar_root + os.sep + 'Merged_Sandbar_data.csv'
    data = pd.read_csv(data_file, sep =',')
    
    data['TripDate'] = pd.to_datetime(data['TripDate'], format='%Y-%m-%d')

    data = data[(data.Time_Series == 'long') & (data.SitePart == 'Eddy')] 
    
    fig, ((ax_0,ax1_0),(ax2_0,ax3_0),(ax4_0,ax5_0)) = plt.subplots(nrows=3,ncols=2,figsize=(7.5,9),sharex=True,sharey=True)
    
    r=['Group 1a','Group 1b','Group 1c','Group 2','Group 3','Group 4']
    n=0
    m = ['o','x','d','^','*','s']
    m_size=4
    ls = ['-','--','-.',':','-','--']
    colors=['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c']
    writer = pd.ExcelWriter(out_root + os.sep +'NormalizedVol_NormalizedArea_bivariate.xlsx',engine='xlsxwriter')
    
    
    for group1 in [g_1a,g_1b,g_1c,g_2,g_3,g_4]:
        subset = data[data['Site'].isin(group1)]
        #Find Common dates
        subset = subset[subset.Plane_Height != 'eddyminto8k']     
        date_fz = subset[(subset['Volume']>0) & (subset['Plane_Height'] == 'eddy8kto25k') ].SurveyDate.unique()
        date_he = subset[(subset['Volume']>0) & (subset['Plane_Height'] == 'eddyabove25k') ].SurveyDate.unique()
        common_dates = np.intersect1d(date_fz,date_he)
        subset = subset[subset['SurveyDate'].isin(common_dates)]
        
        #calculate above 8k metrics
        subset =  pd.pivot_table(subset,index=['Site','SurveyDate','SitePart','TripDate','SiteRange','Segment','Bar_type','Time_Series','Period'],values=['Area_2D','Area_3D','Volume','Errors','MaxVol'],aggfunc=np.sum).reset_index()
        subset1 = data[data['Site'].isin(group1)]
        
        subset1 = pd.pivot_table(subset1,index=['Site','SurveyDate','SitePart','TripDate','SiteRange','Segment','Bar_type','Time_Series','Period'],values=['Max_Area'],aggfunc=np.average).reset_index()
        subset = subset.merge(subset1, on=['Site','SurveyDate','SitePart','TripDate','SiteRange','Segment','Bar_type','Time_Series','Period'],how='left')
        del subset1
        
        subset.loc[:,'Norm_Area']=subset.loc[:,'Area_2D']/subset.loc[:,'Max_Area']
        subset.loc[:,'Norm_Vol'] = subset.loc[:,'Volume']/subset.loc[:,'MaxVol']
        
        subset2 = pd.pivot_table(subset,index=['TripDate'], values=['Norm_Area','Norm_Vol'], aggfunc=np.average)
        s,i,rr,p,err = linregress(subset['Norm_Vol'],subset['Norm_Area'])
        s = '%1.4f' %s
        rr = '%1.4f' %rr**2
        p = "%04.03e" %p
        label = r[n] + ' slope: ' + s + ', R$^2$: '+ rr + ', p-value: ' + p
        subset2.plot(x='Norm_Vol', y='Norm_Area',ax=fig.axes[n],marker=m[n],ls=' ',ms=m_size,c='k', label=label) 
        fig.axes[n].plot(subset['Norm_Vol'],i+subset['Norm_Vol']*linregress(subset['Norm_Vol'],subset['Norm_Area'])[0],'k')  
        fig.axes[n].set_title(r[n])
        n+=1
        
    [i.legend_.remove() for i in fig.axes]
    [i.set_ylabel('NORMALIZED AREA') for i in fig.axes]
    [i.set_xlabel('NORMALIZED VOLUME') for i in fig.axes]

    [i.set_ylim(0.1,0.8) for i in fig.axes]
    [i.set_xlim(0.1,0.8) for i in fig.axes]
    
    handles, labels = [],[]
    
    [handles.append(i.get_legend_handles_labels()[0][0]) for i in fig.axes]
    [labels.append(i.get_legend_handles_labels()[1][0]) for i in fig.axes]
    
    fig.legend(handles = handles, labels=labels, loc = 'lower center', bbox_to_anchor = (0,0.005,1,1),
            bbox_transform = fig.transFigure,ncol=2,fontsize='small')
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.18)
    writer.save()
    fig.savefig(out_root + os.sep +'NormalizedVol_NormalizedArea_bivariate.png')

    
    
    
#    df =  data[data['Site'] == '035l_r']
#df = pd.pivot_table(df, index=['Site','TripDate'], values=['Area_2D'],aggfunc=np.sum).reset_index().set_index('TripDate')
#
#subset2 = subset2.combine_first(df[['Area_2D']])
#
#subset2['cmap'] = subset2.apply(lambda row: add_colormapper(row),axis=1)
#
#
#colors = {'reatt_present':'r','reatt_absent':'k'}
#
#
#fig,ax = plt.subplots()
#for name, group in subset2.groupby('cmap'):
#    print name
#    ax.scatter(group['Norm_Vol'],group['Norm_Area'],c=colors[name],label=name)
#
#
#ax.set_ylim(0,0.5)
#ax.set_xlim(0,0.5)
#ax.set_title('Group 4, 035L reatt bar presence')
#[i.set_ylabel('NORMALIZED AREA') for i in fig.axes]
#[i.set_xlabel('NORMALIZED VOLUME') for i in fig.axes]
#
#
##Bins to find cluster
#Norm_area = (0.26,0.35)
#Norm_vol = (0.2,0.33)
    
g = subset2[(subset2['Norm_Area']>0.26) &(subset2['Norm_Area']<0.35) &(subset2['Norm_Vol']>0.2) &(subset2['Norm_Vol']<0.33)]
h = subset2[(subset2['Norm_Area']>0.0) &(subset2['Norm_Area']<0.24) &(subset2['Norm_Vol']>0.17) &(subset2['Norm_Vol']<0.45)]

t =subset.pivot(index='Site',columns='TripDate', values = 'Site')