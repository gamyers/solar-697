#!/usr/bin/env python
# coding: utf-8

import os
import site
import sys

import logzero
import numpy as np
import pandas as pd
import yaml
from logzero import logger
from yaml import dump, load, safe_load

sys.path.append("../source")

log_path = "logs/"
log_file = "nsrdb_dl.log"
logzero.logfile(log_path + log_file, maxBytes=1e6, backupCount=5, disableStderrLogger=True)


def get_periods(x):
    if x == 8760:
        periods = 24 * 365
    else:
        # leap year
        periods = 24 * 366
    return x


def main():
    try:
        with open("source/config.yml", "r") as config_in:
            configs = load(config_in, Loader=yaml.SafeLoader)
    except:
        logger.error(f"config file open failure.")
        exit(1)

    # url = f'{configs["url"]["url_string"]}'
    # logger.info(f"url: {url}\n")

    cfg_vars = configs["url_variables"]
    logger.info(f"variables: {cfg_vars}\n")

    years = configs["request_years"]
    logger.info(f"years: {years}\n")

    time_index = configs["time_index"][False]
    logger.info(f"time index: {time_index}\n")

    try:
        with open("source/locations.yml", "r") as locs_in:
            locs = load(locs_in, Loader=yaml.SafeLoader)
    except:
        logger.error(f"location file open failure.")
        exit(1)

    zip_codes = locs["locations"]

    logger.info(f"zip codes: {zip_codes}\n")

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
            logger.info(req_str)

            nrows = 1e5  # 1e5 for 24/7/365(6)

            # Return just the first 2 lines to get metadata:
            df_raw = pd.read_csv(req_str, nrows=nrows)

            df_meta = df_raw.iloc[0].copy()

            row1_cols = df_raw.iloc[1]
            new_header = [item.replace(" ", "_") if isinstance(item, str) else item for item in row1_cols]

            df_data = df_raw.iloc[1:].copy()
            df_data.columns = new_header
            df_data.drop(1, axis=0, inplace=True)
            df_data = df_data.loc[:, df_data.columns.notnull()].copy()
            df_data.reset_index(drop=True, inplace=True)

            if time_index:
                periods = get_periods(len(df_data))

                # Set the time index in the pandas dataframe:
                df_data = df_data.set_index(
                    pd.date_range(
                        f"1/1/{year}",  # .format(yr=year),
                        freq=cfg_vars["interval"] + "Min",
                        periods=periods / int(cfg_vars["interval"]),
                    )
                )

            df_data.insert(0, "zip_code", zip_code)

            data_names = [
                (df_data, "nsrdb_" + str(zip_code) + "_" + str(year) + ".csv"),
                (df_meta, "nsrdb_meta_" + str(zip_code) + "_" + str(year) + ".csv"),
            ]

            for item in data_names:
                item[0].to_csv("data/" + item[1], index=True)
            break

    return


if __name__ == "__main__":
    main()
