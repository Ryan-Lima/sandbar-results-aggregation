# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 11:11:31 2016

@author: dan
"""

import pandas as pd
from glob import glob 
import os

def extract_date(row):
    file_name = row['Grid_File_Name']
    date_string = file_name.split('\\')[-1].split('_')[1]
    return date_string
    
def extract_site(row):
    file_name = row['Grid_File_Name']
    site_string = file_name.split('\\')[-1].split('_')[0]
    return site_string
    
def find_side(row):
    sitenum = row['site_string']
    data = pd.read_csv(r'C:\workspace\survey_stage\LU_site_shape_path.csv', sep = ',')
    data = data[1:]
    query = data[data.Site.str.contains(sitenum)]
    site_side = query['Site'].iloc[0][-1]
    return site_side

def build_filepath(row):
    #Change directory to points
    my = row['Grid_File_Name']
    my = my.split('\\')
    my[3] = 'NAU_Survey_PTS_Files'
    
    #Add the side to the new name
    new_name = my[-1].split('_')
    new_name[0] = new_name[0]+row['site_side']
    new_name[-1] = 'PTS.txt'
    new_name = '_'.join(new_name)
    my[-1] = new_name
    my[0] = 'C:\\'
    new_path = os.path.normpath(os.path.join(my[0],my[1],my[2],my[3],my[4],my[5]))
    return new_path
    
def build_filepath2(row):
    #Change directory to points
    my = row.Grid_File_Name
    my = my.split('\\')
    my[3] = 'NAU_Survey_PTS_Files'
    
    #Add the side to the new name
    new_name = my[-1].split('_')
    new_name[0] = '-6R'
    new_name[-1] = 'PTS.txt'
    new_name = '_'.join(new_name)
    my[-1] = new_name
    my[0] = 'C:\\'
    new_path = os.path.normpath(os.path.join(my[0],my[1],my[2],my[3],my[4],my[5]))
    return new_path

def check1(row):
    if os.path.isfile(row['pts_path']):
        var_back = 'Exists'
    else:
        var_back = 'DOES NOT'
    return var_back
    
def add_zero (row):
    pts_path = row['pts_path'].split('\\')
    pts_path[-1]='0'+pts_path[-1]
    pts_path[0] = 'C:\\'
    new_path = os.path.normpath(os.path.join(pts_path[0],pts_path[1],pts_path[2],pts_path[3],pts_path[4],pts_path[5]))
    return new_path
def remove_zero (row):
    pts_path = row['pts_path'].split('\\')
    pts_path[-1]=pts_path[-1][1:]
    pts_path[0] = 'C:\\'
    new_path = os.path.normpath(os.path.join(pts_path[0],pts_path[1],pts_path[2],pts_path[3],pts_path[4],pts_path[5]))
    return new_path
    
grid_list = glob(r'C:\workspace\survey_stage\NAU_GRID_FILES\*\*.txt')
df = pd.DataFrame(grid_list, columns=['Grid_File_Name'])

pts_list = glob(r'C:\workspace\survey_stage\NAU_Survey_PTS_Files\*\*.txt')

#append date string and site string to dataframe 
df['date_string']= df.apply(lambda row: extract_date(row), axis=1)
df['site_string']= df.apply(lambda row: extract_site(row), axis=1)

#Pad site numbers
format_df = df[df.site_string != 'M06R']
leftovers = df[df.site_string == 'M06R']
format_df['site_string'] = format_df['site_string'].apply(lambda x: '{0:0>3}'.format(x))

#Find Site Side
format_df['site_side'] = format_df.apply(lambda row: find_side(row), axis = 1)
leftovers['site_side'] = 'R'


#Build file paths for not M006R
format_df['pts_path'] = format_df.apply(lambda row: build_filepath(row), axis=1)
format_df = format_df[['Grid_File_Name','pts_path']]

#Build path for M006R
leftovers['pts_path'] = leftovers.apply(lambda row: build_filepath2(row), axis=1)
leftovers = leftovers[['Grid_File_Name','pts_path']]

df = pd.concat([format_df,leftovers])
del format_df, leftovers


df['File_Check'] = df.apply(lambda row: check1(row), axis=1)

great = df[df.File_Check != 'DOES NOT']
problem_children = df[df.File_Check == 'DOES NOT']

#Try this too
problem_children['pts_path'] = problem_children.apply(lambda row: add_zero(row), axis=1)
problem_children['File_Check'] = problem_children.apply(lambda row: check1(row), axis=1)

great1 = problem_children[problem_children.File_Check != 'DOES NOT']
great = pd.concat([great,great1])
del great1
problem_children = problem_children[problem_children.File_Check == 'DOES NOT']
problem_children['pts_path'] = problem_children.apply(lambda row: remove_zero(row), axis=1)

problem_children = problem_children[['pts_path']]
problem_children.to_csv(r'C:\workspace\survey_stage\problem_children.csv',sep=',',index=False)

