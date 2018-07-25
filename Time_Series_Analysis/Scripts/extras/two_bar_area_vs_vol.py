# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 15:26:23 2017

@author: dan
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import platform
import os
from scipy.stats import linregress

if __name__ =='__main__':
    if platform.system() == 'Darwin':
        sandbar_root = '/~/git_clones/sandbar-results-aggregation/Time_Series_Analysis/input'
        time_root = '/~/git_clones/sandbar-results-aggregation/Time_Series_Analysis'
        out_root = time_root + os.sep + 'Output'
    elif platform.system() == 'Windows':
        sandbar_root = r'C:\workspace\sandbar-results-aggregation\Time_Series_Analysis\input'
        time_root = r'C:\workspace\sandbar-results-aggregation\Time_Series_Analysis'
        out_root = time_root + os.sep + r'Output'
        
        
    #Read Data from file
    data_file = sandbar_root + os.sep + 'Merged_Sandbar_data.csv'
    data = pd.read_csv(data_file, sep =',')
    
    data['TripDate'] = pd.to_datetime(data['TripDate'], format='%Y-%m-%d')
    
    data = data[(data.Time_Series == 'long') & (data.SitePart == 'Eddy') & (data.Plane_Height != 'eddyminto8k')]
    
    #subset to two bar sites
    data = data[data.Site.str.len()>4]
    
    #Get Rid of zeros
    data = data[data['Area_2D']>0]
    
    data = pd.pivot_table(data,index=['Site','SurveyDate','SitePart','TripDate','SiteRange','Segment','Bar_type','Time_Series','Period'],values=['Area_2D','Area_3D','Volume','Errors','MaxVol','Max_Area'],aggfunc=np.sum).reset_index()
    #Group by bar type
    grouped = data.groupby('Bar_type')
    reatt = grouped.get_group('Reattachment')
    sep = grouped.get_group('Separation')
    
    for r_site, s_site in zip(reatt.Site.unique(),sep.Site.unique()):
        r_subset = reatt[reatt['Site'] == r_site]
        s_subset = sep[sep['Site'] == s_site]
    
        #find dates where both high elevation and fluctuating zone
        common_dates = np.intersect1d(r_subset.SurveyDate.unique(),s_subset.SurveyDate.unique())
        r_subset = r_subset[r_subset['SurveyDate'].isin(common_dates)]
        s_subset = s_subset[s_subset['SurveyDate'].isin(common_dates)]
        
        fig, (ax) = plt.subplots(figsize=(7.5,2.5))
        s,i,r,p,stderr = linregress(s_subset['Volume'], s_subset['Area_2D'])
        s_subset.plot(kind='scatter', x='Volume',y='Area_2D',ax=ax,label='Separation',c='k')
        ax.plot(s_subset['Volume'], i +s*s_subset['Volume'],'k')
        #ax.set_ylim(3000,7000)    
#        ax.text(1125,5000,'R$_{sep}$$^2$=%1.4f' % r )
#        ax.text(1125,4500,'m$_{sep}$=%1.4f' % s )
        
        s,i,r,p,stderr = linregress(r_subset['Volume'], r_subset['Area_2D'])
        r_subset.plot(kind='scatter', x='Volume',y='Area_2D',ax=ax,label='Reattachment',marker='x',c='green')
        ax.plot(r_subset['Volume'], i +s*r_subset['Volume'],'green',ls=':')
        ax.set_title(r_site[0:-2])
#        ax.text(7250,4000,'R$_{reatt}$$^2$=%1.4f' % r )
#        ax.text(7250,3519,'m$_{sep}$=%1.4f' % s )
        ax.set_autoscale_on(False)
        ax.set_xlabel('Volume m$^3$')
        ax.set_ylabel('Area m$^2$')
        plt.tight_layout()
        plt.savefig(out_root + os.sep + r_site[0:-2] +'_area_vol.png')
        

    
    