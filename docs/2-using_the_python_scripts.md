# Running scripts
A number of python files can be run directly from the command line.

## Download data
Before using the algorithm, we need to make sure all required data is present in the `data/raw/` folder : annual 
demand excel/csv files from ETP/EDC, hourly load demands for countries, but also .csv hourly weather files.

More details in the `0-data_organization.md` file, but weather hourly data can be downloaded (for countries specified 
in the file) by running this script :
```
python src/data/download_data.py
```
Or manually downloaded here : https://www.renewables.ninja/.
Download manually US States Hourly Demand : https://www.eia.gov/opendata/qb.php?category=2122628

## Process data
If the rest of the required raw data is also present, you can process everything to get usable dataframes
```
python src/data/make_dataset.py
```
This will load, process and merge hourly historical load data, hourly historical weather data, annual demand data 
(historical and scenarios), and monthly temperature anomalies in scenario, into a single dataset for each scenario 
(in the `data/processed` folder).

## Train the model
You should now be able to start training the model, by running this :
```
# train the model, and plot average profiles for each country at the end of training
python src/models/train_model.py

# train the model, but don't plot profiles (significantly speeds up the run)
python src/models/train_model.py --skip_plot

# other command line options specific to pytorch lightning are also available, for instance, to have a quick test run 
# to check that there are no errors
python src/models/train_model.py --fast_dev_run=True
```

Many configurations options are located in this file, and can have an impact on the results, so they should be 
chosen carefully to ensure coherent outputs.

The `subsector_mapping` dict in particular defines
- the clustering of the subsectors
- the features used for each cluster (features come from the weather data processed in 
    `src/data/process_hourly_weather.py` and/or the `src/features/build_features.py` file)
- the temperature penalty (or penalties), with their threshold (temperature above/below which there is a penalty) 
    and their weight (higher weight : higher contribution to the total loss function)

The `hparams` dict contains a few hyper-parameters that configure the model and the training process. 
This dict will be saved automatically by pytorch-lightning before training, so we also use it to save a few other 
things such as the countries used for training, or the load scale factor `load_std`.
This way we can load previously trained model and run them the way there are supposed to be run to make predictions.

The training process first trains a shared model on all the data, from all countries. 
Then, for each country, we load the trained shared model and continue the training, but on data from this country only, 
to obtain a country-specific model.
The trained models, the hyper params, and optionally the average load profiles are saved in a new folder in `models/logs`

## Make predictions
To make predictions on processed data from a scenario (e.g `SDS2050`, `STEPS2050` or even `historical`), using models 
trained from the experiment with version number `<V_NB>`, run 
```
# by default, try to apply res/non-res cooling load separation
python src/models/predict_model.py --scenario <SCENARIO> --version_number <V_NB>

# but you can choose not to (and keep CLU_SC as a subsector)
python src/models/predict_model.py --scenario <SCENARIO> --version_number <V_NB> --no_separation
```


# More interaction using the jupyter notebooks
If you want more flexibility and/or to prototype and experiment on the fly, with interactive feedback, or to present 
results and graphs, you can run everything inside jupyter notebooks

Navigate to the project's root directory (using `cd PATH/TO/DIRECTORY`) and start jupyter lab
```
jupyter lab
```

> (optional) If you want interactive graphs, you will need to follow the instructions here : 
> https://github.com/matplotlib/ipympl
> In short, with nodejs installed, run
> ```
> jupyter labextension install @jupyter-widgets/jupyterlab-manager
> jupyter lab build
> ```
