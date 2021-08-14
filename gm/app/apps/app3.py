#!/usr/bin/env python3

import os
import sqlite3
import sys

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import logzero
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import yaml
from app import app
from dash.dependencies import Input, Output
from dash_table import DataTable
from logzero import logger
from pmdarima import model_selection
# from yaml import dump, load, safe_load

# app source path additions
sys.path.append("./source")
sys.path.append("../../sql")
sys.path.append("../source")
sys.path.append("../.")

import plot_tools
import pmd_plot_tools
import pmd_tools
import queries
import ts_tools

pd.set_option("plotting.backend", "plotly")

# open and retrieve configuration information
configs = None
try:
    with open("../configs/config.yml", "r") as config_in:
        configs = yaml.load(config_in, Loader=yaml.SafeLoader)
        logger.info(f"{configs}\n")
except:
    logger.error(f"config file open failure.")
    exit(1)

cfg_vars = configs["url_variables"]
logger.info(f"variables: {cfg_vars}\n")

years = configs["request_years"]
logger.info(f"years: {years}\n")

db_path = configs["file_paths"]["db_path"]

city = configs["location_info"]["city"]
state = configs["location_info"]["state"]
db_file = city + "_" + state + ".db"
db_file = "nsrdb_monthly.db"

db_table1 = configs["table_names"]["db_table1"]
db_table2 = configs["table_names"]["db_table2"]

logger.info(f"{db_path}, {db_file}")

data_units = configs["data_units"]
meteoro_fields = configs["meteorological_fields"]
viz_pages = configs["viz_page_options"]

nrows = configs["num_rows"][0]
logger.info(f"number of rows: {nrows}\n")

db_files = ts_tools.get_db_files(db_path)
logger.info(f"DB Path: {db_path}\n{db_files}\n")

# define app3 page layout
layout_app3 = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="app3-dd-db-selection",
                        options=[{"label": db, "value": db} for db in db_files],
                        value="nsrdb_monthly.db",
                        placeholder="Select a database",
                    ),
                    width={"size": 2, "offset": 0},
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="app3-dd-zipcode-selection",
                        placeholder="Select a Zip Code",
                    ),
                    width={"size": 2, "offset": 1},
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="app3-dd-feature-selection",
                        placeholder="Select a Feature",
                    ),
                    width={"size": 2, "offset": 1},
                ),
            ],
            no_gutters=False,
        ),
        dbc.Row(
            dbc.Col(
                [
                    dcc.Graph(id="app3-graph-arima-1"),
                    dcc.Graph(id="app3-graph-arima-2"),
                ],
                width={"size": 11, "offset": 0},
            )
        ),
    ]
)


#--------------------------begin callbacks--------------------------#

@app.callback(
    Output("app3-dd-zipcode-selection", "options"),
    [
        Input("app3-dd-db-selection", "value"),
    ],
)
def get_zipcodes(file_name):
    logger.info(f"get_zipcodes callback: {file_name}")

    conn = ts_tools.get_db_connection(db_path, file_name)
    zipcodes = ts_tools.get_db_zipcodes(conn)
    conn.close()

    logger.info(f"app3 zipcodes retrieved\n{zipcodes}")

    # return the list object to properly populate the dropdown!
    return [{"label": zipcode, "value": zipcode} for zipcode in zipcodes]


@app.callback(
    Output("app3-dd-zipcode-selection", "value"),
    [
        Input("app3-dd-zipcode-selection", "options"),
    ],
)
def set_zipcode_value(options):
    logger.info(f"app3 zipcode selected: {options[0]['value']}")
    return options[0]["value"]

#-------------------------------------------------------------------#

@app.callback(
    Output("app3-dd-feature-selection", "options"),
    [
        Input("app3-dd-db-selection", "value"),
    ],
)
def get_features(file_name):
    logger.info(f"get_features callback")

    conn = ts_tools.get_db_connection(db_path, file_name)
    col_names = ts_tools.get_column_names(conn, configs["table_names"]["db_table1"])
    conn.close()

    logger.info(f"app3 column names:\n{col_names}")
    
    column_names = []

    for name in col_names:
        if name in configs["drop_columns"]:
            continue
        column_names.append(name)

    logger.info(f"app3 feature names: {column_names}")
        
    # return the list object to properly populate the dropdown!
    return [{"label": column, "value": column} for column in column_names]


