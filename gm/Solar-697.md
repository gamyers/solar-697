# Title - 
## SIADS-697 Capstone Project

[![N|Solid](https://cldup.com/dTxpPi9lDf.thumb.png)](https://nodesource.com/products/nsolid)

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

Dillinger is a cloud-enabled, mobile-ready, offline-storage compatible,
AngularJS-powered HTML5 Markdown editor.


## Project Collaborators
- Collin Brosko
- Greg Myers
- Robert Underhill
- Monica Yen


## About

- Project background


Markdown is a lightweight markup language based on the formatting conventions
that people naturally use in email.
As [John Gruber] writes on the [Markdown site][df1]

> The overriding design goal for Markdown's


## Goals

Brief overall blurb

- Irradiance and Meteorological
- Economics
- Policy and Programmatic
- [Dashboard](https://pv-solar-697.herokuapp.com/) - HTML

And of course Dillinger itself is open source with a [public repository][dill]
 on GitHub.

## Key Learnings

Brief overall blurb

- Irradiance and Meteorological
- Economics
- Policy and Programmatic

Dillinger requires [Node.js](https://nodejs.org/) v10+ to run.


```python
xyz = 5
npm i
node app
```



## Python Environment Requirements

Dillinger is currently extended with the following plugins.
Instructions on how to use them in your own application are linked below.

| Plugin | README |
| ------ | ------ |
| Dropbox | [plugins/dropbox/README.md][PlDb] |
| GitHub | [plugins/github/README.md][PlGh] |
| Google Drive | [plugins/googledrive/README.md][PlGd] |
| OneDrive | [plugins/onedrive/README.md][PlOd] |
| Medium | [plugins/medium/README.md][PlMe] |
| Google Analytics | [plugins/googleanalytics/README.md][PlGa] |

## Usage

#### Irradiance and Meteorological  
##### Database preparation  
A series of notebooks and a python script are used to ready the irradiance database. If needed the zipcode_import.ipynb notebook is used to move data from a CSV file of ZIP Code data into the geo_zipcodes.db database. This is generally no longer required.  

The zipcodes_get_geos.ipynb is used to query the geo_zipcodes.db and extract lat/lon coordinates for each ZIP Code pulled from a standard text file (one per line). This produces a YAML file that is used by the NREL API download script.  

The nsrdb_download.py has several responsibilities, the first of which is to instantiate the irradiance database and the two tables within. The ‘nsrdb’ table a standard “CREATE TABLE…” query and the ‘geo_zipcodes’ table is a simple “INSERT INTO…” query from the geo_zipcodes.db.  

The NREL API query process now begins requesting data for each ZIP Code for each year between 1998 and 2020. Each received CSV file is process and saved in two forms, a data file and a metadata file. Simultaneously, each data CSV is written to the ‘nsrdb’ table of the irradiance database and certain fields are extracted from the metadata and inserted into the ‘geo_zipcodes’ table and the geo_zipcode.db database.  

The current final step is to execute the nsrdb_aggregator notebook which, at present, performs the initial steps of the nsrdb_download script. Rather than querying the NREL API, the saved raw data is processed into monthly aggregated data and saved to a database similar to that created by nsrdb_download.  

A future project will be to combine the API download and aggregation into a single process, for multiple aggregation levels.  

#### Economics
#### Policy and Programmatic

First Tab:

```sh
node app
```

## Future Work

Dillinger is very easy to install and deploy in a Docker container.


#### Credits

Interviews

```sh
gulp build --prod
```





```sh
docker run -d -p 8000:8080 --restart=always --cap-add=SYS_ADMIN --name=dillinger <youruser>/dillinger:${package.json.version}
```

> Note: `--capt-add=SYS-ADMIN` is required for PDF rendering.

## License

MIT



   [dill]: <https://github.com/joemccann/dillinger>
   [git-repo-url]: <https://github.com/joemccann/dillinger.git>
   [john gruber]: <http://daringfireball.net>
   [df1]: <http://daringfireball.net/projects/markdown/>
   [markdown-it]: <https://github.com/markdown-it/markdown-it>
   [Ace Editor]: <http://ace.ajax.org>
   [node.js]: <http://nodejs.org>
   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>
   [jQuery]: <http://jquery.com>
   [@tjholowaychuk]: <http://twitter.com/tjholowaychuk>
   [express]: <http://expressjs.com>
   [AngularJS]: <http://angularjs.org>
   [Gulp]: <http://gulpjs.com>

   [PlDb]: <https://github.com/joemccann/dillinger/tree/master/plugins/dropbox/README.md>
   [PlGh]: <https://github.com/joemccann/dillinger/tree/master/plugins/github/README.md>
   [PlGd]: <https://github.com/joemccann/dillinger/tree/master/plugins/googledrive/README.md>
   [PlOd]: <https://github.com/joemccann/dillinger/tree/master/plugins/onedrive/README.md>
   [PlMe]: <https://github.com/joemccann/dillinger/tree/master/plugins/medium/README.md>
   [PlGa]: <https://github.com/RahulHP/dillinger/blob/master/plugins/googleanalytics/README.md>
