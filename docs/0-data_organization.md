# Data organization and sources
`data/` is the `data_root`
- `external`
    - `weo_results` contains hourly load data by subsector from WEO model runs. It can be used to make comparisons, validity checks, etc. Also used to separate residential from non-residential data, for the space cooling cluster
- `mapping`
    - `country_mapping.csv` contains all the data regarding countries to process, and what data to use.
    Rows that are not complete (e.g. Iceland, as we are missing hourly weather data) will be ignored
        - `country` is how the country will be referred. 
        It is also the country identifier used to load data from the etp_inputs file.
        For non-total loads (e.g. enedis sector loads in France), a row can be added with a different `country` name,
        but adjustments to the load will have to be made during data processing
        - `ISO_2_digits` used to load the country weather data
        - `edc_country_name` the country's identifier in EDC data
        - `timezone` can be found here https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        - `load_data_name` name of the load data column in the processed hourly load dataset.
        For ENTSO-E data, name of the column in the original (raw) dataset, for other countries it's defined during
        data processing
    - `sector_mapping.csv` maps EDC subsectors (e.g Iron and steel) to our subsectors names (e.g IND_IS). Only subsectors listed in this file are used (which is why there is no RES/SER data, as we are using ETP data for that). 
- `processed` : processed data, after running the `make_dataset.py` script
- `raw`
    - `annual_demand` : annual demand data for historical and future years. For historical years, currently using EDC data for industry/transport (to have a country-level spatial resolution), and ETP data for buildings (to have more details in the subsectors). ETP scenario data is required for future years for all sectors, so some spatial disaggregation may be necessary in Excel here. 
    - `explanatory_variables` : hourly inputs to the model (temperature, solar irradiance, etc). 
    Weather files for every country can be downloaded at 
    `https://www.renewables.ninja/country_downloads/<CC>/ninja_weather_country_<CC>_merra-2_population_weighted.csv`
    where `<CC>` is the 2 digits country code, e.g. `FR` (or the region code e.g. `US.CA` for California).
    The `src/data/download_data.py` script automates this.
    Spatial aggregation is population weighted, and underlying data comes from the MERRA-2 reanalysis dataset
    - `hourly_demand`
        - `Singapore` : Excel files with hourly demand for a whole week can be found at 
        `https://www.ema.gov.sg/statistic.aspx?sta_sid=20140826Y84sgBebjwKV`.
        This dataset `https://data.gov.sg/dataset/half-hourly-system-demand` has already done the aggregation 
        (using the same data source) from 2012 up to June 2016. For more recent data, we aggregate the excel files
        with week-long hourly data in `process_hourly_load.py`
        - `time_series_60min_singleindex.csv` : hourly demand data (along with other variables that we don't use) 
        for some European countries, based on ENTSO-E data. https://data.open-power-system-data.org/time_series/
    - `scenarios_anomalies` : csv files from Chiara, with monthly temperature anomalies for countries/ETP regions, for a given future year and RCP scenario


**Notes**
- Subsectors name in the raw data (from ETP/EDC, before clustering) need to have a specific format : `IND_**`, `RES_**`, `SER_**`, `TRA_**`, `CLU_**` where `**` is 2 (or more) capital letters or digits.
For instance, `RES_SC` for residential space cooling. This is required (and can be changed) in `src/data/load_processed_data.py`, in order to find the subsectors in the columns of the processed dataframe
