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
layout_app1 = html.Div(
    [
        # Dropdown row 0
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="dd-db-selection",
                        options=[{"label": db, "value": db} for db in db_files],
                        value=cfg["file_names"]["default_db"],
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
        ),
        # Plots row 1
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H6(
                            "Data View",
                            style={"display": "inline-block", "textAlign": "center"},
                        ),
                        dcc.Graph(id="graph-data-view"),
                    ],
                    width={"size": 6},
                ),
                dbc.Col(
                    [
                        html.H6(
                            "Distribution View",
                            style={"display": "inline-block", "textAlign": "center"},
                        ),
                        dcc.Graph(id="graph-dist-view"),
                    ],
                    width={"size": 5},
                ),
            ],
        ),
        # Plots row 2
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H6(
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
                        html.H6(
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


# --------------------------begin callbacks--------------------------#
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

#-------------------------------------------------------------------#
@app.callback(
    Output("dd-zipcode-selection", "value"),
    [
        Input("dd-zipcode-selection", "options"),
    ],
)
def set_zipcode_value(options):
    logger.info(f"app1 zipcode selected: {options[0]['value']}")
    return options[0]["value"]

#-------------------------------------------------------------------#
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
    df_desc.rename(columns={"index": "feature"}, inplace=True)
    df_desc.insert(loc=1, column="unit", value=[value for value in cfg["data_units"].values()])
    desc_columns = [{"id": col, "name": col} for col in df_desc.columns]

    logger.info(f"app1 passed df_desc")

    title1 = "Irradiance Data"
    fig1 = plot_tools.plot_irradiance(
        df, title=title1, zipcode=zipcode, irr_columns=cfg["irradiance_columns"], locale=locale_data
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
        columns=cfg["meteorological_fields"],
    )
    logger.info(f"app1 passed {title3}")

    return fig1, fig2, fig3, df_desc.to_dict("records"), desc_columns
