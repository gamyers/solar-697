#!/usr/bin/env python3

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

sys.path.append("../../sql")
import queries

sys.path.append("./source")
import plot_tools
import ts_tools

# open and retrieve configuration data
try:
    with open("config.yml", "r") as config_in:
        cfg = yaml.load(config_in, Loader=yaml.SafeLoader)
        logger.info(f"{cfg}\n")
except:
    logger.error(f"config file open failure.")
    exit(1)

db_path = cfg["file_paths"]["db_path"]
db_files = ts_tools.get_db_files(db_path)
logger.info(f"DB Path: {db_path}\n{db_files}\n")

# --------------------------begin layout--------------------------#
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
                        persistence=True,
                    ),
                    width={"size": 2, "offset": 0},
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="app2-dd-zipcode-selection",
                            placeholder="Select a Zip Code",
                            persistence=True,
                        ),
                        html.H5(id="app2-dd-zipcode-selection-locale"),
                    ],
                    width={"size": 2, "offset": 1},
                ),
            ],
        ),
        dbc.Row(
            dbc.Col(
                dcc.Graph(id="app2-graph-trend-1"),
                width={"size": 11, "offset": 0},
            )
        ),
    ]
)


# --------------------------begin callbacks--------------------------#
@app.callback(
    Output("app2-dd-zipcode-selection", "options"),
    Input("app2-dd-db-selection", "value"),
)
def get_zipcodes(file_name):
    logger.info(f"get_zipcodes callback: {file_name}")

    conn = ts_tools.get_db_connection(db_path, file_name)
    zipcodes = ts_tools.get_db_zipcodes(conn)
    conn.close()

    logger.info(f"app2 zipcodes retrieved\n{zipcodes}")

    # return the list object to properly populate the dropdown!
    return [{"label": zipcode, "value": zipcode} for zipcode in zipcodes]


# -------------------------------------------------------------------#
# @app.callback(
#     Output("app2-dd-zipcode-selection", "value"),
#     [
#         Input("app2-dd-zipcode-selection", "options"),
#     ],
# )
# def set_zipcode_value(options):
#     logger.info(f"app2 zipcode selected: {options[0]['value']}")
#     return options[0]["value"]

# -------------------------------------------------------------------#
@app.callback(
    Output("app2-graph-trend-1", "figure"),
    Output("app2-dd-zipcode-selection-locale", "children"),
    Input("app2-dd-db-selection", "value"),
    Input("app2-dd-zipcode-selection", "value"),
)
def graph_output(db_filename, zipcode):

    cntx = dash.callback_context
    context = cntx.triggered[0]["prop_id"].split(".")[0]
    logger.info(f"app2 graph_output #1 Context = {context}\n")

    if context == "app2-dd-db-selection":
        conn = ts_tools.get_db_connection(db_path, db_filename)
        # zipcodes = ts_tools.get_db_zipcodes(conn)
        # zipcode = zipcodes[0]
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
        db_filename = cfg["file_names"]["default_db"]
        conn = ts_tools.get_db_connection(db_path, db_filename)
        zipcodes = ts_tools.get_db_zipcodes(conn)
        if not zipcode:
            zipcode = zipcodes[0]
        locale_data = ts_tools.get_locale_data(conn, zipcode)
        df = ts_tools.get_irr_data(conn, zipcode)
        logger.info(f"app2 Made else: {db_filename}, {zipcode}")

    logger.info(f"app2 passed if/elif/else")

    title1 = "Trend Data (decomposed)"
    fig1 = plot_tools.plot_trends(
        df,
        title=title1,
        zipcode=zipcode,
        locale=locale_data,
    )
    logger.info(f"app2 passed {title1}")

    return (
        fig1,
        f"{locale_data[0]}, {locale_data[2]}",
    )
