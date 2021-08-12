import glob
import math
import sqlite3
import sys
from itertools import product

sys.path.append("../../sql")

import pandas as pd
import queries
from logzero import logger
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.statespace.varmax import VARMAX

pd.set_option("plotting.backend", "plotly")


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


def get_locale_data(conn, zipcode):
    cursor = conn.cursor()
    cursor.execute(queries.select_locale_data, {"zipcode": zipcode})
    query_data = cursor.fetchone()
    locale_data = [qd for qd in query_data]
    logger.info(f"Locale data: {locale_data}")
    return locale_data


def get_db_files(db_path="./"):
    db_files = [
        file.split("/")[-1]
        for file in glob.glob(db_path + "*.db")
        if file.split("/")[-1] != "geo_zipcodes.db"
    ]

    return tuple(sorted(db_files))


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


def get_plots_layout(num_columns=1, num_items=1):
    # row, column dimension calculation
    return {"rows": (math.ceil(num_items / num_columns)), "columns": num_columns}


def get_data_decomps(df, period=12):
    decomps = {}
    cols = df.columns.tolist()
    
    for col in cols:
        decomps.update({col: seasonal_decompose(df[col], model="additive", period=period)})
        
    return decomps


def gen_varmax_params(p_rng=(0, 0), q_rng=(0, 0), debug=False):
    """
    input: 2 2-tuples of inclusive (p, q) value ranges
           Boolean for debug printing
    functionality: produce a cartesian product of the inputs
    output: list of 2-tuple products
    """
    p = range(p_rng[0], p_rng[1] + 1)
    q = range(q_rng[0], q_rng[1] + 1)

    # Create a list with all possible combination of parameters
    parameters = product(p, q)
    parameters_list = list(parameters)

    order_list = []

    for params in parameters_list:
        order_list.append(tuple(list(params)))

    if debug:
        print(f"VARMA Order list length: {len(order_list)}")
        print(f"VARMA Order list\n {order_list[:3]}")

    return order_list


def VARMAX_optimizer(series, varmax_order, debug=False):
    """
    input: Pandas data series with pd.datetime index
           list of 2-tuples representing VARMA orders (p, q)
           Boolean for debug printing
    functionality: model each (p, q) sequence, store AIC
    return: pandas dataframe listing all (p, q) AIC pairs,
            ordered best to worst
    """

    results = []

    for order in varmax_order:
        try:
            model = VARMAX(
                series,
                order=order,
                enforce_stationarity=True,
                trend="c",
            ).fit(disp=False)

        except:
            if debug:
                print("exception occured")
            continue

        aic = model.aic
        results.append([order, model.aic])

    result_df = pd.DataFrame(results)
    result_df.columns = ["(p, q)", "AIC"]
    result_df = result_df.sort_values(by="AIC", ascending=True).reset_index(drop=True)

    return result_df


def varmax_model(frame, p=0, q=0, num_fc=1, forecast=False, summary=False):
    """
    input: Pandas Series with pd.datetime index.
           Integers: VARMA parameters p, q
           Integer: number of forecast periods
           Boolean: summary print
           Bookean: True return forecast, False return model
    functionality: perform an ARIMA forecast of the Series time-series
    return: forecast data or model
    """

    model = VARMAX(
        frame,
        order=(p, q),
        trend="c",
        enforce_stationarity=True,
    ).fit(disp=False)

    if summary:
        print(model.summary())

    if forecast:
        start = len(frame)
        end = start + num_fc
        forecast = model.predict(start=start, end=end)
        return forecast

    return model


def gen_arima_params(p_rng=(0, 0), d_rng=(0, 0), q_rng=(0, 0), debug=False):
    """
    input: 3 2-tuples of inclusive value ranges
           Boolean for debug printing
    functionality: produce a cartesian product of the inputs
    output: list of 3-tuple products
    """
    p = range(p_rng[0], p_rng[1] + 1)
    d = range(d_rng[0], d_rng[1] + 1)
    q = range(q_rng[0], q_rng[1] + 1)

    # Create a list with all possible combination of parameters
    parameters = product(p, d, q)
    parameters_list = list(parameters)

    order_list = []

    for params in parameters_list:
        params = list(params)
        params = tuple(params)
        order_list.append(params)

    if debug:
        print(f"ARIMA Order list length: {len(order_list)}")
        print(f"ARIMA Order list\n {order_list[:3]}")

    return order_list


