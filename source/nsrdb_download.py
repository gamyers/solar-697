# see ./notebooks/nsrdb_download.ipynb for details related to this script

import sqlite3
import sys
from time import sleep

import logzero
import numpy as np
import pandas as pd
import yaml
from logzero import logger
from tqdm import tqdm
from yaml import dump, load, safe_load

sys.path.append("../source")
import queries
from secret import nrel_key


log_path = "logs/"
log_file = "nsrdb_download.log"

logzero.logfile(log_path + log_file, maxBytes=1e5, backupCount=5, disableStderrLogger=True)
logger.info(f"{log_path}, {log_file}\n")


configs = None
try:
    with open("../source/config.yml", "r") as config_in:
        configs = load(config_in, Loader=yaml.SafeLoader)
        logger.info(f"{configs}\n")
except:
    logger.error(f"config file open failure.")
    exit(1)

cfg_vars = configs["url_variables"]
logger.info(f"variables: {cfg_vars}\n")

years = configs["request_years"]
logger.info(f"years: {years}\n")

db1_path = configs["file_paths"]["downloads_path_db"]
db2_path = configs["file_paths"]["db_path"]
data_path = configs["file_paths"]["downloads_path_zips"]
raw_path = configs["file_paths"]["downloads_path_raw"]

city = configs["location_info"]["city"]
state = configs["location_info"]["state"]

db1_file = city + "_" + state + ".db"
db2_file = configs["file_names"]["db_file_gzc"]

db_table1 = configs["table_names"]["db_table1"]
db_table2 = configs["table_names"]["db_table2"]

logger.info(f"{db1_path}, {db1_file}")
logger.info(f"{db2_path}, {db2_file}")

nrows = configs["num_rows"][0]
zip_import = configs["zip_import"][True]

logger.info(f"number of rows: {nrows}\n")

print(db1_path, db1_file)
print(db2_path, db2_file)
print(data_path + " zipcodes_" + city + "_" + state + ".yml")

try:
    with open(data_path + "zipcodes_" + city + "_" + state + ".yml", "r") as locs_in:
        locs = load(locs_in, Loader=yaml.SafeLoader)
        logger.info(locs)
except:
    logger.error(f"location file open failure.")
    exit(1)

zip_codes = locs["zipcodes"]
logger.info(f"zip codes: {zip_codes}\n")


# establish db connection and cursor
conn = sqlite3.connect(db1_path + db1_file)
cursor = conn.cursor()

cursor.execute(queries.create_table_nsrdb)
conn.commit()
cursor.execute(queries.create_table_geo_zipcodes)
conn.commit()

conn2 = sqlite3.connect(db2_path + db2_file)
cursor2 = conn2.cursor()

# need to test for existance of records in the db
# and skip the import if so
# for now...
if zip_import:
    cursor.execute("""ATTACH DATABASE '../data/db/geo_zipcodes.db' AS gzc_db;""")
    cursor.execute("""INSERT INTO 'geo_zipcodes' SELECT * FROM gzc_db.geo_zipcodes;""")
    conn.commit()
    cursor.execute("DETACH gzc_db")


# ### Download link information
# https://developer.nrel.gov/docs/solar/nsrdb/psm3-download/


for year in years:
    for zip_code in tqdm(zip_codes.keys()):
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
            + f'&api_key={nrel_key}'
            + f'&attributes={cfg_vars["attrs"]}'
        )

        logger.info(f"{req_str}\n")

        # sleep so we don't overrun the rate NREL limit
        sleep(2)
        try:
            df_raw = pd.read_csv(req_str, nrows=nrows)
            logger.info("reg_str successful.")
        except:
            logger.error(f"Error requesting\n{req_str}\n")

        # query and extract the first 2 lines to get metadata:
        df_meta = df_raw.iloc[0].copy()
        # display(df_meta)

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

        # df_data.drop(["Year", "Month", "Day", "Hour", "Minute"], axis=1, inplace=True)
        df_data.drop(["Minute"], axis=1, inplace=True)
        df_data.insert(1, "zipcode", zip_code)
        df_data.insert(2, "location_id", df_meta["Location ID"])

        data_names = [
            (df_data, "nsrdb_" + str(zip_code) + "_" + str(year) + ".csv"),
            (df_meta, "nsrdb_meta_" + str(zip_code) + "_" + str(year) + ".csv"),
        ]

        try:
            for item in data_names:
                item[0].to_csv(raw_path + item[1], index=True)
                logger.info(f"{item[1]} successfully written.\n")
        except:
            logger.error("Error writing .csv raw file(s)")

        try:
            cursor.execute(queries.select_zip_year, {"zipcode": zip_code, "year": year})
            count = cursor.fetchone()
            # logger.info(count)

            if (count[0] == "8760") or (count[0] == "8784"):
                logger.warning(f"data for {year}, {zip_code} already present\n")
            else:
                df_data.to_sql("nsrdb", conn, if_exists="append", index=False, method="multi")
                logger.info(f"data for {year}, {zip_code} written to {db_file}:{db_table1}\n")
        except:
            logger.error("Error writing to nsrdb\n")

        llltze_params = {
            "loc_id": df_meta["Location ID"],
            "lat": df_meta["Latitude"],
            "lon": df_meta["Longitude"],
            "elev": df_meta["Elevation"],
            "tz": df_meta["Time Zone"],
            "zipcode": zip_code,
        }
        logger.info(f"{llltze_params}\n")

        cursor.execute(queries.update_gzc_llltze, llltze_params)
        conn.commit()

        cursor2.execute(queries.update_gzc_llltze, llltze_params)
        conn2.commit()

        cursor.execute(queries.select_zipcode, {"zipcode": zip_code})
        logger.info(f"gzc: {cursor.fetchall()}\n")


conn.close()
conn2.close()
