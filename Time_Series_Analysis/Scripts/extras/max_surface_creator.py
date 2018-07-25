# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 14:07:20 2018

@author: dan
"""

from osgeo import gdal_array, gdal, osr
import numpy as np
from glob import glob
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pyproj


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
    sed_class[np.isnan(sed_class)] = -99
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
    
    
files = glob(r"C:\Users\dan\Desktop\Dan_test\*.tif")


for raster in files:
    
 
    data = gdal_array.LoadFile(raster)
    
    if raster == files[0]:
        ds = gdal.Open(raster)
        output = data
        proj = ds.GetProjection()
        gt = ds.GetGeoTransform()
        del ds
    else:
        output=np.dstack((data,output))

result = np.max(output,axis=2)


CreateRaster(result,gt,r"C:\Users\dan\Desktop\Dan_test\output\max_surface.tif")

result2 = output.argmax(axis=2).astype(float)
result2[result==-9999]=-9999

glon, glat = get_lons_data(r"C:\Users\dan\Desktop\Dan_test\output\max_surface.tif")

fig, ax = plt.subplots()

m = Basemap(projection='merc', 
                epsg=26949, 
                llcrnrlon=np.min(glon), 
                llcrnrlat=np.min(glat),
                urcrnrlon=np.max(glon), 
                urcrnrlat=np.max(glat)-0.00055 ,ax=ax)
m.wmsimage(server='http://grandcanyon.usgs.gov/arcgis/services/Imagery/ColoradoRiverImageryExplorer/MapServer/WmsServer?', layers=['3'], xpixels=1000)
x,y = m.projtran(glon, glat)

result2[result2<0]=np.nan
im = m.contourf(x,y,result2.T, cmap='Paired',levels=[0,1,2,3,4])
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
cbr = plt.colorbar(im, cax=cax)


cbr.ax.get_yaxis().set_ticks([])
for j, lab in enumerate(['2008-04-12', '2008-06-02', '2008-10-26','2009-10-25']):
    cbr.ax.text(1.1, (2 * j + 1) / 8.0, lab, ha='left', va='center')
    
    
cbr.ax.set_yticklabels(['2008-04-12', '2008-06-02', '2008-10-26','2009-10-25'],va='center')     
cbr.ax.set_label()

for t in cbr.ax.get_yticklabels():
    t.set_horizontalalignment('right')   
    t.set_x(3.5)   
    
        
