from itertools import product

import numpy as np
import pandas as pd
import pmdarima as pm
from pmdarima import model_selection
from sklearn.metrics import mean_squared_error
from tqdm.notebook import tqdm



# Fit a simple auto_arima model
def pmd_optimize_sarima():
    model = pm.auto_arima(train, start_p=1, start_q=1, start_P=1, start_Q=1,
                         max_p=5, max_q=5, max_P=5, max_Q=5, seasonal=True,
                         stepwise=True, suppress_warnings=True, D=10, max_D=10,
                         error_action='ignore')

    # Create predictions for the future, evaluate on test
    preds, conf_int = model.predict(n_periods=test.shape[0], return_conf_int=True)




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

    for order in tqdm(arima_order):
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

    for order in tqdm(sarima_order):
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
