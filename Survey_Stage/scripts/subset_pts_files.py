# -*- coding: utf-8 -*-
"""
Created on Thu Jun 02 11:44:44 2016

@author: dh396
"""

import pandas as pd
from glob import glob
from osgeo import ogr
import os

def get_extent(shpFile):
    '''
    Function to get extent from input shapefile
    '''
    ds = ogr.Open(shpFile)
    lyr = ds.GetLayer(0)
    eddy_extent = list(lyr.GetExtent())
    x_min, x_max, y_min, y_max =[i for i in eddy_extent]
    del lyr,ds
    return x_min, x_max, y_min, y_max 
    
def date_from_file(fp):
    '''
    Fucntion to parse and format date from file name
    '''
    date = fp.split('\\')[-1].split('_')[1]
    date = pd.to_datetime(date, format='%y%m%d')
    return date

def clip_points (df, shpFile):
    '''
    Funciton to clip water surface points to extents of computational boundary
    '''
    x_min, x_max, y_min, y_max =get_extent(shpFile)
    local_mask = (df.northing >= y_min) & (df.northing < y_max) & (df.easting >= x_min) & (df.easting < x_max)
    subset_we = df.loc[local_mask]
    return subset_we
    
def subset_we (df, attrib = None):
    '''
    Function to points files to attributes like a given attribute
    '''
    
    if attrib is None:
        attrib = 'W'
    df['attribute']= df['attribute'].str.upper()
    we_points = df[df.attribute.str.startswith(attrib.upper())]
    return we_points
    
def make_dir(site_name):
    '''
    Function to create output directory for merged water surface points
    '''
    target_dir = r'C:\workspace\survey_stage\WSE_Points' + os.sep + site_name
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    return target_dir
    
def find_shpfile_path(site_name):
    '''
    Function to find shapefile path
    '''
    lu_shp_path = pd.read_csv(r"C:\workspace\survey_stage\LU_site_shape_path.csv", sep =',')
    query = lu_shp_path[lu_shp_path.Site == site_name]
    shp_path = query['shp_path'].iloc[0]
    return shp_path
    
#Tempoary working path to cathederal's points
#filelist = glob(r'C:\workspace\survey_stage\NAU_Survey_PTS_Files\003L\*pts.txt')
#file = filelist[0]
#shpFile = r"C:\workspace\survey_stage\shp\RM003_ed.shp"
#x_min, x_max, y_min, y_max =get_extent(shpFile)

df = pd.read_excel(r"C:\workspace\survey_stage\missing_wse_surveys_jeh.xlsx",parse_cols="A,B,E")

#Sitelist 
sitelist = glob(r'C:\workspace\survey_stage\NAU_Survey_PTS_Files\*')
#site = sitelist[0]
for site in sitelist:
    #Search for pts files
    filelist = glob(site+ r'\*pts.txt')
    
    #Create output directory
    site_name = site.split('\\')[-1]
    target_dir = make_dir(site_name)
    
    #Find relevant shapefile path
    shpFile = find_shpfile_path(site_name)
    
    for file in filelist:
        #file = filelist[17]
        #read points file
        data = pd.read_csv(file, sep = ',',names=['pt_id','easting','northing','z','attribute'])
        
        #append Date to dataframe
        date = date_from_file(file)
        data['Date']= date
        
        #Subset points to watersurface elevations  
        we_list = subset_we(data)
        
        if len(we_list) == 0:
            try:
                attrib = df[(df.Site == site_name) & (df.Survey_Date == date)]['WSE_attribute'].iloc[0]
            except:
                print file + ' does not have any WSE obserbations'
            we_list = subset_we(data, attrib)
            
        #clip to shapefile extents
        clip_we_list = clip_points (we_list,shpFile)
        
        #check to see if clip_we_list is empty
        #if so, check to see if the northing and easting are flipped in the input file
        if clip_we_list.empty:
            data = pd.read_csv(file, sep = ',',names=['pt_id','northing','easting','z','attribute'])
            #append Date to dataframe
            date = date_from_file(file)
            data['Date']= date
            #Subset points to watersurface elevations  
            we_list = subset_we(data)
            clip_we_list = clip_points (we_list,shpFile)
            
        
        
        #export individual surveys to text files
        survey_export = clip_we_list[['pt_id','easting','northing','z','attribute']]
        outFP = target_dir + os.sep + file.split('\\')[-1]
        survey_export.to_csv(outFP, sep = ',', header=False, index=False)
        
        #Merge all wse points for merged site output
        if file == filelist[0]:
            pt_list = clip_we_list
        else:
            pt_list = pd.concat([pt_list,clip_we_list])
            
    pt_list = pt_list[['Date','pt_id','easting','northing','z','attribute']]   
    outfile = r'C:\workspace\survey_stage\Merged_WSE_PTS' + os.sep + site_name + '_clipped_wse.pts'
    pt_list.to_csv(outfile, sep =',',index=False)
    del pt_list

##Subset Points to only wsurface elecations        
#pt_list['attribute'] = pt_list['attribute'].str.upper()        
#we_list = pt_list[pt_list.attribute.str.startswith('W')]
#
##Shapefile extent mask
#mask = (we_list.northing >= y_min) & (we_list.northing < y_max) & (we_list.easting >= x_min) & (we_list.easting < x_max)
#sub_we_list = we_list.loc[mask]
#
##testing area to check clip points function
#test_we = clip_points(data,shpFile)