def ARIMA_optimizer(series, arima_order, debug=False):
    """
    input: Pandas data series with pd.datetime index
           list of 3-tuples representing ARIMA orders (p, d, q)
           Boolean for debug printing
    functionality: model each (p, d, q) sequence, store AIC
    return: pandas dataframe listing all (p, d, q) AIC pairs,
            ordered best to worst
    """

    results = []

    for order in arima_order:
        try:
            model = ARIMA(
                series,
                order=order,
            ).fit()
        except:
            if debug:
                print("exception occured")
            continue

        aic = model.aic
        results.append([order, model.aic])

    result_df = pd.DataFrame(results)
    result_df.columns = ["(p, d, q)", "AIC"]
    result_df = result_df.sort_values(by="AIC", ascending=True).reset_index(drop=True)

    return result_df


def arima_model(series, p=0, d=0, q=0, num_fc=1, summary=False, forecast=False):
    """
    input: Pandas Series with pd.datetime index.
           Integers: ARIMA parameters p, d, q
           Integer: number of forecast periods
           Boolean: summary print
           Bookean: True return forecast, False return model
    functionality: perform an ARIMA forecast of the Series time-series
    return: forecast data or model
    """

    model = ARIMA(
        series,
        order=(p, d, p),
        enforce_stationarity=True,
        # trend="n",
    ).fit()

    if summary:
        print(model.summary())

    if forecast:
        start = len(series)
        end = start + num_fc
        forecast = model.predict(start=start, end=end)
        return forecast

    return model


def gen_sarima_params(
    p_rng=(0, 0),
    d_rng=(0, 0),
    q_rng=(0, 0),
    P_rng=(0, 0),
    D_rng=(0, 0),
    Q_rng=(0, 0),
    debug=False,
):
    """
    input: 3 3-tuples of inclusive value ranges
           Boolean for debug printing
    functionality: produce a cartesian product of the inputs
    output: list of 3-tuple products
    """
    p = range(p_rng[0], p_rng[1] + 1)
    d = range(d_rng[0], d_rng[1] + 1)
    q = range(q_rng[0], q_rng[1] + 1)

    P = range(P_rng[0], P_rng[1] + 1)
    D = range(D_rng[0], D_rng[1] + 1)
    Q = range(Q_rng[0], Q_rng[1] + 1)

    # Create a list with all possible combination of parameters
    parameters = product(p, d, q, P, D, Q)
    parameters_list = list(parameters)

    order_list = []

    for params in parameters_list:
        params = list(params)
        params = tuple(params)
        order_list.append(params)

    if debug:
        print(f"SARIMA Order list length: {len(order_list)}")
        print(f"SARIMA Order list\n {order_list[:3]}")

    return order_list


def SARIMA_optimizer(series, sarima_order, s=0, debug=False):
    """
    input: Pandas data series with pd.datetime index
           list of 6-tuples representing ARIMA orders (p, d, q, P, D, Q)
           Boolean for debug printing
    functionality: model each (p, d, q) sequence, store AIC
    return: pandas dataframe listing all (p, d, q, P, D, Q) AIC pairs,
            ordered best to worst
    """

    results = []

    for order in sarima_order:
        if debug:
            print(order)
        try:
            model = ARIMA(
                series,
                order=(order[0], order[1], order[2]),
                seasonal_order=(order[3], order[4], order[5], s),
                enforce_stationarity=True,
                # trend="c",
            ).fit()
        except:
            if debug:
                print("exception occured")
            continue

        aic = model.aic
        results.append([order, model.aic])

    result_df = pd.DataFrame(results)
    result_df.columns = ["(p, d, q, P, D, Q, s)", "AIC"]
    result_df = result_df.sort_values(by="AIC", ascending=True).reset_index(drop=True)

    return result_df


def sarima_model(series, p=0, d=0, q=0, P=0, D=0, Q=0, s=0, num_fc=1, summary=False, forecast=False):
    """
    input: Pandas Series with pd.datetime index.
           Integers: ARIMA parameters p, d, q
           Integer: number of forecast periods
           Boolean: summary print
           Bookean: True return forecast, False return model
    functionality: perform an ARIMA forecast of the Series time-series
    return: forecast data or model
    """

    model = ARIMA(
        series,
        order=(p, d, p),
        seasonal_order=(P, D, Q, s),
        enforce_stationarity=True,
        # trend="c",
    ).fit()

    if summary:
        print(model.summary())

    if forecast:
        start = len(series)
        end = start + num_fc
        forecast = model.predict(start=start, end=end)
        return forecast

    return model