@app.callback(
    Output("app3-dd-feature-selection", "value"),
    [
        Input("app3-dd-feature-selection", "options"),
    ],
)
def set_feature_value(options):
    logger.info(f"app3 feature selected: {options[0]['value']}")
    return options[0]["value"]

#-------------------------------------------------------------------#

@app.callback(
    # Output("app3-graph-arima-1", "figure"),
    [
        Output("app3-graph-arima-1", "figure"),
        Output("app3-graph-arima-2", "figure"),
    ],
    [
        Input("app3-dd-db-selection", "value"),
        Input("app3-dd-zipcode-selection", "value"),
        Input("app3-dd-feature-selection", "value"),
        # Input("app3-dd-fc-period-selection", "value"),
    ],
)
def graph_output(db_filename, zipcode, feature_selection):

    cntx = dash.callback_context
    context = cntx.triggered[0]["prop_id"].split(".")[0]
    logger.info(f"app3 graph_output #1 Context = {context}\n")
    
    feature = feature_selection

    if context == "app3-dd-db-selection":
        conn = ts_tools.get_db_connection(db_path, db_filename)
        zipcodes = ts_tools.get_db_zipcodes(conn)
        zipcode = zipcodes[0]
        locale_data = ts_tools.get_locale_data(conn, zipcode)
        df = ts_tools.get_irr_data(conn, zipcode)
        logger.info(f"app3 Made if: {db_filename}, {zipcode}")

    elif context == "app3-dd-zipcode-selection":
        # print(f"Made elif: {db_filename}, {zipcode}")
        conn = ts_tools.get_db_connection(db_path, db_filename)
        locale_data = ts_tools.get_locale_data(conn, zipcode)
        df = ts_tools.get_irr_data(conn, zipcode)
        logger.info(f"app3 Made elif: {db_filename}, {zipcode}")

    elif context == "app3-dd-feature-selection":
        # print(f"Made elif: {db_filename}, {zipcode}")
        conn = ts_tools.get_db_connection(db_path, db_filename)
        locale_data = ts_tools.get_locale_data(conn, zipcode)
        df = ts_tools.get_irr_data(conn, zipcode)
        feature = feature_selection
        logger.info(f"app3 Made 2nd elif: {feature}")
        
    else:
        db_filename = db_files[0]
        conn = ts_tools.get_db_connection(db_path, db_filename)
        zipcodes = ts_tools.get_db_zipcodes(conn)
        zipcode = zipcodes[0]
        locale_data = ts_tools.get_locale_data(conn, zipcode)
        df = ts_tools.get_irr_data(conn, zipcode)
        logger.info(f"app3 Made else: {db_filename}, {zipcode}")

    logger.info(f"app3 passed if/elif/else")

    test_len_yrs = 5
    test_periods = 5 * 12
    fc_periods = 5 * 12
    
    logger.info(f"app3 parameters: {test_len_yrs}, {test_periods}, {fc_periods}, {feature}")
    
    train, test = model_selection.train_test_split(df, test_size=test_periods)
    logger.info(train.tail(5))
    logger.info(test.head(5))

    fft_model = pmd_tools.get_arima_fft_model(train[feature], fc_periods)
    logger.info(fft_model)
    
    forecast, conf_int = fft_model.predict(n_periods=fc_periods, return_conf_int=True)
    forecast = pd.Series(forecast, index=test.index)
    
    logger.info(f"Len of train {len(train)}")
    logger.info(f"Len of test {len(test)}")
    logger.info(f"Len of forecast {len(forecast)}")
    logger.info(f"forecast: {forecast.head(10)}")    

    title1 = f"{feature}, FFT,"
    fig1 = pmd_plot_tools.plot_forecast(
        train[feature],
        test[feature],
        forecast,
        title=title1,
        zipcode=zipcode,
    )
    logger.info(f"app3 passed {title1}")
    
    auto_model = pmd_tools.get_arima_auto_model(train[feature], fc_periods)
    logger.info(auto_model)
    
    forecast, conf_int = auto_model.predict(n_periods=fc_periods, return_conf_int=True)
    forecast = pd.Series(forecast, index=test.index)    

    title2 = f"{feature}, Diff,"
    fig2 = pmd_plot_tools.plot_forecast(
        train[feature],
        test[feature],
        forecast,
        title=title2,
        zipcode=zipcode,
    )
    logger.info(f"app3 passed {title2}")

    return fig1, fig2
