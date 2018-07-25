# -*- coding: utf-8 -*-
"""
Created on Thu May 18 14:49:57 2017

@author: dan
"""

from osgeo import ogr
from glob import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from scipy.stats import probplot
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import FormatStrFormatter
import platform
import os

def get_area(ind,files):
    shp = files[ind]
    ds = ogr.Open(shp)
    layer = ds.GetLayer()
    for feat in layer:
        geom = feat.GetGeometryRef()
        area = geom.GetArea()
    del ds
    return area


if __name__ =='__main__':
    if platform.system() == 'Darwin':
        sandbar_root = '/~/git_clones/sandbar-results-aggregation/Time_Series_Analysis/input'
        time_root = '/~/git_clones/sandbar-results-aggregation/Time_Series_Analysis'
        out_root = time_root + os.sep + 'Output'
    elif platform.system() == 'Windows':
        sandbar_root = r'C:\workspace\sandbar-results-aggregation\Time_Series_Analysis\input'
        time_root = r'C:\workspace\sandbar-results-aggregation\Time_Series_Analysis'
        out_root = time_root + os.sep + r'Output'

    files = glob(time_root + os.sep + "input\comp_boundaries\*.shp")
    
    new_sitecode =['024l','029l','033l','035l',  '041r',  '045l', '055r','056r']
    ind_new =     [18,     20,    28,   (33,34), (37,38),(50,51),  73,   74]
    
    
    new_bt = ['u','u','r','c','c','c','c','r','u']
    
    
    lt_sitecode = ['003l','008l','016l','022r','030r','032r','043l', '044l',  '047r', '050r',   '051l']
    ind_lt =      [6,      7,     14,    17,    24,     27,    41,   (45,46),   54,   (63,64),    67]
    area_new = []
    
    
    lt_bt = ['r','s','s','r','r','u','r','s','r','c','r']
    area_old = []
    
    for thing in ind_lt:
        if hasattr(thing, '__iter__'):
            area1 = get_area(thing[0],files)
            area2 = get_area(thing[1],files)
            area_old.append(area1+area2)
        else:
            area1 = get_area(int(thing),files)
            area_old.append(area1)
    del area1,area2  
        
    for thing in ind_new:
        if hasattr(thing, '__iter__'):
            area1 = get_area(thing[0],files)
            area2 = get_area(thing[1],files)
            area_new.append(area1+area2)
        else:
            area1 = get_area(int(thing),files)
            area_new.append(area1)
    del area1,area2       
    
    print'new ', np.max(area_new)
    print 'old ', np.max(area_old)
    
    combined = area_old + area_new
    pd.DataFrame(area_new).describe()
    
    df2 = pd.DataFrame(columns=['SiteCode','Area'])
    df2['SiteCode'] = lt_sitecode+new_sitecode
    df2['Area'] = area_old+area_new
    
    
    df = pd.DataFrame(combined).merge(pd.DataFrame(area_old),how='left',left_index=True, right_index=True)
    df = df.rename(columns={'0_x':'All Sites N=19','0_y':'Long Term Sites: N=11'})
    df = df.merge(pd.DataFrame(area_new,columns=['Additional Sites N=8']), how='left',left_index=True, right_index=True)
    
    df_all = df['All Sites N=19'].to_frame().merge(pd.DataFrame(lt_sitecode+new_sitecode),left_index=True, right_index=True)
    df_old = pd.DataFrame({'Area':area_old,'SiteCode':lt_sitecode})
    df_new = pd.DataFrame({'Area':area_new,'SiteCode':new_sitecode})
    
    fontP = FontProperties()
    fontP.set_size('x-small')
    
    
    
    colors = ['#1b9e77','#d95f02','#7570b3','#e7298a','#66a61e','#e6ab02']
    g_1a = np.array(['145l','022r','213l','084r','030r','081l','137l','119r','122r'])
    g_1b = np.array(['123l','172l','041r','044l','183r','220r','050r','065r','047r','045l'])  #'009l' dropped because it was added in 2008,-'045l' dropped 045L because sep and reatt bar wasnt surveyed each time
    g_1c = np.array(['194l','068r','051l','055r']) # '070r' dropped because it was added in 2008
    g_2 = np.array(['008l','024l','029l','032r','056r'])# ,'167l' removed because it is a technical outlier
    g_3 = np.array(['043l','087l','093l','139r','225r','104r'])
    g_4 = np.array(['016l','033l','035l','091r','202r'])
    
    
    fig, (ax,ax1,ax2) = plt.subplots(figsize=(7.5,5),ncols=3,sharey=True)
    
    #Make box plot from all of the data, dictionary is returned for future formatting
    r = df['All Sites N=19'].plot.box(ax=ax2, showfliers=False,return_type='dict')
    
    #plot Group 1a data
    x = np.random.normal(1,0.04,len(df_all[df_all[0].isin(g_1a)]['All Sites N=19']))
    ax2.plot(x,df_all[df_all[0].isin(g_1a)]['All Sites N=19'],marker='*',lw=0,label='Group 1a: N=2',markersize=8,c=colors[0],alpha=0.4)
    
    #plot group 1b data
    x = np.random.normal(1,0.04,len(df_all[df_all[0].isin(g_1b)]['All Sites N=19']))
    ax2.plot(x,df_all[df_all[0].isin(g_1b)]['All Sites N=19'],marker='d',lw=0,label='Group 1b: N=5',markersize=8,alpha=0.4,c=colors[1])
    
    #plot groub 1c data
    x = np.random.normal(1,0.04,len(df_all[df_all[0].isin(g_1c)]['All Sites N=19']))
    ax2.plot(x,df_all[df_all[0].isin(g_1c)]['All Sites N=19'],marker='o',lw=0,label='Group 1c: N=2',markersize=8,alpha=0.4,c=colors[2])
    
    #plot groub 2 data
    x = np.random.normal(1,0.04,len(df_all[df_all[0].isin(g_2)]['All Sites N=19']))
    ax2.plot(x,df_all[df_all[0].isin(g_2)]['All Sites N=19'],marker='H',lw=0,label='Group 2: N=5',markersize=8,alpha=0.4,c=colors[3])
    
    #plot groub 3 data
    x = np.random.normal(1,0.04,len(df_all[df_all[0].isin(g_3)]['All Sites N=19']))
    ax2.plot(x,df_all[df_all[0].isin(g_3)]['All Sites N=19'],marker='8',lw=0,label='Group 3: N=1',markersize=8,alpha=0.4,c=colors[4])
    
    #plot groub 4 data
    x = np.random.normal(1,0.04,len(df_all[df_all[0].isin(g_4)]['All Sites N=19']))
    ax2.plot(x,df_all[df_all[0].isin(g_4)]['All Sites N=19'],marker='P',lw=0,label='Group 4: N=3',markersize=8,alpha=0.4,c=colors[5])
    legend = ax2.legend(loc=9,title='C',prop=fontP,numpoints=1)
    ax2.set_ylim(0,60000)
    
    #=======================================================================================================================
    r1 = df['Long Term Sites: N=11'].plot.box(ax=ax,sharey=ax, showfliers=False,return_type='dict')
    
    #plot Group 1a data
    x = np.random.normal(1,0.04,len(df_old[df_old['SiteCode'].isin(g_1a)]['Area']))
    ax.plot(x,df_old[df_old['SiteCode'].isin(g_1a)]['Area'],marker='*',lw=0,label='Group 1a: N=2',markersize=8,c=colors[0],alpha=0.4)
    
    #plot Group 1b data
    x = np.random.normal(1,0.04,len(df_old[df_old['SiteCode'].isin(g_1b)]['Area']))
    ax.plot(x,df_old[df_old['SiteCode'].isin(g_1b)]['Area'],marker='d',lw=0,label='Group 1b: N=3',markersize=8,alpha=0.4,c=colors[1])
    
    #plot Groub 1c data
    x = np.random.normal(1,0.04,len(df_old[df_old['SiteCode'].isin(g_1c)]['Area']))
    ax.plot(x,df_old[df_old['SiteCode'].isin(g_1c)]['Area'],marker='o',lw=0,label='Group 1c: N=1',markersize=8,alpha=0.4,c=colors[2])
    
    #plot Groub 2 data
    x = np.random.normal(1,0.04,len(df_old[df_old['SiteCode'].isin(g_2)]['Area']))
    ax.plot(x,df_old[df_old['SiteCode'].isin(g_2)]['Area'],marker='H',lw=0,label='Group 2: N=2',markersize=8,alpha=0.4,c=colors[3])
    
    #plot Groub 3 data
    x = np.random.normal(1,0.04,len(df_old[df_old['SiteCode'].isin(g_3)]['Area']))
    ax.plot(x,df_old[df_old['SiteCode'].isin(g_3)]['Area'],marker='8',lw=0,label='Group 3: N=1',markersize=8,alpha=0.4,c=colors[4])
    
    #plot Groub 4 data
    x = np.random.normal(1,0.04,len(df_old[df_old['SiteCode'].isin(g_4)]['Area']))
    ax.plot(x,df_old[df_old['SiteCode'].isin(g_4)]['Area'],marker='P',lw=0,label='Group 4: N=1',markersize=8,alpha=0.4,c=colors[5])
    
    legend1 = ax.legend(loc=9,title='A',prop=fontP,numpoints=1)
    
    
    #=======================================================================================================================
    r2 = df['Additional Sites N=8'].plot.box(ax=ax1,sharey=ax1, showfliers=False,return_type='dict')
    
    ##plot Group 1a data
    #x = np.random.normal(1,0.04,len(df_new[df_new['SiteCode'].isin(g_1a)]['Area']))
    #ax.plot(x,df_new[df_new['SiteCode'].isin(g_1a)],marker='*',lw=0,label='Group 1a: N=0',markersize=8,c=colors[0],alpha=0.4)
    #
    #plot Group 1b data
    x = np.random.normal(1,0.04,len(df_new[df_new['SiteCode'].isin(g_1b)]['Area']))
    ax1.plot(x,df_new[df_new['SiteCode'].isin(g_1b)]['Area'],marker='d',lw=0,label='Group 1b: N=2',markersize=8,alpha=0.4,c=colors[1])
    
    #plot Groub 1c data
    x = np.random.normal(1,0.04,len(df_new[df_new['SiteCode'].isin(g_1c)]['Area']))
    ax1.plot(x,df_new[df_new['SiteCode'].isin(g_1c)]['Area'],marker='o',lw=0,label='Group 1c: N=1',markersize=8,alpha=0.4,c=colors[2])
    
    #plot Groub 2 data
    x = np.random.normal(1,0.04,len(df_new[df_new['SiteCode'].isin(g_2)]['Area']))
    ax1.plot(x,df_new[df_new['SiteCode'].isin(g_2)]['Area'],marker='H',lw=0,label='Group 2: N=3',markersize=8,alpha=0.4,c=colors[3])
    
    #plot Groub 3 data
    #x = np.random.normal(1,0.04,len(df_new[df_new['SiteCode'].isin(g_3)]['Area']))
    #ax.plot(x,df_new[df_new['SiteCode'].isin(g_3)]['Area'],marker='8',lw=0,label='Group 3: N=0',markersize=8,alpha=0.4,c=colors[4])
    
    #plot Groub 4 data
    x = np.random.normal(1,0.04,len(df_new[df_new['SiteCode'].isin(g_4)]['Area']))
    ax1.plot(x,df_new[df_new['SiteCode'].isin(g_4)]['Area'],marker='P',lw=0,label='Group 4: N=2',markersize=8,alpha=0.4,c=colors[5])
    legend2 = ax1.legend(loc=9,title='B',prop=fontP,numpoints=1)
    
    
    plt.setp(legend.get_title(),fontsize='large')
    plt.setp(legend1.get_title(),fontsize='large')
    plt.setp(legend2.get_title(),fontsize='large')
    
    plt.setp(r['boxes'], color='black',lw=1.5) 
    plt.setp(r['whiskers'], color='black',lw=1.5) 
    plt.setp(r['caps'], color='black',lw=1.5)
    plt.setp(r['medians'], color='black',lw=1.5)
    
    plt.setp(r1['boxes'], color='black',lw=1.5) 
    plt.setp(r1['whiskers'], color='black',lw=1.5) 
    plt.setp(r1['caps'], color='black',lw=1.5)
    plt.setp(r1['medians'], color='black',lw=1.5)
    
    plt.setp(r2['boxes'], color='black',lw=1.5) 
    plt.setp(r2['whiskers'], color='black',lw=1.5) 
    plt.setp(r2['caps'], color='black',lw=1.5)
    plt.setp(r2['medians'], color='black',lw=1.5)
     
    ax.set_ylabel('TOTAL EDDY AREA, IN METERS SQUARED')
    ax.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.tight_layout()
    plt.savefig(out_root + os.sep + "grouped_mc_area_boxplot.png",dpi=600)
    
    
    
    
    #################################################################################################
    #################################################################################################
