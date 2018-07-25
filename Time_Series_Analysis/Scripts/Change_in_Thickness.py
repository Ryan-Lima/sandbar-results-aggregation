# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 16:01:14 2017

@author: dan
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import platform
import os

def thick_calc(df):
    
    df.loc[:,'Thickness'] = df.loc[:,'Volume']/df.loc[:,'Max_Area']
    df.loc[:,'Norm_Thickness'] = df.loc[:,'Volume']/df.loc[:,'Area_2D'] * df.loc[:,'Max_Area'] /df.loc[:,'MaxVol']
    df = df[['Site','TripDate','Thickness','Norm_Thickness']]
    return df


def all_data(mc_t,gc_t,b,e):
    
    mc_a = mc_t[mc_t['Site'].isin(set(lu_sites['Sediment Deficit Sites']))]
    gc_a = gc_t[gc_t['Site'].isin(set(lu_sites['Sediment Deficit Sites']))]
    
    mc_a_b = mc_a[(mc_a['TripDate']==b)]
    mc_a_e = mc_a[(mc_a['TripDate']==e)]
    
    gc_a_b = gc_a[(gc_a['TripDate']==b)]
    gc_a_e = gc_a[(gc_a['TripDate']==e)]

    mc_df = mc_a_b[['Thickness','Norm_Thickness','Site']].merge(mc_a_e[['Thickness','Norm_Thickness','Site']],left_on='Site',right_on='Site',how='left')
    mc_df.loc[:,'Delta_Thick'] = mc_df.loc[:,'Thickness_y'] - mc_df.loc[:,'Thickness_x'] 
    mc_df.loc[:,'Delta_N_Thick'] = mc_df.loc[:,'Norm_Thickness_y'] - mc_df.loc[:,'Norm_Thickness_x']
    mc_df = mc_df[['Site','Delta_Thick','Delta_N_Thick']]
    
    gc_df = gc_a_b[['Thickness','Norm_Thickness','Site']].merge(gc_a_e[['Thickness','Norm_Thickness','Site']],left_on='Site',right_on='Site',how='left')
    gc_df.loc[:,'Delta_Thick'] = gc_df.loc[:,'Thickness_y'] - gc_df.loc[:,'Thickness_x'] 
    gc_df.loc[:,'Delta_N_Thick'] = gc_df.loc[:,'Norm_Thickness_y'] - gc_df.loc[:,'Norm_Thickness_x']
    gc_df = gc_df[['Site','Delta_Thick','Delta_N_Thick']]
    return mc_df, gc_df

def enrich_data(mc_t,gc_t,b,e):
    mc_a = mc_t
    gc_a = gc_t
    
    mc_a_b = mc_a[(mc_a['TripDate']==b)]
    mc_a_e = mc_a[(mc_a['TripDate']==e)]
    
    gc_a_b = gc_a[(gc_a['TripDate']==b)]
    gc_a_e = gc_a[(gc_a['TripDate']==e)]

    mc_df = mc_a_b[['Thickness','Norm_Thickness','Site']].merge(mc_a_e[['Thickness','Norm_Thickness','Site']],left_on='Site',right_on='Site',how='left')
    mc_df.loc[:,'Delta_Thick'] = mc_df.loc[:,'Thickness_y'] - mc_df.loc[:,'Thickness_x'] 
    mc_df.loc[:,'Delta_N_Thick'] = mc_df.loc[:,'Norm_Thickness_y'] - mc_df.loc[:,'Norm_Thickness_x']
    mc_df = mc_df[['Site','Delta_Thick','Delta_N_Thick']]
    
    gc_df = gc_a_b[['Thickness','Norm_Thickness','Site']].merge(gc_a_e[['Thickness','Norm_Thickness','Site']],left_on='Site',right_on='Site',how='left')
    gc_df.loc[:,'Delta_Thick'] = gc_df.loc[:,'Thickness_y'] - gc_df.loc[:,'Thickness_x'] 
    gc_df.loc[:,'Delta_N_Thick'] = gc_df.loc[:,'Norm_Thickness_y'] - gc_df.loc[:,'Norm_Thickness_x']
    gc_df = gc_df[['Site','Delta_Thick','Delta_N_Thick']]
    return mc_df, gc_df

