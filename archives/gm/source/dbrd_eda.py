import sys
import pandas as pd

sys.path.append("../../sql")
import queries



def get_irr_data(conn, zipcode):
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