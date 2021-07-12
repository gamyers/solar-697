#!/usr/bin/env python
# coding: utf-8

import os
import site
import sqlite3
import sys
from time import sleep

import logzero
import numpy as np
import pandas as pd
import yaml
from logzero import logger
from yaml import dump, load, safe_load

log_path = "logs/"
log_file = "nsrdb_dl2.log"

logzero.logfile(log_path + log_file, maxBytes=1e6, backupCount=5, disableStderrLogger=True)
logger.info(f"{log_path}, {log_file}\n")

sys.path.append("../source")
import queries


def get_configs():

    configs = None

    try:
        with open("../source/config.yml", "r") as config_in:
            configs = load(config_in, Loader=yaml.SafeLoader)
            logger.info(f"{configs}\n")
    except:
        logger.error(f"config file open failure.")
        exit(1)

    return configs


def get_locations():
    try:
        with open("../source/locations.yml", "r") as locs_in:
            locs = load(locs_in, Loader=yaml.SafeLoader)
            logger.info(locs)
    except:
        logger.error(f"location file open failure.")
        exit(1)

    return locs


def main():

    configs = get_configs()
    cfg_vars = configs["url_variables"]
    logger.info(f"variables: {cfg_vars}\n")

    years = configs["request_years"]
    logger.info(f"years: {years}\n")

    db_path = configs["file_locations"]["db_path"]
    db_file = configs["file_locations"]["db_file_nsr"]
    logger.info(f"{db_path}, {db_file}")

    nrows = configs["num_rows"][0]
    logger.info(f"number of rows: {nrows}\n")

    locs = get_locations()
    zip_codes = locs["locations"]
    logger.info(f"zip codes: {zip_codes}\n")

    # establish db connection and cursor
    conn = sqlite3.connect(db_path + db_file)
    cursor = conn.cursor()

    cursor.execute(queries.create_table_nsrdb)
    conn.commit()

    for yr_count, year in enumerate(years):
        for zip_count, zip_code in enumerate(zip_codes.keys()):
            req_str = (
                f"https://developer.nrel.gov/api/solar/nsrdb_psm3_download.csv?"
                + f'wkt=POINT({zip_codes[zip_code]["lon"]}%20{zip_codes[zip_code]["lat"]})'
                + f"&names={year}"
                + f'&leap_day={cfg_vars["leap_year"]}'
                + f'&interval={cfg_vars["interval"]}'
                + f'&utc={cfg_vars["utc"]}'
                + f'&full_name={cfg_vars["name"]}'
                + f'&email={cfg_vars["email"]}'
                + f'&affiliation={cfg_vars["affiliation"]}'
                + f'&mailing_list={cfg_vars["mailing_list"]}'
                + f'&reason={cfg_vars["use"]}'
                + f'&api_key={cfg_vars["key"]}'
                + f'&attributes={cfg_vars["attrs"]}'
            )

            logger.info(f"{req_str}\n")

            # sleep so we don't overrun the rate NREL limit
            sleep(2)
            df_raw = pd.read_csv(req_str, nrows=nrows)

            # query and extract the first 2 lines to get metadata:
            df_meta = df_raw.iloc[0].copy()

            row1_cols = df_raw.iloc[1]
            new_header = [item.replace(" ", "_") if isinstance(item, str) else item for item in row1_cols]

            df_data = df_raw.iloc[1:].copy()
            df_data.columns = new_header
            df_data.drop(1, axis=0, inplace=True)
            df_data = df_data.loc[:, df_data.columns.notnull()].copy()
            df_data.reset_index(drop=True, inplace=True)

            df_data.insert(0, "date_time", "")

            df_data["date_time"] = pd.to_datetime(
                df_data["Year"].astype(str)
                + "-"
                + df_data["Month"].astype(str)
                + "-"
                + df_data["Day"].astype(str)
                + " "
                + df_data["Hour"].astype(str)
                + ":"
                + df_data["Minute"].astype(str)
                + ":"
                + "00"
            )

            df_data.drop(["Year", "Month", "Day", "Hour", "Minute"], axis=1, inplace=True)

            df_data.insert(1, "zip_code", zip_code)

            data_names = [
                (df_data, "nsrdb_" + str(zip_code) + "_" + str(year) + ".csv"),
                (df_meta, "nsrdb_meta_" + str(zip_code) + "_" + str(year) + ".csv"),
            ]

            for item in data_names:
                item[0].to_csv("../data/" + item[1], index=True)

            df_data.to_sql("nsrdb", conn, if_exists="append", index=False, method="multi")

    conn.close()
    return


if __name__ == "__main__":
    main()
