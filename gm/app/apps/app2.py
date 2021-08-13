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

# from yaml import dump, load, safe_load

sys.path.append("../../sql")
sys.path.append("../source")
sys.path.append("../.")
import plot_tools
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

# define app2 page layout
layout_app2 = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="app2-dd-db-selection",
                        options=[{"label": db, "value": db} for db in db_files],
                        value="nsrdb_monthly.db",
                        placeholder="Select a database",
                    ),
                    width={"size": 2, "offset": 0},
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="app2-dd-zipcode-selection",
                        placeholder="Select a Zip Code",
                    ),
                    width={"size": 2, "offset": 1},
                ),
            ],
            no_gutters=False,
        ),
        dbc.Row(
            dbc.Col(
                [
                    dcc.Graph(id="app2-graph-trend-1"),
                    # dcc.Graph(id="app2-graph-trend-2"),
                ],
                width={"size": 11, "offset": 0},
            )
        ),
    ]
)


# begin callbacks
@app.callback(
    Output("app2-dd-zipcode-selection", "options"),
    [
        Input("app2-dd-db-selection", "value"),
    ],
)
def get_zipcodes(file_name):
    logger.info(f"get_zipcodes callback: {file_name}")

    conn = ts_tools.get_db_connection(db_path, file_name)
    zipcodes = ts_tools.get_db_zipcodes(conn)
    conn.close()

    logger.info(f"app2 zipcodes retrieved\n{zipcodes}")

    # return the list object to properly populate the dropdown!
    return [{"label": zipcode, "value": zipcode} for zipcode in zipcodes]


@app.callback(
    Output("app2-dd-zipcode-selection", "value"),
    [
        Input("app2-dd-zipcode-selection", "options"),
    ],
)
def set_zipcode_value(options):
    logger.info(f"app2 zipcode selected: {options[0]['value']}")
    return options[0]["value"]


@app.callback(
    Output("app2-graph-trend-1", "figure"),
#     [
#         Output("app2-graph-trend-1", "figure"),
#         Output("app2-graph-trend-2", "figure"),
#     ],
    [
        Input("app2-dd-db-selection", "value"),
        Input("app2-dd-zipcode-selection", "value"),
    ],
)
def graph_output(db_filename, zipcode):

    cntx = dash.callback_context
    context = cntx.triggered[0]["prop_id"].split(".")[0]
    logger.info(f"app2 graph_output #1 Context = {context}\n")

    if context == "app2-dd-db-selection":
        conn = ts_tools.get_db_connection(db_path, db_filename)
        zipcodes = ts_tools.get_db_zipcodes(conn)
        zipcode = zipcodes[0]
        locale_data = ts_tools.get_locale_data(conn, zipcode)
        df = ts_tools.get_irr_data(conn, zipcode)
        logger.info(f"app2 Made if: {db_filename}, {zipcode}")

    elif context == "app2-dd-zipcode-selection":
        # print(f"Made elif: {db_filename}, {zipcode}")
        conn = ts_tools.get_db_connection(db_path, db_filename)
        locale_data = ts_tools.get_locale_data(conn, zipcode)
        df = ts_tools.get_irr_data(conn, zipcode)
        logger.info(f"app2 Made elif: {db_filename}, {zipcode}")

    else:
        db_filename = db_files[0]
        conn = ts_tools.get_db_connection(db_path, db_filename)
        zipcodes = ts_tools.get_db_zipcodes(conn)
        zipcode = zipcodes[0]
        locale_data = ts_tools.get_locale_data(conn, zipcode)
        df = ts_tools.get_irr_data(conn, zipcode)
        logger.ifno(f"app2 Made else: {db_filename}, {zipcode}")

    logger.info(f"app2 passed if/elif/else")
    
    title1 = "Data Trends"
    fig1 = plot_tools.plot_trends(
        df,
        title=title1,
        zipcode=zipcode,
        units=data_units,
    )
    logger.info(f"app2 passed {title1}")

    #     title2 = "Trend 2"
    #     fig2 = plot_tools.plot_histograms(
    #         df,
    #         title=title2,
    #         zipcode=zipcode,
    #     )
    #     logger.info(f"app2 passed {title2}")

    #     title3 = "Meteorological Conditions"
    #     fig3 = plot_tools.plot_multi_line(
    #         df,
    #         title=title3,
    #         locale=locale_data,
    #         columns=meteoro_fields,
    #     )

    return fig1 # , fig2  # , fig3