def calc_averages(mc_t,gc_t):
    pvt_mc = pd.pivot_table(mc_t, index=['TripDate'],values=['Thickness'],aggfunc=np.nanmean).reset_index()
    pvt_gc = pd.pivot_table(gc_t, index=['TripDate'],values=['Thickness'],aggfunc=np.nanmean).reset_index()
    pvt_mc = pvt_mc[(pvt_mc['TripDate'] == '1990-06-10') | (pvt_mc['TripDate'] == '2003-09-20') | (pvt_mc['TripDate'] == '2016-10-01')]
    pvt_gc = pvt_gc[(pvt_gc['TripDate'] == '1990-06-10') | (pvt_gc['TripDate'] == '2003-09-20') | (pvt_gc['TripDate'] == '2016-10-01')]
    pvt_mc = pvt_mc.rename(columns={'Thickness':'Marble Canyon Average Thickness'})
    pvt_gc = pvt_gc.rename(columns={'Thickness':'Grand Canyon Average Thickness'})
    merge = pvt_mc.merge(pvt_gc, left_on='TripDate', right_on='TripDate',how='left')
    return merge
    
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
    
    data['TripDate'] = pd.to_datetime(data['TripDate'], format='%Y-%m-%d')
    
    
    subset = data[(data.Time_Series == 'long') & (data.Site !='m006r')& (data.Site !='062r')& (data.Site !='068r') & 
                  (data.Site !='167l') & (data.SitePart == 'Eddy') & (data.Plane_Height != 'eddyminto8k') & (data.Bar_type != 'Total')]   
    subset = pd.pivot_table(subset,index=['Site','SurveyDate','SitePart','TripDate','SiteRange','Segment','Bar_type','Time_Series','Period'],values=['Area_2D','Area_3D','Volume','Errors','MaxVol'],aggfunc=np.sum).reset_index()
    
    subset1 = data[(data.Time_Series == 'long') & (data.Site !='m006r')& (data.Site !='062r')& (data.Site !='068r') & 
                  (data.Site !='167l') & (data.SitePart == 'Eddy') & (data.Plane_Height != 'eddyminto8k') & (data.Bar_type != 'Total')]   
    
    subset1 = pd.pivot_table(subset1,index=['Site','SurveyDate','SitePart','TripDate','SiteRange','Segment','Bar_type','Time_Series','Period'],values=['Max_Area'],aggfunc=np.average).reset_index()
    subset = subset.merge(subset1, on=['Site','SurveyDate','SitePart','TripDate','SiteRange','Segment','Bar_type','Time_Series','Period'],how='left')
    del subset1
    
    mc_query = 'Segment == ["1_UMC","2_LMC"]'
    gc_query = 'Segment != ["1_UMC","2_LMC"]'
    
    mc = subset.query(mc_query)
    gc = subset.query(gc_query)
    
    mc_t = thick_calc(mc)
    gc_t = thick_calc(gc)
    
    mc_df_a,gc_df_a = all_data(mc_t,gc_t,'1990-06-10','2016-10-01')
    mc_df_d,gc_df_d = all_data(mc_t,gc_t,'1990-06-10','2003-09-20')
    mc_df_e,gc_df_e = enrich_data(mc_t,gc_t,'2003-09-20','2016-10-01')
    
    
    fig, ((ax,ax1,ax2),(ax3,ax4,ax5)) = plt.subplots(ncols=3,nrows=2,figsize=(7.5,6),sharey=True)
    
    #Entire Time Series
    bins=[round(x,1)for x in np.linspace(-1,1,21)]
    counts, division = np.histogram(mc_df_a.loc[:,'Delta_Thick'],bins=bins)
    mc_df_a.loc[:,'Delta_Thick'].hist(ax=ax, bins=division,color='gray',label='Marble Canyon',xrot=0,grid=False,width=0.06)
    ax.xaxis.set_ticks(np.arange(-1, 1.5, 0.5))
    ax.set_title('A. 1990-2016')
    ax.set_ylabel('Number of Sites in \n Marble Canyon')
    
    
    #Deficit
    bins=[round(x,1)for x in np.linspace(-1,0.6,16)]
    counts, division = np.histogram(mc_df_a.loc[:,'Delta_Thick'],bins=bins)
    mc_df_d.loc[:,'Delta_Thick'].hist(ax=ax1, bins=division,color='gray', label='1990-2003',xrot=0,grid=False,width=0.06)
    ax1.xaxis.set_ticks(np.arange(-1, 1.5, 0.5))
    ax1.set_title('B. 1990-2003')
    ax1.set_xlabel('Change in Thickness, in Meters')
    
    #Enrich
    bins=[round(x,1)for x in np.linspace(-1,1,21)]
    counts, division = np.histogram(mc_df_e.loc[:,'Delta_Thick'],bins=bins)
    mc_df_e.loc[:,'Delta_Thick'].hist(ax=ax2, bins=division,color='gray',label='2003-2016',xrot=0,grid=False,width=0.06)
    ax2.xaxis.set_ticks(np.arange(-1, 2, 0.5))
    ax2.set_xlim(-1,1)
    ax2.set_title('C. 2003-2016')
    
    bins = [round(x,1)for x in np.linspace(-1,1.5,24)]
    counts, division = np.histogram(gc_df_a.loc[:,'Delta_Thick'],bins=bins)
    gc_df_a.loc[:,'Delta_Thick'].hist(ax=ax3, bins=division,label='Grand Canyon',color='gray',xrot=0,grid=False,width=0.06)
    ax3.xaxis.set_ticks(np.arange(-1, 2.5 ,0.5))
    ax3.set_xlim(-1,1)
    ax3.set_title('D. 1990-2016')
    ax3.set_ylabel('Number of Sites in \n Grand Canyon')
    
    
    #Deficit
    bins=[round(x,1)for x in np.linspace(-1,1,21)]
    counts, division = np.histogram(gc_df_d.loc[:,'Delta_Thick'],bins=bins)
    gc_df_d.loc[:,'Delta_Thick'].hist(ax=ax4, bins=division,color='gray',xrot=0,grid=False,width=0.06)
    ax4.xaxis.set_ticks(np.arange(-1, 1.5, 0.5))
    ax4.set_title('E. 1990-2003')
    ax4.set_xlabel('Change in Thickness, in Meters')
    
    #Enrich
    bins=[round(x,1)for x in np.linspace(-1,1,21)]
    counts, division = np.histogram(gc_df_e.loc[:,'Delta_Thick'].dropna(),bins=bins)
    a = gc_df_e.loc[:,'Delta_Thick'].hist(ax=ax5, bins=division,color='gray',xrot=0,grid=False,width=0.06)#,hatch='o'
    ax5.xaxis.set_ticks(np.arange(-1,1.5, 0.5))
    ax5.set_title('F. 2003-2016')
    
    
    for t in fig.axes:
        for tick in t.xaxis.get_major_ticks():
            tick.label1.set_horizontalalignment('center')
    
    
    plt.tight_layout()
    plt.savefig(out_root + os.sep + 'Change_in_Thickness.png')
    
    #Data Export section
    
    avg_data = calc_averages(mc_t,gc_t)
    
    #Marble Canyon
    mc_df_a = mc_df_a.rename(columns={'Delta_Thick':'1990-2016 Change in Thickness'})
    mc_df_d = mc_df_d.rename(columns={'Delta_Thick':'1990-2003 Change in Thickness'})
    mc_df_e = mc_df_e.rename(columns={'Delta_Thick':'2003-2016 Change in Thickness'})
    
    gc_df_a = gc_df_a.rename(columns={'Delta_Thick':'1990-2016 Change in Thickness'})
    gc_df_d = gc_df_d.rename(columns={'Delta_Thick':'1990-2003 Change in Thickness'})
    gc_df_e = gc_df_e.rename(columns={'Delta_Thick':'2003-2016 Change in Thickness'})
    
    mc_out = mc_df_e[['Site','2003-2016 Change in Thickness']].merge(mc_df_a[['Site','1990-2016 Change in Thickness']].merge(mc_df_d[['Site','1990-2003 Change in Thickness']],left_on='Site',right_on='Site',how='left'),left_on='Site',right_on='Site',how='left')
    gc_out = gc_df_e[['Site','2003-2016 Change in Thickness']].merge(gc_df_a[['Site','1990-2016 Change in Thickness']].merge(gc_df_d[['Site','1990-2003 Change in Thickness']],left_on='Site',right_on='Site',how='left'),left_on='Site',right_on='Site',how='left')
    
    #Average thickness
    writer = pd.ExcelWriter(out_root + os.sep + "Change_in_Thickness.xlsx",engine='xlsxwriter')
    mc_out.to_excel(writer,sheet_name='Marble Canyon')
    gc_out.to_excel(writer,sheet_name='Grand Canyon')
    avg_data.to_excel(writer, sheet_name='Average_Thickness')
    writer.save()



