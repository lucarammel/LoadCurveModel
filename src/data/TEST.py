# -*- coding: utf-8 -*-
"""
Created on Thu Jul  8 15:59:51 2021

@author: PEREIRA_LU
"""


import os 
os.environ['KMP_DUPLICATE_LIB_OK']='True' 

#%%
from pathlib import Path




import yaml

import pandas as pd
pd.set_option("display.max_columns",None)

import numpy as np

from src.data.merge_hourly import merge_hourly_weather_and_load, interpolate_missing_timestamps
from src.data.process_annual_demand import process_historical_annual_data, process_scenarios_annual_data
from src.data.process_hourly_load import process_historical_hourly_load, data_augmentation_CL
from src.data.process_hourly_weather import process_historical_hourly_weather
from src.data.process_scenarios_anomalies import process_scenarios_anomalies
from src.data.process_hourly_load import load_and_process_wem_inputs_hourly
from src.features.build_features import compute_features



#%%
data_root = Path(__file__).resolve().parents[2]
data_root = data_root.joinpath('data')


not_use_wem_inputs = False
split_week_end = True
pop_weighted =  True
with open(data_root.parent.absolute().joinpath('models/logs/subsector_mapping.yaml'),'r') as file : 
        subsector_mapping = yaml.safe_load(file)
        sector = list(subsector_mapping.keys())
missing_features = ['load'] + sector

df_annual_demand = process_historical_annual_data(data_root)
hourly_weather_dict = process_historical_hourly_weather(data_root, drop_before_year=2002)
if not_use_wem_inputs :
    hourly_load_dict = process_historical_hourly_load(data_root)
    df_hourly = merge_hourly_weather_and_load(data_root=data_root, hourly_weather_dict=hourly_weather_dict,
                                              hourly_load_dict=hourly_load_dict, not_use_wem_inputs = True,split_week_end = split_week_end)
else : 
    hourly_load_dict = process_historical_hourly_load(data_root)
    df_hourly_load = load_and_process_wem_inputs_hourly(data_root = data_root,df_hist_annual = df_annual_demand, pop_weighted = pop_weighted)
    hourly_load_dict_wem = data_augmentation_CL(df_hourly_load = df_hourly_load, missing_features = missing_features, get_dict = True)
    
country_mapping_path = data_root.joinpath('mapping/country_mapping.csv')

#%% Merge hourly
country_mapping_path = data_root.joinpath('mapping/country_mapping.csv')

country_mapping = pd.read_csv(country_mapping_path)
    # Drop countries where we are missing weather datasets
country_mapping.dropna(subset=['ISO_2_digits'], inplace=True)
    # Get the names of the dataset to use, for every countries
timezones = country_mapping.set_index('country').to_dict()['timezone']
c = 'US_FL'
data_frames = []
for country in hourly_weather_dict.keys():
    if country == c : 
        # We need at least weather data (as it's a required input), but it's not a problem if we are
        # missing load data (e.g. to use the model, in scenarios predictions)
        df_weather = hourly_weather_dict[country]
        if not_use_wem_inputs : 
            df_load_actual = hourly_load_dict.get(country, pd.DataFrame(columns=['utc_timestamp', 'load']))
            df_country = pd.merge(df_weather, df_load_actual, how='left', on='utc_timestamp')
        else : 
            with open(data_root.parent.absolute().joinpath('models/logs/subsector_mapping.yaml'),'r') as file : 
                subsector_mapping = yaml.safe_load(file)
                sector = list(subsector_mapping.keys())
            df_load = hourly_load_dict_wem.get(country, pd.DataFrame(columns=['utc_timestamp','load'] + sector))
            df_load_actual = hourly_load_dict.get(country, pd.DataFrame(columns=['utc_timestamp', 'load']))
            df_country = pd.merge(df_weather, df_load, how='left', on='utc_timestamp')
            df_country.drop(columns = 'load',inplace = True) #Don't use the total load of the WEM model but the total actual load
            df_country = pd.merge(df_country,df_load_actual, how = 'left', on = 'utc_timestamp')
        df_country = interpolate_missing_timestamps(df_country, timezone=timezones[country], country=country, not_use_wem_inputs =not_use_wem_inputs)   
        df_country = compute_features(df_country, country = country,split_week_end = split_week_end)
        df_country['country'] = country
        data_frames.append(df_country)
        
df = pd.concat(data_frames, ignore_index=True, sort=False)
#%% Interpolate missing timestamps
df_country['local_timestamp'] = df_country.utc_timestamp.dt.tz_convert(timezones[c])
    # Outlier (outage ?) : almost 0 load, better to interpolate as if it was a missing value

if country == 'NOR':
    df_country.loc[df_country.utc_timestamp == '2010-12-09 19:00:00+00:00', 'load'] = np.nan
    
# Locate missing data : complete the DateTimeIndex so that we always have full years (8760 or 8784 hours)
# in local time.
# This will mark missing load data (e.g. at the beginning/end of the year, or during blackouts) as NaN
# instead of simply having a missing row, in order to interpolate and fill this NaN data later.
full_index = pd.date_range(start=f'{int(df_country.local_timestamp.dt.year.min())}-01-01 00:00:00',
                               end=f'{int(df_country.local_timestamp.dt.year.max())}-12-31 23:00:00',
                               tz=timezones[c], freq='1H')
try :
    df_country = df_country.set_index('local_timestamp').reindex(index=full_index).reset_index().rename(
            columns={'index': 'local_timestamp'})  
except ValueError : 
    df_country = df_country.set_index('local_timestamp')
    df_country = df_country.loc[~df_country.index.duplicated(),:]
    df_country = df_country.reindex(index=full_index).reset_index().rename(columns={'index': 'local_timestamp'})   
    
    # Fill the gaps in utc timestamps with the right values
df_country.utc_timestamp = df_country.local_timestamp.dt.tz_convert('UTC')
    # Fill the gaps in load data
    
df_country.loc[:, 'load'] = df_country.loc[:, 'load'].interpolate(limit_direction='both', method='cubic',
                                                                      limit=24).fillna(method='bfill', limit=2)
df_country.loc[:,'load'] = df_country.loc[:,'load'].fillna(method='bfill', limit=).fillna(method='ffill', limit=2)

if not_use_wem_inputs : 
    df_country.dropna(inplace=True)

#%%get full year data only 

df = df[df.day_of_year < 366]

    # Locate the years with missing load data
df_count = df.groupby(['country', 'year']).load.count()
df_incomplete_years = df_count[df_count != 8760]
print(df_count)