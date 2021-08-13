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


layout_app1 = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="dd-db-selection",
                        options=[{"label": db, "value": db} for db in db_files],
                        value="nsrdb_monthly.db",  # db_files[0],
                        placeholder="Select a database",
                    ),
                    width={"size": 2, "offset": 0},
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="dd-zipcode-selection",
                        placeholder="Select a Zip Code",
                    ),
                    width={"size": 2, "offset": 1},
                ),

            ],
            no_gutters=False,
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label(
                            "Data View",
                            style={"display": "inline-block", "textAlign": "center"},
                        ),
                        dcc.Graph(
                            id="graph-data-view",
                        ),
                    ],
                    width={"size": 6, "offset": 0},
                ),
                dbc.Col(
                    [
                        html.Label(
                            "Distribution View",
                            style={"display": "inline-block", "textAlign": "center"},
                        ),
                        dcc.Graph(
                            id="graph-dist-view",
                        ),
                    ],
                    width={"size": 5},
                ),
            ],
            no_gutters=True,
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label(
                            "Meteorological View",
                            style={"display": "inline-block", "textAlign": "center"},
                        ),
                        dcc.Graph(
                            id="graph-meteoro-view",
                        ),
                    ],
                    width={"size": 6, "offset": 0},
                ),
                dbc.Col(
                    [
                        html.Label(
                            "Desciptive Statistics",
                            style={
                                "display": "inline-block",
                                "textAlign": "center",
                            },
                        ),
                        DataTable(
                            id="table-desc-stats",
                            style_cell={
                                "padding": "5px",
                                "backgroundColor": "black",
                                "forgroundColor": "white",
                                "fontWeight": "bold",
                            },
                            style_header={
                                "padding": "5px",
                                "backgroundColor": "black",
                                "forgroundColor": "white",
                                "fontWeight": "bold",
                            },
                        ),
                    ],
                    width={"size": 5},
                ),
            ],
        ),
    ],
)
# end of layout

#

# begin callbacks
@app.callback(
    Output("dd-zipcode-selection", "options"),
    [
        Input("dd-db-selection", "value"),
    ],
)
def get_zipcodes(file_name):
    logger.info(f"get_zipcodes callback: {file_name}")

    conn = ts_tools.get_db_connection(db_path, file_name)
    zipcodes = ts_tools.get_db_zipcodes(conn)
    conn.close()

    logger.info(f"app1 zipcodes retrieved\n{zipcodes}")
    
    # return the list object to properly populate the dropdown!
    return [{"label": zipcode, "value": zipcode} for zipcode in zipcodes]


@app.callback(
    Output("dd-zipcode-selection", "value"),
    [
        Input("dd-zipcode-selection", "options"),
    ],
)
def set_zipcode_value(options):
    logger.info(f"app1 zipcode selected: {options[0]['value']}")
    return options[0]["value"]


@app.callback(
    [
        Output("graph-data-view", "figure"),
        Output("graph-dist-view", "figure"),
        Output("graph-meteoro-view", "figure"),
        Output("table-desc-stats", "data"),
        Output("table-desc-stats", "columns"),
    ],
    [
        Input("dd-db-selection", "value"),
        Input("dd-zipcode-selection", "value"),
    ],
)
def graph_output(db_filename, zipcode):

    cntx = dash.callback_context
    context = cntx.triggered[0]["prop_id"].split(".")[0]
    logger.info(f"app1 graph_output #1 Context = {context}\n")

    if context == "dd-db-selection":
        conn = ts_tools.get_db_connection(db_path, db_filename)
        zipcodes = ts_tools.get_db_zipcodes(conn)
        zipcode = zipcodes[0]
        locale_data = ts_tools.get_locale_data(conn, zipcode)
        df = ts_tools.get_irr_data(conn, zipcode)
        logger.info(f"app1 Made if: {db_filename}, {zipcode}")

    elif context == "dd-zipcode-selection":
        conn = ts_tools.get_db_connection(db_path, db_filename)
        locale_data = ts_tools.get_locale_data(conn, zipcode)
        df = ts_tools.get_irr_data(conn, zipcode)
        logger.info(f"app1 Made elif: {db_filename}, {zipcode}")

    else:
        db_filename = db_files[0]
        conn = ts_tools.get_db_connection(db_path, db_filename)
        zipcodes = ts_tools.get_db_zipcodes(conn)
        zipcode = zipcodes[0]
        locale_data = ts_tools.get_locale_data(conn, zipcode)
        df = ts_tools.get_irr_data(conn, zipcode)
        logger.info(f"app1 Made else: {db_filename}, {zipcode}")
        
    logger.info(f"app1 passed if/elif/else")        

    df_desc = df.describe().transpose().round(decimals=2).reset_index(drop=False)
    desc_columns = [{"id": col, "name": col} for col in df_desc.columns]
    
    logger.info(f"app1 passed df_desc")

    title1 = "Irradiance Data"
    fig1 = plot_tools.plot_data(
        df,
        title=title1,
        zipcode=zipcode,
        units=data_units,
    )
    logger.info(f"app1 passed {title1}")

    title2 = "Data Distributions"
    fig2 = plot_tools.plot_histograms(
        df,
        title=title2,
        zipcode=zipcode,
    )
    logger.info(f"app1 passed {title2}")

    title3 = "Meteorological Conditions"
    fig3 = plot_tools.plot_multi_line(
        df,
        title=title3,
        locale=locale_data,
        columns=meteoro_fields,
    )
    logger.info(f"app1 passed {title3}")
    
    logger.info(f"app1 graph_output return")

    return fig1, fig2, fig3, df_desc.to_dict("records"), desc_columns
