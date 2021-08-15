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
import pmdarima as pm
import yaml
from app import app
from dash.dependencies import Input, Output, State
from dash_table import DataTable
from logzero import logger

sys.path.append("../../sql")
import queries

sys.path.append("../source")
import plot_tools
import pmd_tools
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
layout_app3 = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="app3-dd-db-selection",
                        options=[{"label": db, "value": db} for db in db_files],
                        value=cfg["file_names"]["default_db"],
                        placeholder="Select a database",
                        persistence=True,
                    ),
                    width={"size": 2, "offset": 0},
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="app3-dd-zipcode-selection",
                        placeholder="Select a Zip Code",
                        persistence=True,
                    ),
                    width={"size": 2, "offset": 1},
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="app3-dd-feature-selection",
                        value="GHI",
                        placeholder="Select a Feature",
                        persistence=True,
                    ),
                    width={"size": 2, "offset": 1},
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            "Forecast",
                            id="app3-btn-forecast",
                            type="submit",
                            color="success",
                            className="mr-1",
                        ),
                    ],
                    width={"size": 1, "offset": 2},
                ),
            ],
        ),
        dbc.Row(
            dbc.Col(
                [
                    html.H5(
                        "ARIMA with Fourier Seasonal Tranformation",
                        style={"display": "inline-block", "textAlign": "center"},
                    ),
                    dcc.Graph(id="app3-graph-arima-1"),
                ],
                width={"size": 11},
            ),
        ),
        dbc.Row(
            dbc.Col(
                [
                    html.H5(
                        "ARIMA with Traditional Seasonal Differencing",
                        style={"display": "inline-block", "textAlign": "center"},
                    ),
                    dcc.Graph(id="app3-graph-arima-2"),
                ],
                width={"size": 11},
            ),
        ),
    ]
)


# --------------------------begin callbacks--------------------------#
@app.callback(
    Output("app3-dd-zipcode-selection", "options"),
    [
        Input("app3-dd-db-selection", "value"),
    ],
)
def get_zipcodes(file_name):
    logger.info(f"get_zipcodes callback: {file_name}")
    # print(f"app3 get_zipcodes callback: {file_name}")

    conn = ts_tools.get_db_connection(db_path, file_name)
    zipcodes = ts_tools.get_db_zipcodes(conn)
    conn.close()

    logger.info(f"app3 zipcodes retrieved\n{zipcodes}")
    # print(f"app3 1st of zipcodes retrieved: {zipcodes[0]}")

    # return the list object to properly populate the dropdown!
    return [{"label": zipcode, "value": zipcode} for zipcode in zipcodes]


# -------------------------------------------------------------------#
@app.callback(
    Output("app3-dd-zipcode-selection", "value"),
    Input("app3-dd-zipcode-selection", "options"),
)
def set_zipcode_value(options):
    logger.info(f"app3 zipcode selected: {options[0]['value']}")
    # print(f"app3 set_zipcode_value: {options[0]['value']}")
    return options[0]["value"]


# -------------------------------------------------------------------#
@app.callback(
    Output("app3-dd-feature-selection", "options"),
    Input("app3-dd-db-selection", "value"),
)
def get_features(file_name):
    logger.info(f"get_features callback")

    conn = ts_tools.get_db_connection(db_path, file_name)
    col_names = ts_tools.get_column_names(conn, cfg["table_names"]["db_table1"])
    conn.close()

    logger.info(f"app3 column names:\n{col_names}")

    column_names = []

    for name in col_names:
        if name in cfg["drop_columns"]:
            continue
        column_names.append(name)

    logger.info(f"app3 feature names: {column_names}")

    # return the list object to properly populate the dropdown!
    return [{"label": column, "value": column} for column in column_names]


# -------------------------------------------------------------------#
@app.callback(
    Output("app3-dd-feature-selection", "value"),
    Input("app3-dd-feature-selection", "options"),
)
def set_feature_value(options):
    logger.info(f"app3 feature selected: {options[6]['value']}")
    return options[6]["value"]


