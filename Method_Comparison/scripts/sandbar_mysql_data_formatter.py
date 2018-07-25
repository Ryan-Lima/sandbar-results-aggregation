# -*- coding: utf-8 -*-
"""
Created on Tue Jan 02 10:24:50 2018

@author: dan
"""

import pandas as pd
from sandbar_max_vol import max_volumes,max_areas
from sandbar_TimeSeries import time_series

def plane_height(row):
    if row['BinID'] == 2:
        return 'eddy8kto25k'
    elif row['BinID'] == 3:
        return 'eddyabove25k'
    elif row['BinID'] == 1:
        return 'eddyminto8k'
    
def pivot_two_bars(tmp_df):
    '''
    Helper function to pivot sandbar data to aggregrate area and volumes
    Input: Dataframe containing the data to be aggregrated
    Output: Dataframe with two bar sites surveys merged
    Note: 
        SectionID is different between sep and reatt bars<- Have to drop them during the pivot
    '''
    
    return pd.pivot_table(tmp_df,values=['Area', 'Volume'], index=[u'SiteCode','SiteID','RunID','SurveyID', 'SurveyDate', 'BinID', 'TripDate',
       'TripID',  'Plane_Height'],aggfunc='sum').reset_index()

def two_bar_merger(data):
    '''
    Function to combine two bar site surveys so each site only has one measurment per survey date.  Also checks for mutiple RunID's and returns a unique dataset with the latest RunID
    Inputs: Dataframe containing sandbar data
    Outputs: Dataframe with two bar sites surveys merged with single bar sites
    Notes:

    '''
    
    two_bar_sites = data[(data['Title'] != 'Eddy - Single') ].SiteCode.unique()
    tmp_df = data[data['SiteCode'].isin(two_bar_sites)]
    other_data = data[~data['SiteCode'].isin(two_bar_sites)]
    tmp_df = pivot_two_bars(tmp_df)
    other_data = other_data[['SiteCode','SiteID','RunID','SurveyID', 'SurveyDate', 'BinID', 'TripDate',
       'TripID',  'Plane_Height','Area','Volume']]
    
    result = pd.concat([tmp_df,other_data],axis=0)
    
    if len(result.RunID.unique())==1:    
        return result
    else:
        return keep_max_runid(result)

def keep_max_runid(df):
    '''
    Function to drop duplicate records and keep the recrod with the maximum of RunID
    Inputs: Dataframe containing sandbar data
    Outputs: Dataframe with unique recrods
    Notes:
        
    '''
    return  df.groupby(['SiteCode','SiteID','SurveyID', 'SurveyDate', 'BinID', 'TripDate',
       'TripID',  'Plane_Height','Area','Volume'],as_index=False).max()
        
def max_area_vol(df):
    '''
    Function to assign maximum area and volumes for each bin at each site
    Input: Dataframe with sandbar data exported from MySql database
    Output: Dataframe with maximum metrics appended
    Notes:
        Maximum surface metrics were recomputed by Rob Ross on April 26, 2017 (dictonary is stored in max_vol.py)
        There is an outstanding issue with the maximum surface at 003L, still being worked on
    '''
    #Volumes
    sites2drop = ['035L_R','035L_S','041R_R','041R_S','044L_S','044L_R','045L_S','045L_R','050R_R','050R_S','063L_S','063L_R','065R_R','065R_S','202R_S','202R_R']
    tmp = pd.DataFrame.from_dict(max_volumes).drop(sites2drop)
    tmp = tmp.T.unstack().rename("Max_Vol").to_frame().dropna()
    df = df.set_index(['SiteCode','BinID'])
    tmp.index.names =df.index.names 
    result = df.combine_first(tmp)
    
    #Areas
    tmp = pd.DataFrame.from_dict(max_areas).drop(sites2drop)
    tmp = tmp.T.unstack().rename("Max_Area").to_frame().dropna().reset_index()[['level_0','Max_Area']].set_index('level_0','SiteCode')
    df = df.reset_index().set_index('SiteCode')
    tmp.index.names =df.index.names 
    return result.combine_first(tmp).reset_index()

def append_time_series(df):
    '''
    Function to append time series type to each record
    Inputs: Dataframe containing sandbar data
    Outputs: Dataframe with time series type appended as column
    Notes:
        Time_Series - Complete or partial trip
            -'long' = complete trips, can use for marble canyon and grand canyon time series.
            -'na'= incomplete trip, exclude from time series analysis
            -'mc' = only include in marble canyon time series
    '''
    tmp = pd.DataFrame.from_dict(time_series)
    df = df.set_index('TripID')
    return df.combine_first(tmp)


def data_formatter(in_file):
    '''
    Function to format sandbar data export from mysql database
    Input: csv exported from the MySQL database 
    Output: Dataframe with all the sandbar data with maximum surface bins, max areas, and trip identifier
    Notes:
        Used the following query:
        SELECT Site.SiteCode as SiteCode,
        Survey.SiteID ,
        MR.RunID ,
        MR.SectionID ,
        Section.SectionTypeID ,
        Survey.SurveyID ,
        Survey.SurveyDate ,
        MR.BinID ,
        MR.Area ,
        MR.Volume ,
        L.Title,
        Survey.TripID,
        T.TripDate
        FROM (SELECT 
                mrb.RunID, mrb.SectionID, mrb.BinID, mrb.Area, mrb.Volume
            FROM
                test.ModelResultsBinned mrb
            WHERE
                mrb.RunID IN (30 , 31, 32, 34)) MR   /* <-------Must speficy the runs you want*/ 
        INNER JOIN SandbarSections Section ON MR.SectionID = Section.SectionID
        INNER JOIN SandbarSurveys Survey ON Survey.SurveyID = Section.SurveyID
        INNER JOIN Trips T ON T.TripID = Survey.TripID
        INNER JOIN LookupListItems L ON L.ItemID = Section.SectionTypeID
        INNER JOIN SandbarSites Site ON Site.SiteID=Survey.SiteID;
    
    '''
    data = pd.read_csv(in_file,sep = ',')
    data['Plane_Height'] = data.apply(lambda x: plane_height(x), axis=1)
    data = data[(data['Title'] != 'Channel')]
    
    #Merged two bar sites
    two_bar_merged = two_bar_merger(data)
    
    #Append maximum area and volume metrics
    result = max_area_vol(two_bar_merged)
    
    #append Time_Series type
    result = append_time_series(result)
    result['SurveyDate'] = pd.to_datetime(result['SurveyDate'],format='%Y-%m-%d').dt.date
    result['TripDate'] = pd.to_datetime(result['TripDate'],format='%Y-%m-%d').dt.date
    return result[['SiteCode','SurveyDate','TripDate','Plane_Height','RunID','Area','Volume','Time_Series', 'Max_Area','Max_Vol']].sort_values(by=['SiteCode','SurveyDate'])

if __name__ == '__main__':
    
    data_formatter(in_file)
    

