#    This script is part of crypto_ta
#    Copyright (C) 2021 dokato

import os
from abc import ABC, abstractmethod
from typing import Union, Optional, Sequence, List, Dict, overload
from datetime import datetime

from binance.client import Client


class NotYetCalculated(Exception):
    pass

class API(ABC):
    '''
    Asbtract API object with a few helper methods.
    '''

    def __init__(self, api_key: Optional[str] = None,
                 api_secret: Optional[str] = None) -> None:
        if api_key is None:
            self.api_key = os.environ['API_KEY']
        else:
            self.api_key = api_key
        if api_key is None:
            self.api_secret = os.environ['API_SECRET']
        else:
            self.api_secret = api_secret
        self.ohlcv = None
        self.features = None

    def init_client(self):
        self.client = self.client(self.api_key, self.api_secret)

    @abstractmethod
    def get_ohlcv(self):
        '''
        Calculate Open High Low Close Volume values.
        '''
        pass

    def get_ta_features(self):
        '''
        List available features.
        '''
        if self.features is None:
            return []
        else:
            return list(self.features.columns[5:])


    def assert_ohlcv_exists(self):
        '''
        Checks if "ohlcv" property exists.
        '''
        if self.ohlcv is None:
            raise NotYetCalculated("You need to calculate OHLCV values first! Use `get_ohlcv()` method.")

    def assert_ta_exists(self):
        '''
        Checks if "features" (TA) property exists.
        '''
        if self.ohlcv is None:
            raise NotYetCalculated("You need to calculate TA features first! Use `calculate_ta()` method.")

    def assert_arima_exists(self):
        '''
        Checks if "arima" property exists.
        '''
        if self.ohlcv is None:
            raise NotYetCalculated("You need to calculate arima features first! Use `calculate_ta()` method.")

    def plot_candle(self, moving_averages = (10,20),
                     volume = True, lastn = None):
        """
        Make candle plot.
        """
        self.assert_ohlcv_exists()
        plot_candle(self.ohlcv, moving_averages = moving_averages,
                    volume = volume, lastn = lastn)

    def plot_renko(self, moving_averages = (3,6,9),
                    volume = True, lastn = None):
        """
        Make Renko plot.
        """
        self.assert_ohlcv_exists()
        plot_renko(self.ohlcv, moving_averages = moving_averages,
                    volume = volume, lastn = lastn)

    def plot(self, moving_averages = (3,6,9), volume = True, lastn = None):
        """
        Make basic plot.
        """
        self.assert_ohlcv_exists()
        plot_basic(self.ohlcv, moving_averages = moving_averages,
                    volume = volume, lastn = lastn)
    
    def calculate_ta(self):
        self.assert_ohlcv_exists()
        clean_ohlcv = dropna(self.ohlcv)
        self.features = add_all_ta_features(clean_ohlcv, open="open",
                       high="high", low="low", close="close",
                       volume="volume", fillna=True)
        return self.features

    def calculate_arima(self, order = (2,1,2), quiet=True):
        self.assert_ohlcv_exists()
        model = ARIMA(self.ohlcv['close'], order = order)
        self.arima = model.fit()
        if not quiet:
            self.arima.plot_diagnostics()
            plt.show()
            print("AIC", self.arima.aic, "BIC", self.arima.bic)
        return self.arima
    
    def forecast(self, n):
        """
        Forest to *n* periods.
        """
        self.assert_arima_exists()
        return self.arima.forecast(n)

    def plot_forecasts(self, date_to, date_from=None, prop='close', start_pred = 5):
        """
        Plot ARIMA forecasts.
        """
        self.assert_arima_exists()
        fig, ax = plt.subplots()
        # TODO check if correct date (i.e. in index)
        if date_from is None:
            subsdf = self.ohlcv[prop]
        else:
            subsdf = self.ohlcv[date_from:][prop]
        subsdf.plot(ax=ax, color='k')
        assert start_pred > 0, "*start_pred* must be > 0"
        last_k_dt = self.ohlcv.tail(start_pred).index[0]
        plot_predict(self.arima, last_k_dt, date_to, ax=ax)

    def plot_ta(self, feature_name = None, style='r-'):
        if feature_name:
            raise ValueError("You need to specify a feature name. Check `get_ta_features()`")
        self.assert_ta_exists()
        plot_ta_feature(self.features, feature_name, style=style)

    def get_trend_lines(self, date_from=None, date_to=None, prop='close', style='k-'):
        """
        TODO date_from date_to
        """
        xrange = np.arange(self.ohlcv.shape[0]) + 1
        slope, intercept, r_value, p_value, std_err = linregress(x=xrange, y=self.ohlcv['close'])
        line_trend = slope * xrange + intercept
        plot_ta_feature(self.ohlcv, prop, style=style, label=prop)
        plt.plot(self.ohlcv.index, line_trend, 'r--', label="linear trend")
        plt.legend()

class BinanceAPI(API):

    def __init__(self, api_key: Optional[str] = None,
                 api_secret: Optional[str] = None) -> None:
        super().__init__(api_key, api_secret)
        self.client = Client # Binance client
        self.init_client()

    def get_ohlcv(self, cpair, interval = '1w', from_date=None, to_date=None):
        '''
        Calculate Open High Low Close Volume values.
        '''
        if from_date is None:
            from_date = self.client._get_earliest_valid_timestamp(cpair, '1M')
        if not to_date is None and isinstance(to_date, datetime):
            to_date = to_date.timestamp()
        raw_resp = self.client.get_historical_klines(
            cpair,
            interval,
            from_date,
            end_str=to_date
        )
        self.ohlcv = binance_raw_to_ohlcv(raw_resp, silent=True)
        return self.ohlcv