# -------------------------------------------------------------------#
@app.callback(
    [
        Output("app3-graph-arima-1", "figure"),
        Output("app3-graph-arima-2", "figure"),
    ],
    [
        Input("app3-btn-forecast", "n_clicks"),
    ],
    [
        State("app3-dd-db-selection", "value"),
        State("app3-dd-zipcode-selection", "value"),
        State("app3-dd-feature-selection", "value"),
    ],
)
def graph_output(n_clicks, db_filename, zipcode, feature):

    # feature = feature_selection
    cntx = dash.callback_context
    context = cntx.triggered[0]["prop_id"].split(".")[0]

    logger.info(f"graph_output entry context: {context}")
    logger.info(f"graph_output arguments: {db_filename}, {zipcode}, {feature}")
    
    print(f"graph_output entry context: {context}")
    print(f"graph_output arguments: {db_filename}, {zipcode}, {feature}")

    if context == "":
        db_filename = cfg["file_names"]["default_db"]
        conn = ts_tools.get_db_connection(db_path, db_filename)
        zipcodes = ts_tools.get_db_zipcodes(conn)

        if not zipcode:
            zipcode = zipcodes[0]

        locale_data = ts_tools.get_locale_data(conn, zipcode)
        df = ts_tools.get_irr_data(conn, zipcode)

        logger.info(f"app3 Made if: {db_filename}, {zipcode}, {locale_data}")
        # print(f"Made if: {db_filename}, {zipcode}, {feature}")

    elif context == "app3-btn-forecast":
        # db_filename = cfg["file_names"]["default_db"]
        conn = ts_tools.get_db_connection(db_path, db_filename)
        # zipcodes = ts_tools.get_db_zipcodes(conn)
        # zipcode = zipcodes[0]
        locale_data = ts_tools.get_locale_data(conn, zipcode)
        df = ts_tools.get_irr_data(conn, zipcode)
        # feature = feature_selection

        logger.info(f"app3 Made else: {db_filename}, {zipcode}, {locale_data}, {feature}")
        # print(f"Made else: {db_filename}, {zipcode}, {locale_data}, {feature}")

    logger.info(f"app3 passed if/elif/else")
    logger.info(f"{db_filename}, {zipcode}, {locale_data}, {feature}")
    print(f"ready for forecast: {db_filename}, {zipcode}, {locale_data}, {feature}")

    if context == "app3-btn-forecast":
        test_len_yrs = 5
        test_periods = 5 * 12
        fc_periods = 5 * 12

        dt_idx = pd.date_range("2021-01-01", periods=fc_periods, freq="M")

        logger.info(f"app3 parameters: {test_len_yrs}, {test_periods}, {fc_periods}, {feature}")
        logger.info(f"forecast datetime index: {dt_idx}")

        train, test = pm.model_selection.train_test_split(df, test_size=test_periods)
        logger.info(train.tail(5))
        logger.info(test.head(5))

        fft_model = pmd_tools.get_arima_fft_model(train[feature], fc_periods)
        logger.info(fft_model)

        fft_test_pred = fft_model.predict(n_periods=fc_periods, return_conf_int=False)
        fft_test_pred = pd.Series(fft_test_pred, index=test.index)

        fft_model.update(test[feature])

        fft_forecast = fft_model.predict(n_periods=fc_periods, return_conf_int=False)
        fft_forecast = pd.Series(fft_forecast, index=dt_idx)

        title1 = f"{feature}, FFT,"
        fig1 = plot_tools.plot_forecast(
            train[feature],
            test[feature],
            fft_test_pred,
            fft_forecast,
            title=title1,
            zipcode=zipcode,
            locale=locale_data,
        )
        logger.info(f"app3 passed {title1}")

        auto_model = pmd_tools.get_arima_auto_model(train[feature], fc_periods)
        logger.info(auto_model)

        auto_test_pred = auto_model.predict(n_periods=fc_periods, return_conf_int=False)
        auto_test_pred = pd.Series(auto_test_pred, index=test.index)

        auto_model.update(test[feature])

        auto_forecast = auto_model.predict(n_periods=fc_periods, return_conf_int=False)
        auto_forecast = pd.Series(auto_forecast, index=dt_idx)

        title2 = f"{feature}, Diff,"
        fig2 = plot_tools.plot_forecast(
            train[feature],
            test[feature],
            auto_test_pred,
            auto_forecast,
            title=title2,
            zipcode=zipcode,
            locale=locale_data,
        )
        logger.info(f"app3 passed {title2}")

        return fig1, fig2
    
    if context != "app3-btn-forecast":
        return go.Figure(), go.Figure()
    else:
        return fig1, fig2