#    from scipy.stats.mstats import normaltest, skewtest
#    
#    print 'old ', normaltest(area_old)
#    print 'combined ', normaltest(combined)
#    
#    print 'old ', skewtest(area_old)
#    print 'combined ', skewtest(combined)
#    
#    a = probplot(area_old,dist='norm', plot=None)
#    b= probplot(combined,dist='norm', plot=None)
#    colors = {'r':'red','s':'blue', 'u':'green'}
#    markers = {'r':'*','s':'x', 'u':'o'}
#    
#    old_df = pd.DataFrame(area_old, columns=['Long Term Sites: N=12'])
#    old_df['Bar_Type'] = lt_bt
#    old_df = old_df.sort_values(by='Long Term Sites: N=12')
#    old_df['quart']=a[0][0]
#    
#    combined_df = pd.DataFrame(combined, columns=['ALL SITES N=22'])
#    combined_df['Bar_Type'] = lt_bt + new_bt
#    combined_df = combined_df.sort_values(by='ALL SITES N=22')
#    combined_df['quart']=b[0][0]
#    
#    
#    undif = plt.Line2D([0,0],[0,1], color='green',marker='o',linestyle=' ')
#    reatt = plt.Line2D([0,0],[0,1], color='red',marker='*',linestyle=' ')
#    sep = plt.Line2D([0,0],[0,1], color='blue',marker='x',linestyle=' ')
#    
#    
#    
#    fig,(ax,ax1) = plt.subplots(figsize=(7.5,5),ncols=2,sharey=True)
#    
#    #Plot each data point seperatly with different markers and colors
#    for i, thing in old_df.iterrows():
#        ax.scatter(thing['quart'],thing['Long Term Sites: N=12'],c=colors[thing['Bar_Type']],marker=markers[thing['Bar_Type']],zorder=10,s=50)
#    del i, thing
#    
#    for i , thing in combined_df.iterrows():
#        ax1.scatter(thing['quart'],thing['ALL SITES N=22'],c=colors[thing['Bar_Type']],marker=markers[thing['Bar_Type']],zorder=10,s=50)
#    del i, thing
#    
#    #Plot trend line
#    ax.plot(a[0][0],a[0][1],"w",a[0][0],a[0][0]*a[1][0] + a[1][1],'black')
#    ax.text(0.4,4600,"$R^2=%1.4f$" % a[1][-1] )
#    ax1.plot(b[0][0],b[0][1],"w",b[0][0],b[0][0]*b[1][0] + b[1][1],'black')
#    ax1.text(0.70,4600,"$R^2=%1.4f$" % b[1][-1] )
#    
#    
#    ax.set_title('LONG TERM SITES N=12')
#    ax1.set_title('ALL SITES N=22')
#    ax1.set_ylabel('')
#    ax.set_ylabel('TOTAL EDDY AREA, IN METERS SQUARED')
#    ax.set_ylim(0,35000)
#    ax.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x), ',')))
#    
#    legend = ax.legend([reatt,sep,undif],["Reattachment: N=7","Separation: N=6", "Undifferentiated: N=1"],loc=2,title='Bar Type',prop=fontP)
#    legend2 = ax1.legend([reatt,sep,undif],["Reattachment: N=12","Separation: N=8", "Undifferentiated: N=4"],loc=2,title='Bar Type',prop=fontP)
#    
#    plt.setp(legend.get_title(),fontsize='x-small')
#    plt.setp(legend2.get_title(),fontsize='x-small')
#    ax.set_xlabel('QUANTILES')
#    ax1.set_xlabel('QUANTILES')
#    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
#    ax1.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
#    plt.tight_layout()
#    plt.savefig(r"C:\workspace\Time_Series\Output\Joes_Figs\mc_area_probability_plot.png",dpi=600)
    


