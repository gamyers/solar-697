#!/usr/bin/env python3

import glob
import math
import sqlite3
import sys
from itertools import product

import logzero
import pandas as pd
from logzero import logger
from statsmodels.tsa.seasonal import seasonal_decompose

sys.path.append("../../sql")
import queries


def get_db_connection(db_path, db_filename):
    conn = sqlite3.connect(db_path + db_filename)
    logger.info(f"Connection made: {conn}")
    return conn


def get_db_zipcodes(conn):
    cursor = conn.cursor()
    cursor.execute(queries.select_distinct_zips)
    zipcodes = cursor.fetchall()
    zipcodes = [z[0] for z in zipcodes]
    logger.info(f"Distinct zip codes: {zipcodes}")
    return zipcodes


def get_column_names(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(queries.select_column_names, {"table_name": table_name})
    names = cursor.fetchall()
    names = [name[0] for name in names]
    logger.info(f"Column Names: {names}")
    return names


def get_locale_data(conn, zipcode):
    """retrieve locale data from geo_zipcodes table of the database"""
    cursor = conn.cursor()
    cursor.execute(queries.select_locale_data, {"zipcode": zipcode})
    query_data = cursor.fetchone()
    locale_data = [qd for qd in query_data]
    logger.info(f"Locale data: {locale_data}")
    return locale_data


def get_db_files(db_path="./"):
    """retrieve database file names from the file system"""
    db_files = [
        file.split("/")[-1]
        for file in glob.glob(db_path + "*.db")
        if file.split("/")[-1] != "geo_zipcodes.db"
    ]

    return tuple(sorted(db_files))


def get_irr_data(conn, zipcode):
    """retrieve irradiance data from database"""
    params = {"zipcode": zipcode}

    df = pd.read_sql(
        queries.select_nsr_rows,
        conn,
        params=params,
        index_col="date_time",
        parse_dates=["date_time"],
    )

    df.sort_index(axis=0, inplace=True)

    return df


def get_plots_layout(num_columns=1, num_items=1):
    """row, column dimension calculation"""
    return {"rows": (math.ceil(num_items / num_columns)), "columns": num_columns}


def get_data_decomps(df, period=12):
    """data decomposition"""
    decomps = {}
    cols = df.columns.tolist()

    for col in cols:
        decomps.update({col: seasonal_decompose(df[col], model="additive", period=period)})

    return decomps


def get_train_test(df, test_len_yrs=1):
    """produce a time-series friendly train/test split"""

    months = 12
    total_len = len(df)
    test_len = months * test_len_yrs
    train_len = total_len - test_len

    train = df.iloc[:train_len]  # [columns[forecast_on_idx]]
    test = df.iloc[train_len:]  # [columns[forecast_on_idx]]

    return train, val
