#!/usr/bin/env python3

from functools import lru_cache

import logzero
import numpy as np
import pandas as pd
import pmdarima as pm
from logzero import logger
from pmdarima import arima, model_selection, pipeline
from pmdarima import preprocessing as ppc

@lru_cache(maxsize=64)
def get_train_test(df, feature, test_size):
    """Produce and return time-series friendly train and test dataframes"""
    
    columns = df.columns.tolist()
    
    train, test = model_selection.train_test_split(df, test_size=test_periods)
    
    train = pd.DataFrame(train, index=df[:len(train)].index, columns=columns)
    test = pd.DataFrame(test, index=df[len(train):].index, columns=columns)    

    return train, test

def get_arima_fft_model(train, fc_periods):

    pipe = pipeline.Pipeline(
        [
            ("fourier", ppc.FourierFeaturizer(m=12, k=4)),
            (
                "arima",
                arima.AutoARIMA(
                    stepwise=True,
                    trace=1,
                    error_action="ignore",
                    seasonal=False,  # because we use Fourier
                    suppress_warnings=True,
                ),
            ),
        ]
    )
    
    pipe.fit(train)
    
    return pipe
    

def get_arima_auto():
    
    
    return