# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 10:29:39 2018

@author: dan
"""

from osgeo import gdal_array,gdal
from rasterstats import zonal_stats
import rasterio
from affine import Affine

import matplotlib.pyplot as plt
import pandas as pd

from glob import glob
import numpy as np
import os

#Input data dictionaries
from sandbar_sd_coeff import sd_coeff

def elev_lu(siteCode):
    '''
    Function to find 8k and 25k elevations
    Inputs: 
        siteCode = string site code
    Outputs:
        low = 8k elevation in meters
        high = 25k elevation in meters
    '''
    df = pd.DataFrame.from_dict(sd_coeff)
    df = df.set_index('SiteCode')
    i = df.loc[siteCode]['int']
    lin_coef =  df.loc[siteCode]['coflin']
    sqd_coef =  df.loc[siteCode]['cofsqd']
    
    low = i + lin_coef*8000 + sqd_coef*8000**2
    high = i + lin_coef*25000 + sqd_coef*25000**2
    return low, high


def get_date_list(files):
    '''
    Function to parse date from input tif
    Inputs:
        files = list of files returned from a glob.glob search
    Outputs:
        survey_dates = list of survey dates fomratted for python
    '''
    survey_dates =[x.split('\\')[-1].split('_')[1] for x in files]
    from datetime import datetime
    return [datetime.strptime(a, '%Y%m%d').strftime('%m/%d/%Y') for a in survey_dates]


def get_surfaces(files,out_root,site,reatt=False,sep=False):
    '''
    Function to calulate max and min surface values for a set of rasters
    inputs:
        files = list of rasters to use in min and max suface calculations
        out_root = desired output root for output surface files
        site = string site code to use in output surface filexs 
        reatt (optional) = boolean, used to flag for reattachment bars at two bar sites
        sep (optional) = boolean, used to flag for separation bars at two bar sites
    '''
    if reatt ==True:
        site = site + '_r'
    elif sep == True:
        site = site + '_s'
    else:
        pass
    
    for raster in files:
        data = gdal_array.LoadFile(raster)        
        if raster == files[0]:
            ds = gdal.Open(raster)
            output = data
            gt = ds.GetGeoTransform()
            del ds
        else:
            output=np.dstack((output,data))

    max_surf = np.max(output,axis=2)
    min_surf = np.min(np.ma.masked_equal(output,-9999), axis=2)
    
    
    max_index = output.argmax(axis=2)
    max_index[max_surf==-9999]=-9999
    
    
    min_index = np.ma.masked_equal(output,-9999).argmin(axis=2).astype(float)
    min_index[max_surf==-9999]=-9999
    

    return max_index, min_index, max_surf, min_surf,gt


def eddy_metrics_calculator(max_surf, min_surf, gt, shps,site,survey_dates,raster_out=False,reatt=False,sep=False):
    '''
    Function to calculate eddy metrics between max and min surfaces
    Inputs:
        max_surf: numpy ndarray containing max surface values
            Notes:
                nodata = -9999
        min_surf: masked array containg min surface values
        gt = geotransfrom for either the max of min surfaces
        shps = list containg path to eddy computational boundary shape file
            Notes:
                list is derived from glob.glob search
        site = string sitecode parsed from input rasters
        raster_out (optional) = flag to output intermediate processing rasters for manual caluations
        reatt (optional)= boolean, true if processing the reattchement bar at a two bar site.
        sep (optional)= boolean, true if processing the separation bar at a two bar site.
    '''
    siteCode = site[1:]
    #convert     
    affine = Affine.from_gdal(*gt)
    eddy = shps[0]
    arrays = zonal_stats(eddy,max_surf,affine=affine,nodata=-9999,stats=['count'], raster_out=True)
    eddy_data = arrays[0]['mini_raster_array']
    mini_affine = arrays[0]['mini_raster_affine']

    if siteCode == '006R':
        siteCode = 'M' + siteCode
    else:
        pass

    #get 8k and 25k elevations
    low, high = elev_lu(siteCode)
    
    #get min surface data for low elevation bin volume calculations
    arrays2 = zonal_stats(eddy,min_surf.filled(-9999),affine=affine,nodata=-9999,stats=['count'], raster_out=True)
    eddy_min_data = arrays2[0]['mini_raster_array']
    
    
    # Low elevation Data
    le_data = np.ma.masked_greater(eddy_data, low,copy=True)
    eddy_min_masked = np.ma.masked_where(np.ma.getmask(le_data), eddy_min_data)    
    le_dod = le_data-eddy_min_masked 
    le_max_vol = np.ma.sum(np.ma.sum(le_dod, axis=1),axis=0)*0.25**2

    
    #FZ Data
    fz_data = np.ma.masked_where(np.ma.masked_where(eddy_data<=low,eddy_data)>high,np.ma.masked_where(eddy_data<=low,eddy_data))
    eddy_fz_masked = np.ma.masked_where(np.ma.getmask(fz_data), eddy_min_data)
    fz_dod = fz_data - eddy_fz_masked
    fz_max_vol = np.ma.sum(np.ma.sum(fz_dod, axis=1),axis=0)*0.25**2
    
    #he_data
    he_data = np.ma.masked_where(eddy_data<=high,eddy_data)
    eddy_he_masked = np.ma.masked_where(np.ma.getmask(he_data), eddy_min_data)
    he_dod = he_data - eddy_he_masked
    he_max_vol = np.ma.sum(np.ma.sum(he_dod, axis=1),axis=0)*0.25**2

    
#    fig, axes = plt.subplots(ncols=3)
#    
#    axes_list = [item for item in axes] 
#    
#    axes_list[0].hist(fz_dod.compressed())
#    axes_list[1].hist(he_dod.compressed())
    
    arrays3 = zonal_stats(eddy,min_index,affine=affine,nodata=-9999,stats=['count'], raster_out=True)
    eddy_min_index = arrays3[0]['mini_raster_array']
    eddy_fz_index = np.ma.masked_where(np.ma.getmask(fz_data), eddy_min_index)
    eddy_he_index = np.ma.masked_where(np.ma.getmask(he_data), eddy_min_index)
                                                                                

    if reatt == True:
        siteCode = siteCode + '_r'

    elif sep == True:
        siteCode = siteCode + '_s'
    else:             
        pass

    
    fz_df = histogram_history(fz_dod,eddy_fz_index,survey_dates)
    he_df = histogram_history(he_dod,eddy_he_index,survey_dates)

    try:
        cmap, bounds, norm,kw = plotting_utils(list(fz_df.Survey_Date.unique()))
        fig, ax= plt.subplots(figsize=(12,12))
        
        fz_df.groupby('Survey_Date').DoD.apply(hist).sort_index(level=0).unstack(0).plot.bar(ax=ax,colormap=cmap, legend=False,**kw)
        bars = ax.patches
        patterns =('--', '+', 'x','/','//','O','o','\\','\\\\','--', '+', 'x','/','//','O','o','\\','\\\\','--','+', 'x','/','//','--', '+', 'x','--', '+', 'x','/','//','O','o','\\','\\\\','--', '+', 'x','/','//','O','o','\\','\\\\','--','+', 'x','/','//','--', '+', 'x')
        hatches = [p for p in patterns for i in range(len(fz_df.groupby('Survey_Date').DoD.apply(hist).sort_index(level=0).unstack(0)))]
        for bar, hatch in zip(bars, hatches):
            bar.set_hatch(hatch)
        ax.legend(bbox_to_anchor=(0., 1.08, 1., .102), loc=3,fontsize='large',ncol=4)
        ax.set_title(siteCode + ' FZ_DoD: 8k Elev= ' + str(low)+', 25k Elev= ' + str(high))
        ax.set_ylabel('Freqency')
        ax.set_xlabel('DoD Elevation (m)')
        fig.tight_layout()
        fig.subplots_adjust(top=0.695,bottom=0.137)
        fig.savefig(out_root + os.sep + 'DoD_Plots'+ os.sep + siteCode + '_FZ_DoD_Min_Surface_History.png')
    except:
        pass
    try:
        cmap, bounds, norm,kw = plotting_utils(list(he_df.Survey_Date.unique()))
        
        fig, ax= plt.subplots(figsize=(12,12))
        
        he_df.groupby('Survey_Date').DoD.apply(hist).sort_index(level=0).unstack(0).plot.bar(ax=ax,colormap=cmap, legend=False,**kw)
        bars = ax.patches
        hatches = [p for p in patterns for i in range(len(he_df.groupby('Survey_Date').DoD.apply(hist).sort_index(level=0).unstack(0)))]
        for bar, hatch in zip(bars, hatches):
            bar.set_hatch(hatch)
        ax.legend(bbox_to_anchor=(0., 1.08, 1., .102), loc=3,fontsize='large',ncol=4)
        ax.set_title(siteCode + ' HE_DoD: 8k Elev= ' + str(low)+', 25k Elev= ' + str(high))
        ax.set_ylabel('Freqency')
        ax.set_xlabel('DoD Elevation (m)')
        fig.tight_layout()
        fig.subplots_adjust(top=0.695,bottom=0.137)
        fig.savefig(out_root + os.sep + 'DoD_Plots'+ os.sep + siteCode + '_HE_DoD_Min_Surface_History.png')    
    except:
        pass
    
    plt.close('all')
def hist(x):
    h, e = np.histogram(x.dropna(), bins=20,range=(0, 10))
    #e = e.astype(int)
    return pd.Series(h, zip(e[:-1], e[1:]))
   
def histogram_history(dod_data,index_data,survey_dates):
    df = pd.DataFrame({'DoD':dod_data.compressed(),'Date_Index':index_data.compressed()})
    tmp = pd.DataFrame(np.array(survey_dates), columns = ['Survey_Date'])
    tmp['Survey_Date'] = pd.to_datetime(tmp['Survey_Date'])
    df = pd.merge(df, tmp, left_on='Date_Index', right_index=True,how='left')
    df = df.drop(['Date_Index'],axis=1)
    return df       
def plotting_utils(survey_dates):
    '''
    Function to create color ramp for optimized for the amount of surveys at a site
    Inputs: list of survey dates
    Outputs:
        cmap = customized matplotlib.colors.LinearSegmentedColormap
        bounds = array containing the number of ticks
        norm = customized matplotlib.colors.BoundaryNorm used in controuf pl;ot
    '''
    import matplotlib as mpl
    # define the colormap
    cmap = plt.cm.gist_rainbow
    # extract all colors from the .jet map
    cmaplist = [cmap(i) for i in range(cmap.N)]
    # force the first color entry to be grey
    #cmaplist[0] = (.5,.5,.5,1.0)
    # create the new map
    cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N)

    # define the bins and normalize
    bounds = np.linspace(0,len(survey_dates),len(survey_dates)+1)
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)    
    kw = dict(stacked=True, width=1, rot=45)
    return cmap, bounds, norm,kw

if __name__ =='__main__':
    
    in_root = r"C:\workspace\sandbar-results-aggregation\Max_Min_Surface\input"
    out_root =r"C:\workspace\sandbar-results-aggregation\Max_Min_Surface\output"
    
    single_eddy_sites = ['0003L', '0009L', '0016L', '0022R', '0030R', '0032R', '0043L', '0047R', '0051L', '0055R', '0062R', '0068R', '0070R', '0081L', '0087L', '0091R', '0093L', '0104R', '0119R', '0122R', '0123L', '0137L', '0139R', '0145L', '0172L', '0183R', '0194L', '0213L', '0220R', '0225R', 'M006R']
    
    for i in single_eddy_sites:
        site = i
        files = glob(in_root + os.sep + site + os.sep + '*' + os.sep+ '*.tif')
        shps = glob(in_root + os.sep + site + os.sep + '*_ed.shp')
        survey_dates = get_date_list(files)
        max_index, min_index, max_surf, min_surf, gt = get_surfaces(files,out_root,site)
        eddy_metrics_calculator(max_surf, min_surf, gt, shps,site,survey_dates,raster_out=False,reatt=False,sep=False)

    no_bath_sites = ['0008L', '0024L', '0029L', '0033L', '0056R', '0084R', '0167L']

    for i in no_bath_sites:
        
        site = i
        files = glob(in_root + os.sep + site + os.sep + '*' + os.sep+ '*.tif')
        shps = glob(in_root + os.sep + site + os.sep + 'RM[0-9][0-9][0-9].shp')

        max_index, min_index, max_surf, min_surf, gt = get_surfaces(files,out_root,site)
            
        survey_dates = get_date_list(files)
        
        max_index, min_index, max_surf, min_surf, gt = get_surfaces(files,out_root,site)
        eddy_metrics_calculator(max_surf, min_surf, gt, shps,site,survey_dates,raster_out=False,reatt=False,sep=False)
        
    two_bar_sites = ['0035L', '0041R', '0044L', '0045L', '0050R', '0063L', '0065R', '0202R']
     
    #reatt bars
    for i in two_bar_sites:
        site=i
        files = glob(in_root + os.sep + site + os.sep + '*' + os.sep+ '*.tif')
        shps = glob(in_root + os.sep + site + os.sep + 'RM[0-9][0-9][0-9]_ed_r.shp')
        max_index, min_index, max_surf, min_surf, gt = get_surfaces(files,out_root,site,reatt=True)
        survey_dates = get_date_list(files)
        
        eddy_metrics_calculator(max_surf, min_surf, gt, shps,site,survey_dates,raster_out=False,reatt=True,sep=False)
    
    #sep bars 
    for i in two_bar_sites:
        site=i
        files = glob(in_root + os.sep + site + os.sep + '*' + os.sep+ '*.tif')
        shps = glob(in_root + os.sep + site + os.sep + 'RM[0-9][0-9][0-9]_ed_s.shp')
        max_index, min_index, max_surf, min_surf, gt = get_surfaces(files,out_root,site,sep=True)
        survey_dates = get_date_list(files)
        eddy_metrics_calculator(max_surf, min_surf, gt, shps,site,survey_dates,raster_out=False,reatt=False,sep=True)