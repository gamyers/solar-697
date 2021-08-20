# Residential Adoption of Photovoltaic<br>Solar Electric Power Generation 
## SIADS-697 Capstone

**[Master of Applied Data Science](https://www.si.umich.edu/programs/master-applied-data-science-online)**  
**[School of Information](https://www.si.umich.edu/)**  
**[University of Michigan](https://umich.edu/)**  

## Project Collaborators
> Collin Brosko  
> Greg Myers  
> Robert Underhill  
> Monica Yen  


Table of contents
==============
   * [About](#about)  
   * [Project Goals](#goals)  
   * [Key Learning](#learning)  
   * [Python Environment](#enviro)  
   * [Usage](#usage)  
   * [Future Work](#future)  
   * [Credits & Interviews](#credits)  
   * [Licence](#MIT)  

## About<a name="about"/>

- Project Background  
The project is about gaining a better understanding of the numerous factors impacting the adoption of photovoltaic panels in the residential setting in order to determine which areas are most likely to see a growth in adoption, which areas could see increased adoption with changes to human-controlled factors, and which areas may be best avoided. We are looking to analyze changes in environmental factors due to climate change, the changing cost per Watt of energy versus utility rates, the impacts of policies and incentives as well as sentiment toward renewable energy and solar energy in particular. The output of this work is likely to be multi-faceted, incorporating predictions of adoption rates for regions, identification of weaknesses within a region, and ratings for investment potential within an area. This work is not intended to provide analysis of individual homes, but would rather benefit government, utility and business entities in assessing larger regions.  

- Project GitHub: [GitHub](https://github.com/gamyers/solar-697.git)  

## Project Goals<a name="goals"/>

Brief overall blurb

- Irradiance and Meteorological Data  
  - Provide irradiance data at the **ZIP Code** level, accessible via a portable **SQL** database.  
  - Provide **data trends** visualizations of irradiance and meteorological data.  
  - Provide basic **Exploratory Data Analysis** visualizations.  
  - Present all visualizations through an interactive dashboard [Solar Irradiance Data Explorer](https://pv-solar-697.herokuapp.com/) called SIDE-dash  

![SIDE-dash home page](images/side-dash-1.png)  

- Economics  

- Policy and Programmatic  


## Key Learning<a name="learning"/>

Brief overall blurb  

- Irradiance and Meteorological
The key learning from the collection of solar irradiance data is that the radiation at a given location is not fixed and is susceptible to a variety of influences beyond the seasonal tracking of the sun across the sky. Clouds, water vapor, smoke, dust, and other fine particulate matter all have a bearing on the solar radiation the ultimately arrives at the earth’s surface. Some of these influencers, while not individually indicated, do make themselves known through the “Trend View” on [SIDE-dash](https://pv-solar-697.herokuapp.com/). You are invited to visit and explore for yourself!


- Economics  

- Policy and Programmatic  


## Python Environment<a name="enviro"/>
**requirements.txt**
```
altair==4.2.0.dev0  
black==21.7b0  
causalinference==0.1.3  
dash-bootstrap-components==0.13.0  
dash==1.21.0  
isort==5.9.3  
jupyterlab==3.1.7  
jupyterlab_code_formatter==1.4.10  
logzero==1.7.0  
matplotlib==3.4.3  
numpy==0.19.5  
openpyxl==3.0.7  
pandas==1.3.1  
plotly=5.1.0  
pmdarima==1.8.2  
python==3.8  
rasterstats==0.15.0  
scikit-learn==0.24.2  
scipy==1.7.1  
statsmodels==0.12.2  
tornado==6.1  
tqdm==4.62.1  
umap-learn==0.5.0  
uszipcode==0.2.6  
vega-datasets==0.9.0  
```  
## Usage<a name="usage"/>

# SECTION UPDATE - GM
### Irradiance and Meteorological Data  
##### Database preparation  
A series of notebooks and a python script are used to ready the irradiance database. If needed the zipcode_import.ipynb notebook is used to move data from a CSV file of ZIP Code data into the geo_zipcodes.db database. This is generally no longer required.  

The zipcodes_get_geos.ipynb is used to query the geo_zipcodes.db and extract lat/lon coordinates for each ZIP Code pulled from a standard text file (one per line). This produces a YAML file that is used by the NREL API download script.  

The nsrdb_download.py has several responsibilities, the first of which is to instantiate the irradiance database and the two tables within. The ‘nsrdb’ table a standard “CREATE TABLE…” query and the ‘geo_zipcodes’ table is a simple “INSERT INTO…” query from the geo_zipcodes.db.  

The NREL API query process now begins requesting data for each ZIP Code for each year between 1998 and 2020. Each received CSV file is process and saved in two forms, a data file and a metadata file. Simultaneously, each data CSV is written to the ‘nsrdb’ table of the irradiance database and certain fields are extracted from the metadata and inserted into the ‘geo_zipcodes’ table and the geo_zipcode.db database.  

The current final step is to execute the nsrdb_aggregator notebook which, at present, performs the initial steps of the nsrdb_download script. Rather than querying the NREL API, the saved raw data is processed into monthly aggregated data and saved to a database similar to that created by nsrdb_download.  

A future project will be to combine the API download and aggregation into a single process, for multiple aggregation levels.  

Because of the volume of data brought down from [NREL API server](https://developer.nrel.gov/docs/solar/nsrdb/psm3-download/), directory structures outside the bound of this repo are utilized. As such immediate execution of the database preparation notebooks and scripts is not possible without certain setup work; primarily the creation of directory structure to house CSV downloads and intermediate databases.  

# SECTION UPDATE - GM
##### Dashboard
Please be patient when first accessing SIDE-dash, the initial standup on [Heroku](https://heroku.com/) may take 30-seconds or so to load.  

The dashboard should load to the EDA page which presents two dropdowns for data selection. The first is for database selection of which there is currently one available on the Heroku sight. The second dropdown allows for the selection of a ZIP Code and the data behind it. The EDA page presents four views, Irradiance Data, Distribution, Meteorological, and Descriptive Statistics. The Data Trends page has like dropdowns for data selection.  

![SIDE-dash home page](images/side-dash-2.png)  

The Forecasting page adds a third dropdown for selecting the specific data feature on which to forecast. Note that the Forecasting page defaults to not perform a traditional Seasonal Differencing forecast. The traditional method is computationally much more expensive than the Fast Fourier Transform method and should generally be avoided on the Heroku "free" platform.  

### Economics



### Policy and Programmatic

## Future Work<a name="future"/>
##### Irradiance data and Dashboard  
  - Feature aggregations
    - Period totals for irradiance data
    - The inclusion of cloud cover data
  - Daily, Weekly and Monthly aggregation datasets
  - Additional non-traditional time-series forecasting models
    - LSTM
    - XGBoost
  - UI improvements
    - City/State ZIP Code filtering
    - Connect dashboard pages by selected ZIP Code values
    - Links to external sources such as NREL
    - Rollover help popups to provide guidance to the visualizations
  - Process  
    - Fully pipeline the data download and database create process  

##### Next Subject


## Credits & Interviews<a name="credits"/>
> First one here  
> Thank you to Rusty Haynes of [Smart Electric Power Alliance](https://sepapower.org) for his time and insights into solar data collection.  
> Thank you to Meredith Wan and her [TDS](https://towardsdatascience.com/beginners-guide-to-building-a-multi-page-dashboard-using-dash-5d06dbfc7599) article that inspired me to create [SIDE-dash](https://pv-solar-697.herokuapp.com/) on Heroku.  
> [National Renewable Energy Laboratory](https://www.nrel.gov/index.html) and [National Solar Radiation Database](https://nsrdb.nrel.gov/).  
> more  
> another  
> last one  

## License<a name="MIT"/>
[MIT](LICENSE)