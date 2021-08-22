from math import sqrt

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error


# frame a sequence as a supervised learning problem
def make_supervised(data, lag=1):
    df = pd.DataFrame(data)
    columns = [df.shift(i) for i in range(1, lag + 1)]
    columns.append(df)
    df = pd.concat(columns, axis=1)
    df.fillna(0, inplace=True)
    return df


# create a differenced series
def difference(dataset, interval=1):
    diff = list()
    for i in range(interval, len(dataset)):
        value = dataset[i] - dataset[i - interval]
        diff.append(value)
    return pd.Series(diff)


def inverse_difference(series_orig, series_diffd):
    # invert differenced value
    def inv_diff_value(history, yhat, interval=1):
        return yhat + history[-interval]

    inverted = [series_orig[0]]

    for i in range(len(series_diffd)):
        value = inv_diff_value(series_orig, series_diffd[i], len(series_orig) - i)
        inverted.append(value)

    return pd.Series(inverted)


def persistence_forecast_plot(train, test):
    # From Resources #1

    # walk-forward validation
    history = [x for x in train]
    predictions = []

    for i in range(len(test)):
        # make prediction
        predictions.append(history[-1])
        # observation
        history.append(test[i])

    # report performance
    rmse = sqrt(mean_squared_error(test, predictions))
    print("RMSE: %.3f" % rmse)

    # line plot of observed vs predicted
    plt.plot(test)
    plt.plot(predictions)
    plt.show()
