import glob
import sys
import sqlite3

# sys.path.append("../../sql")
# import queries

# sys.path.append("../source")
# import dbrd_eda
# import dbrd_tools
# import plot_tools


def get_db_files(db_path="./"):
    db_files = [
        file.split("/")[4] for file in glob.glob(db_path + "*.db") if file != "../../data/db/geo_zipcodes.db"
    ]

    return tuple(sorted(db_files))
