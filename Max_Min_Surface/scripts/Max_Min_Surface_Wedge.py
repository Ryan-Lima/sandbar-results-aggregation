# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 14:07:20 2018

@author: dan
"""
#geospatial
from osgeo import gdal_array, gdal, osr
from affine import Affine
from rasterstats import zonal_stats
import rasterio


#operational
import os
import numpy as np
from glob import glob
import pandas as pd


# Plotting
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pyproj
import matplotlib as mpl

#Input data dictionaries
from sandbar_sd_coeff import sd_coeff

def get_lons_data(raster):
    ds = gdal.Open(raster)
    data = ds.GetRasterBand(1).ReadAsArray()
    data[data<=0] = np.nan
    gt = ds.GetGeoTransform()
     
    xres = gt[1]
    yres = gt[5]
    
    # get the edge coordinates and add half the resolution 
    # to go to center coordinates
    xmin = gt[0] + xres * 0.5
    xmax = gt[0] + (xres * ds.RasterXSize) - xres * 0.5
    ymin = gt[3] + (yres * ds.RasterYSize) + yres * 0.5
    ymax = gt[3] - yres * 0.5
    extent = [xmin,xmax,ymin,ymax]
    xx, yy = np.mgrid[xmin:xmax+xres:xres, ymax+yres:ymin:yres]
    
    trans =  pyproj.Proj(init="epsg:26949") 
    glon, glat = trans(xx, yy, inverse=True)
    del ds, xx, yy, extent, xmin, xmax, ymin, ymax, yres, xres
    return glon,glat


def CreateRaster(sed_class,gt,outFile):  
    '''
    Exports data to GTiff Raster
    '''
    proj = osr.SpatialReference()
    proj.ImportFromEPSG(26949)
    sed_class = np.squeeze(sed_class)
    driver = gdal.GetDriverByName('GTiff')
    rows,cols = np.shape(sed_class)
    ds = driver.Create( outFile, cols, rows, 1, gdal.GDT_Float32)      
    if proj is not None:  
        ds.SetProjection(proj.ExportToWkt()) 
    ds.SetGeoTransform(gt)
    ss_band = ds.GetRasterBand(1)
    ss_band.WriteArray(sed_class)
    ss_band.SetNoDataValue(-9999)
    ss_band.FlushCache()
    ss_band.ComputeStatistics(False)
    del ds

def output_surfaces(data, site,gt,out_root,surf_type):
    CreateRaster(data,gt,out_root + os.sep + site +'_' + surf_type +'.tif')
    print 'Sucessfully created ' + surf_type +' for ' + site +'!!'
    
    
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
    
    #output surfaces
    output_surfaces(max_surf.astype(float),site,gt,out_root,'Maximum_Surface')
    output_surfaces(min_surf.filled(-9999),site,gt,out_root,'Minimum_Surface')
    

    
    return max_index, min_index, max_surf, min_surf,gt

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

def plotting_utils(survey_dates):
    '''
    Function to create color ramp for optimized for the amount of surveys at a site
    Inputs: list of survey dates
    Outputs:
        cmap = customized matplotlib.colors.LinearSegmentedColormap
        bounds = array containing the number of ticks
        norm = customized matplotlib.colors.BoundaryNorm used in controuf pl;ot
    '''
    # define the colormap
    cmap = plt.cm.jet
    # extract all colors from the .jet map
    cmaplist = [cmap(i) for i in range(cmap.N)]
    # force the first color entry to be grey
    cmaplist[0] = (.5,.5,.5,1.0)
    # create the new map
    cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N)

    # define the bins and normalize
    bounds = np.linspace(0,len(survey_dates),len(survey_dates)+1)
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)    
    return cmap, bounds, norm


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

def output_processing_rasters(eddy_data,mini_affine,eddy_min_data,le_data,eddy_min_masked,le_dod,fz_data,he_data,site,out_root):
    with rasterio.open(out_root + os.sep + site +'_' + 'eddy_max' +'.tif', 'w', driver='GTiff', 
                       height = eddy_data.shape[0], width = eddy_data.shape[1], dtype=rasterio.dtypes.float64, 
                       crs={'init': 'epsg:26949'}, count = 1, transform=mini_affine) as dst:
        dst.write(eddy_data.filled(-9999),1)
        dst.nodata = -9999
    with rasterio.open(out_root + os.sep + site +'_' + 'eddy_min' +'.tif', 'w', driver='GTiff', 
                       height = eddy_min_data.shape[0], width = eddy_min_data.shape[1], dtype=rasterio.dtypes.float64, 
                       crs={'init': 'epsg:26949'}, count = 1, transform=mini_affine) as dst:
        dst.write(eddy_min_data.filled(-9999),1)
        dst.nodata = -9999    
    with rasterio.open(out_root + os.sep + site +'_' + 'eddy_max_low_elev' +'.tif', 'w', driver='GTiff', 
                       height = le_data.shape[0], width = le_data.shape[1], dtype=rasterio.dtypes.float64, 
                       crs={'init': 'epsg:26949'}, count = 1, transform=mini_affine) as dst:
        dst.write(le_data.filled(-9999),1)
        dst.nodata = -9999
    with rasterio.open(out_root + os.sep + site +'_' + 'eddy_min_low_elev' +'.tif', 'w', driver='GTiff', 
                       height = eddy_min_masked.shape[0], width = eddy_min_masked.shape[1], dtype=rasterio.dtypes.float64, 
                       crs={'init': 'epsg:26949'}, count = 1, transform=mini_affine) as dst:
        dst.write(eddy_min_masked.filled(-9999),1)
        dst.nodata = -9999
    with rasterio.open(out_root + os.sep + site +'_' + 'eddy_dod_low_elev' +'.tif', 'w', driver='GTiff', 
                       height = le_dod.shape[0], width = le_dod.shape[1], dtype=rasterio.dtypes.float64, 
                       crs={'init': 'epsg:26949'}, count = 1, transform=mini_affine) as dst:
        dst.write(le_dod.filled(-9999),1)
        dst.nodata = -9999    
    with rasterio.open(out_root + os.sep + site +'_' + 'eddy_max_fz_elev' +'.tif', 'w', driver='GTiff', 
                       height = fz_data.shape[0], width = fz_data.shape[1], dtype=rasterio.dtypes.float64, 
                       crs={'init': 'epsg:26949'}, count = 1, transform=mini_affine) as dst:
        dst.write(fz_data.filled(-9999),1)
        dst.nodata = -9999    
    with rasterio.open(out_root + os.sep + site +'_' + 'eddy_max_he_elev' +'.tif', 'w', driver='GTiff', 
                       height = he_data.shape[0], width = he_data.shape[1], dtype=rasterio.dtypes.float64, 
                       crs={'init': 'epsg:26949'}, count = 1, transform=mini_affine) as dst:
        dst.write(he_data.filled(-9999),1)
        dst.nodata = -9999 
    print 'Sucessfully Output Intermediate Processing Rasters for ' + site +'!!'

def eddy_metrics_calculator(max_surf, min_surf, gt, shps,site,raster_out=False,reatt=False,sep=False):
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
    
    if raster_out==True:
        if reatt == True:
            site = site + '_r'
            output_processing_rasters(eddy_data,mini_affine,eddy_min_data,le_data,eddy_min_masked,le_dod,fz_data,he_data,site,out_root)
        elif sep == True:
            site = site + '_s'
            output_processing_rasters(eddy_data,mini_affine,eddy_min_data,le_data,eddy_min_masked,le_dod,fz_data,he_data,site,out_root)
        else:             
            output_processing_rasters(eddy_data,mini_affine,eddy_min_data,le_data,eddy_min_masked,le_dod,fz_data,he_data,site,out_root)
    else:
        pass
    
    result = {}
    
    result.setdefault('SiteCode',[]).append(site)
    result.setdefault('Max_Vol_Eddy_FZ',[]).append(fz_max_vol)
    result.setdefault('Max_Vol_Eddy_HE',[]).append(he_max_vol)
    result.setdefault('Max_Vol_Eddy_Low',[]).append(le_max_vol)
    result.setdefault('Max_Area_Eddy_FZ',[]).append(fz_data.count()*0.25**2)
    result.setdefault('Max_Area_Eddy_HE',[]).append(he_data.count()*0.25**2)
    result.setdefault('Max_Area_Eddy_Low',[]).append(le_data.count()*0.25**2)
    return result
    
    
def agg_hist_plot(max_index,min_index,survey_dates, site):
    
    cmap, bounds, norm = plotting_utils(survey_dates)
    
    fig, ax = plt.subplots(figsize=(12,12))
    
    m = Basemap(projection='merc', 
                    epsg=26949, 
                    llcrnrlon=np.min(glon), 
                    llcrnrlat=np.min(glat),
                    urcrnrlon=np.max(glon), 
                    urcrnrlat=np.max(glat)-0.0011 ,ax=ax)
    m.wmsimage(server='http://grandcanyon.usgs.gov/arcgis/services/Imagery/ColoradoRiverImageryExplorer/MapServer/WmsServer?', layers=['3'], xpixels=1000)
    x,y = m.projtran(glon, glat)
    max_index =max_index.astype(float)
    max_index[max_index<0]=np.nan
    im = m.contourf(x,y,max_index.T, cmap=cmap,norm=norm)#
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbr = mpl.colorbar.ColorbarBase(cax, cmap=cmap, norm=norm, spacing='proportional', ticks=bounds, boundaries=bounds, format='%1i')
    cbr.ax.set_yticklabels(survey_dates)
    ax.set_title(site + ': Aggradation History of the Maximum Surface')
    plt.tight_layout()
    plt.subplots_adjust(top = 0.968)
    
    fig1, ax1 = plt.subplots(figsize=(12,12))
    
    m = Basemap(projection='merc', 
                    epsg=26949, 
                    llcrnrlon=np.min(glon), 
                    llcrnrlat=np.min(glat),
                    urcrnrlon=np.max(glon), 
                    urcrnrlat=np.max(glat)-0.0011 ,ax=ax1)
    m.wmsimage(server='http://grandcanyon.usgs.gov/arcgis/services/Imagery/ColoradoRiverImageryExplorer/MapServer/WmsServer?', layers=['3'], xpixels=1000)
    x,y = m.projtran(glon, glat)
    min_index =min_index.astype(float)
    min_index[min_index<0]=np.nan
    im = m.contourf(x,y,min_index.T, cmap=cmap,norm=norm)#
    divider = make_axes_locatable(ax1)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbr1 = mpl.colorbar.ColorbarBase(cax, cmap=cmap, norm=norm, spacing='proportional', ticks=bounds, boundaries=bounds, format='%1i')
    cbr1.ax.set_yticklabels(survey_dates)
    ax1.set_title(site + ': Degradation History of the Minimum Surface')
    plt.tight_layout()
    plt.subplots_adjust(top = 0.968) 
  
if __name__ =='__main__':
    
    in_root = r"C:\workspace\sandbar-results-aggregation\Max_Min_Surface\input"
    out_root =r"C:\workspace\sandbar-results-aggregation\Max_Min_Surface\output"
    
    single_eddy_sites = ['0003L', '0009L', '0016L', '0022R', '0030R', '0032R', '0043L', '0047R', '0051L', '0055R', '0062R', '0068R', '0070R', '0081L', '0087L', '0091R', '0093L', '0104R', '0119R', '0122R', '0123L', '0137L', '0139R', '0145L', '0172L', '0183R', '0194L', '0213L', '0220R', '0225R', 'M006R']
    
    for i in single_eddy_sites:
        site = i
        files = glob(in_root + os.sep + site + os.sep + '*' + os.sep+ '*.tif')
        shps = glob(in_root + os.sep + site + os.sep + '*_ed.shp')

        max_index, min_index, max_surf, min_surf, gt = get_surfaces(files,out_root,site)
    
        glon, glat = get_lons_data(files[0])
        
        survey_dates = get_date_list(files)
        if i == single_eddy_sites[0]:
            result = eddy_metrics_calculator(max_surf, min_surf,gt,shps,site,raster_out=True)
        else:
            
            tmp =eddy_metrics_calculator(max_surf, min_surf,gt,shps,site,raster_out=True)
            result['Max_Vol_Eddy_FZ'].append(tmp['Max_Vol_Eddy_FZ'][0])
            result['Max_Vol_Eddy_HE'].append(tmp['Max_Vol_Eddy_HE'][0])
            result['Max_Vol_Eddy_Low'].append(tmp['Max_Vol_Eddy_Low'][0])
            result['Max_Area_Eddy_Low'].append(tmp['Max_Area_Eddy_Low'][0])
            result['Max_Area_Eddy_FZ'].append(tmp['Max_Area_Eddy_FZ'][0])
            result['Max_Area_Eddy_HE'].append(tmp['Max_Area_Eddy_HE'][0])            
            result['SiteCode'].append(tmp['SiteCode'][0])
            del tmp

    no_bath_sites = ['0008L', '0024L', '0029L', '0033L', '0056R', '0084R', '0167L']

    for i in no_bath_sites:
        
        site = i
        files = glob(in_root + os.sep + site + os.sep + '*' + os.sep+ '*.tif')
        shps = glob(in_root + os.sep + site + os.sep + 'RM[0-9][0-9][0-9].shp')

        max_index, min_index, max_surf, min_surf, gt = get_surfaces(files,out_root,site)
    
        glon, glat = get_lons_data(files[0])
        
        survey_dates = get_date_list(files)
        
        if 'result' in locals():
            tmp =eddy_metrics_calculator(max_surf, min_surf,gt,shps,site)
            result['Max_Vol_Eddy_FZ'].append(tmp['Max_Vol_Eddy_FZ'][0])
            result['Max_Vol_Eddy_HE'].append(tmp['Max_Vol_Eddy_HE'][0])
            result['Max_Vol_Eddy_Low'].append(tmp['Max_Vol_Eddy_Low'][0])
            result['Max_Area_Eddy_Low'].append(tmp['Max_Area_Eddy_Low'][0])
            result['Max_Area_Eddy_FZ'].append(tmp['Max_Area_Eddy_FZ'][0])
            result['Max_Area_Eddy_HE'].append(tmp['Max_Area_Eddy_HE'][0])               
            result['SiteCode'].append(tmp['SiteCode'][0])
        else:
            if i == no_bath_sites[0]:
                result = eddy_metrics_calculator(max_surf, min_surf,gt,shps,site)
            else:
                pass

            
    two_bar_sites = ['0035L', '0041R', '0044L', '0045L', '0050R', '0063L', '0065R', '0202R']
     
    #reatt bars
    for i in two_bar_sites:
        site=i
        files = glob(in_root + os.sep + site + os.sep + '*' + os.sep+ '*.tif')
        shps = glob(in_root + os.sep + site + os.sep + 'RM[0-9][0-9][0-9]_ed_r.shp')
        max_index, min_index, max_surf, min_surf, gt = get_surfaces(files,out_root,site,reatt=True)
        glon, glat = get_lons_data(files[0])
        
        survey_dates = get_date_list(files)
        
        if 'result' in locals():
            tmp =eddy_metrics_calculator(max_surf, min_surf,gt,shps,site,reatt=True,raster_out=True)
            result['Max_Vol_Eddy_FZ'].append(tmp['Max_Vol_Eddy_FZ'][0])
            result['Max_Vol_Eddy_HE'].append(tmp['Max_Vol_Eddy_HE'][0])
            result['Max_Vol_Eddy_Low'].append(tmp['Max_Vol_Eddy_Low'][0])
            result['Max_Area_Eddy_Low'].append(tmp['Max_Area_Eddy_Low'][0])
            result['Max_Area_Eddy_FZ'].append(tmp['Max_Area_Eddy_FZ'][0])
            result['Max_Area_Eddy_HE'].append(tmp['Max_Area_Eddy_HE'][0])               
            result['SiteCode'].append(tmp['SiteCode'][0])
        else:
            if i == two_bar_sites[0]:
                result = eddy_metrics_calculator(max_surf, min_surf,gt,shps,site,reatt=True,raster_out=True)
            else:
                pass
     
    
    #sep bars 
    for i in two_bar_sites:
        site=i
        files = glob(in_root + os.sep + site + os.sep + '*' + os.sep+ '*.tif')
        shps = glob(in_root + os.sep + site + os.sep + 'RM[0-9][0-9][0-9]_ed_s.shp')
        max_index, min_index, max_surf, min_surf, gt = get_surfaces(files,out_root,site,sep=True)
        glon, glat = get_lons_data(files[0])
        
        survey_dates = get_date_list(files)
        
        if 'result' in locals():
            tmp =eddy_metrics_calculator(max_surf, min_surf,gt,shps,site,sep=True,raster_out=True)
            result['Max_Vol_Eddy_FZ'].append(tmp['Max_Vol_Eddy_FZ'][0])
            result['Max_Vol_Eddy_HE'].append(tmp['Max_Vol_Eddy_HE'][0])
            result['Max_Vol_Eddy_Low'].append(tmp['Max_Vol_Eddy_Low'][0])
            result['Max_Area_Eddy_Low'].append(tmp['Max_Area_Eddy_Low'][0])
            result['Max_Area_Eddy_FZ'].append(tmp['Max_Area_Eddy_FZ'][0])
            result['Max_Area_Eddy_HE'].append(tmp['Max_Area_Eddy_HE'][0])               
            result['SiteCode'].append(tmp['SiteCode'][0])
        else:
            if i == two_bar_sites[0]:
                result = eddy_metrics_calculator(max_surf, min_surf,gt,shps,site,sep=True,raster_out=True)
            else:
                pass

    df = pd.DataFrame.from_dict(result, orient='index').transpose().set_index('SiteCode')
    df = df[['Max_Area_Eddy_Low','Max_Vol_Eddy_Low','Max_Area_Eddy_FZ','Max_Vol_Eddy_FZ','Max_Area_Eddy_HE','Max_Vol_Eddy_HE']]
    df.to_csv(out_root + os.sep +'Eddy_Max_Vol_nonWedge_Method.csv', sep = ',')
                
                



    
        
