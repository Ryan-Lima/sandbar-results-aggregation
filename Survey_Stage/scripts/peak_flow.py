# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 14:08:14 2016

@author: dan
"""

import pandas as pd
import numpy as np

def find_peak(early_date,current_date,flow_df):
    mask = (flow_df['date']>= early_date) & (flow_df['date'] < current_date)
    query = flow_df.loc[mask]
    peak_flow = np.max(query['flow'])*0.3048**3
    return peak_flow
    
    
flow_df = pd.read_csv(r"C:\workspace\survey_stage\lees_Ferry_flow_Data.csv", sep ='\t')
flow_df['date'] = pd.to_datetime(flow_df['date'])
    
data = pd.ExcelFile(r"C:\workspace\survey_stage\survey_stage_2016_08_14.xlsx")

list_of_sites = data.sheet_names[:-4]


for site in list_of_sites:
    #site = list_of_sites[0]
    df = data.parse(site,parse_cols="H:I" )
    df['Survey_Date'] = pd.to_datetime(df['Survey_Date'])
    df = df.dropna()


    n=0
    for thing in df['Survey_Date'][1:]:
        early_date = df['Survey_Date'][n]
        current_date = thing
        peak_flow = find_peak(early_date,current_date,flow_df)
        n+=1
        df['Avg_Stage'][n] = peak_flow
    df['site']=site
    
    df = df[['site','Survey_Date','Avg_Stage']]
    if site == list_of_sites[0]:
        out_data = df
    else:
        out_data = pd.concat([out_data,df])
out_data = out_data.rename(columns = {'Avg_Stage':'Peak_Discharge'})        
out_data.to_csv(r"C:\workspace\survey_stage\LU_peak_flow.csv", sep =',', index=False)