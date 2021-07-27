from itertools import product

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from tqdm.notebook import tqdm


def gen_arima_params(p_rng=(0, 0), d_rng=(0, 0), q_rng=(0, 0), debug=False):
    """
    input: 3 3-tuples of inclusive value ranges
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
        print(f"Order list length: {len(order_list)}")

    return order_list


def ARIMA_optimizer(series, order_list, debug=False):
    """
    input: Pandas data series with pd.datetime index
           list of 3-tuples representing ARIMA orders (p, d, q)
           Boolean for debug printing
    functionality: model each (p, d, q) sequence, store AIC
    return: pandas dataframe listing all (p, d, q) AIC pairs,
            ordered best to worst
    """

    results = []

    for order in tqdm(order_list):
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
