import warnings

from scipy.stats import linregress
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_predict 
from ta import add_all_ta_features
from ta.utils import dropna
import matplotlib.pyplot as plt

from .api import API
from .utils import *
from .plots import *

__all__ = ['CryptoTA']

class NotYetCalculated(Exception):
    pass

class CryptoTA(object):
    '''
    Technical Analysis of Cryptocurrency time series.
    '''

    def __init__(self, api : API) -> None:
        self.features = None
        self.ohlcv = None
        self.api = api
    
    def get_ohlcv(self, cpair, interval = '1w', from_date=None, to_date=None, **kwargs):
        '''
        This is a wrapper for API specific `get_ohlcv` method. To learn more
        check `BinanceAPI`, or `KrakenAPI`
        '''
        ohlcv = self.api.get_ohlcv(cpair, interval = interval,
                           from_date=from_date, to_date=to_date)
        self.ohlcv = ohlcv
        if self.ohlcv.shape[0] < 30:
            warnings.warn('''
            CryptoTA warning: your OHLCV selection has less than 30 samples.
            It can be too short for some TA features.
            ''')

    def get_ta_features(self) -> list:
        '''
        List available features.
        '''
        if self.features is None:
            return []
        else:
            return list(self.features.columns[5:])


    def _assert_ohlcv_exists(self):
        '''
        Checks if "ohlcv" property exists.
        '''
        if self.ohlcv is None:
            raise NotYetCalculated("You need to calculate OHLCV values first! Use `get_ohlcv()` method.")

    def _assert_ta_exists(self):
        '''
        Checks if "features" (TA) property exists.
        '''
        if self.ohlcv is None:
            raise NotYetCalculated("You need to calculate TA features first! Use `calculate_ta()` method.")

    def _assert_arima_exists(self):
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
        self._assert_ohlcv_exists()
        plot_candle(self.ohlcv, moving_averages = moving_averages,
                    volume = volume, lastn = lastn)

    def plot_renko(self, moving_averages = (3,6,9),
                    volume = True, lastn = None):
        """
        Make Renko plot.
        """
        self._assert_ohlcv_exists()
        plot_renko(self.ohlcv, moving_averages = moving_averages,
                    volume = volume, lastn = lastn)

    def plot(self, moving_averages = (3,6,9), volume = True, lastn = None):
        """
        Make basic plot.
        """
        self._assert_ohlcv_exists()
        plot_basic(self.ohlcv, moving_averages = moving_averages,
                    volume = volume, lastn = lastn)
    
    def calculate_ta(self):
        """
        Results of this method is stored in the property `features`.
        """
        self._assert_ohlcv_exists()
        clean_ohlcv = dropna(self.ohlcv)
        self.features = add_all_ta_features(clean_ohlcv, open="open",
                       high="high", low="low", close="close",
                       volume="volume", fillna=True)

    def calculate_arima(self, order = (2,1,2), show_diag=False):
        """
        Results of this method is stored in the property `arima`.
        """
        self._assert_ohlcv_exists()
        model = ARIMA(self.ohlcv['close'], order = order)
        self.arima = model.fit()
        if show_diag:
            self.arima.plot_diagnostics()
            plt.show()
            print("AIC", self.arima.aic, "BIC", self.arima.bic)
    
    def forecast(self, n):
        """
        Forest to *n* periods.
        """
        self._assert_arima_exists()
        return self.arima.forecast(n)

    def plot_forecasts(self, date_to, date_from=None, prop='close', start_pred = 5):
        """
        Plot ARIMA forecasts.
        """
        self._assert_arima_exists()
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
        '''
        Plots Technical Analysis features.
        '''
        if not feature_name:
            raise ValueError("You need to specify a feature name. Check `get_ta_features()`")
        self._assert_ta_exists()
        plot_ta_feature(self.features, feature_name, style=style)

    def plot_trend_line(self, date_from=None, date_to=None,
                        prop='close', style='k-', show_diag=False, output=False):
        """
        Fits and plots a trend line in current range.
        """
        sub_ohlcv = self.ohlcv[date_from:date_to]
        xrange = np.arange(sub_ohlcv.shape[0]) + 1
        slope, intercept, r_value, _, std_err = linregress(x=xrange, y=sub_ohlcv['close'])
        if show_diag:
            print(f'R: {r_value}; std {std_err}')
        line_trend = slope * xrange + intercept
        if output:
            return (slope, intercept)
        else:
            plot_ta_feature(sub_ohlcv, prop, style=style, label=prop)
            plt.plot(sub_ohlcv.index, line_trend, 'r--', label="linear trend")
            plt.legend()
