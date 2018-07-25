# -*- coding: utf-8 -*-
"""
Created on Sat Jul 23 12:01:52 2016

@author: dan
"""

import pandas as pd
import os

def build_file_path (row):
    fpath = r'C:\workspace\survey_stage\shp\RM' + str(row['Site'][:-1]) + '_ed.shp'
    return fpath
    

xl = pd.ExcelFile(r"C:\workspace\survey_stage\survey_stage_2015_06_05.xlsx")

list_of_sites = xl.sheet_names[:-4]
df = pd.DataFrame(list_of_sites, columns=['Site'])

df['shp_path'] = df.apply(lambda row: build_file_path (row), axis = 1)

n=0
#Redo sites with out any eddy shapefiles
for thing in df['shp_path']:
    if not os.path.isfile(thing):
        print thing + ' index is %s' %(n,)
        new_fp = thing[:-6] + 'ch.shp'
        df['shp_path'][n] = new_fp
    n = n + 1
del thing, n

n=0
for thing in df['shp_path']:
    if not os.path.isfile(thing):
        print thing + ' index is %s' %(n,)
        new_fp = thing[:-7] +'.shp'
        df['shp_path'][n] = new_fp
    n = n + 1
#check to see if all shp paths are valid
for thing2 in df['shp_path']:
    if not os.path.isfile(thing2):
        print thing2 + ' DOES NOT EXIST'

