from functools import lru_cache

import logzero
import numpy as np
import pandas as pd
import pmdarima as pm
from logzero import logger
from pmdarima import arima, model_selection, pipeline
from pmdarima import preprocessing as ppc

# Connect to logzero log file
log_path = "logs/"
log_file = "dashboard_app.log"
logzero.logfile(
    log_path + log_file,
    maxBytes=1e5,
    backupCount=1,
    disableStderrLogger=True,
)
logger.info(f"pmd_tools logger initialized")


@lru_cache(maxsize=64)
def get_train_test(df, feature, test_size):
    """Produce and return time-series friendly train and test dataframes"""

    columns = df.columns.tolist()

    train, test = model_selection.train_test_split(df, test_size=test_periods)

    train = pd.DataFrame(train, index=df[: len(train)].index, columns=columns)
    test = pd.DataFrame(test, index=df[len(train) :].index, columns=columns)

    return train, test


def get_arima_fft_model(train, fc_periods):

    autoarima = arima.AutoARIMA(
        stepwise=True,
        trace=1,
        seasonal=False,  # because we use Fourier
        intercept="auto",
        suppress_warnings=True,
        error_action="ignore",
        random_state=42,
        m=1,
        start_p=1,
        start_q=1,
        max_p=3,
        max_q=4,
    )

    pipe = pipeline.Pipeline(
        [
            ("fourier", ppc.FourierFeaturizer(m=12, k=2)),
            ("arima", autoarima),
        ]
    )

    pipe.fit(train)

    return pipe


def get_arima_auto_model(train, fc_periods):

    model = pm.AutoARIMA(
        stepwise=True,
        trace=1,
        seasonal=True,
        intercept="auto",
        suppress_warnings=True,
        error_action="ignore",
        random_state=42,
        m=12,
        start_p=1,
        start_q=1,
        max_p=3,
        max_q=3,
        start_P=1,
        start_Q=1,
        max_P=2,
        max_Q=2,
        # start_D=0,
        # max_D=2,
    )

    model.fit(train)

    return model
