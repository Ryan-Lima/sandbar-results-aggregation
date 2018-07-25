# -*- coding: utf-8 -*-
"""
Created on Fri Nov 03 15:12:27 2017

@author: dan
"""

import pandas as pd
from glob import glob
from sympy.solvers import solve
from sympy import Symbol
import os


def get_date(i):
    date_str = i.split('\\')[-1].split('.')[0].split('_')[-2]
    pd_date = pd.to_datetime(date_str, format='%y%m%d')   
    return pd_date

def get_coeff(sd_coeff,site_str):
    sd_coeff = sd_coeff.set_index('site_name')
    i = sd_coeff.loc[site_str]['int']
    lin_coef =  sd_coeff.loc[site_str]['coflin']
    sqd_coef =  sd_coeff.loc[site_str]['cofsqd']
    return i, lin_coef,sqd_coef

def get_discharge(intercept, lin_coeff,sqd_coeff,val):
    x = Symbol('x')
    ans = float(solve(intercept-val + lin_coeff*x +sqd_coeff*x**2)[0])
    return ans

if __name__ =='__main__':
    sites = glob(r"C:\workspace\survey_stage\WSE_Points\*")
    for site in sites[0:1]:
        site_str = site.split('\\')[-1]
        files = glob(site + os.sep + "*.txt")
        sd_coeff = pd.read_excel(r"C:\workspace\survey_stage\survey_stage.xlsm",sheetname='SD_Relations')
        
        dates, qs = [],[]
        for i in files:
            
            date = get_date(i)
            
            #Import WSE from pts file
            data = pd.read_csv(i,sep=',',header=None)
            data.columns = ['point_num','Easting','Northing','Elevation','Attribute']
            
            #find average water surface elevation 
            val = data[data['Elevation']<=data['Elevation'].quantile(.5)]['Elevation'].mean(axis=0)
            
            #get coefficents for sd relationship
            intercept, lin_coeff,sqd_coeff = get_coeff(sd_coeff,site_str)

            q = get_discharge(intercept, lin_coeff,sqd_coeff,val)
            qs.append(q)
            dates.append(date)
        df = pd.DataFrame({'Date':dates,'Discharge':qs})
    
    
    
    
    sd_realation(solve(intercept-val + lin_coeff*x +sqd_coeff*x**2)[1])
