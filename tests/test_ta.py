import pytest
import pandas as pd
import numpy as np
from crypto_ta.ta import CryptoTA
from crypto_ta.api import API

# Mock API

class MockAPI(API):

    def init_client(self):
        pass

    def get_ohlcv(self, cpair, interval = '1w', from_date=None,
                   to_date=None, **kwargs):
        ohlcv = pd.read_csv('tests/test_ohlcv_data.csv')
        ohlcv.index = ohlcv.date
        del ohlcv['date']
        return ohlcv

# Tests
def test_get_ohlcv():
    ta = CryptoTA(MockAPI())
    assert ta.ohlcv is None
    ta.get_ohlcv("BX")
    assert not ta.ohlcv is None
    assert isinstance(ta.ohlcv, pd.DataFrame)

def test_calculate_ta():
    ta = CryptoTA(MockAPI())
    ta.get_ohlcv("BX")
    assert ta.features is None
    ta.calculate_ta()
    assert not ta.features is None
    assert isinstance(ta.features, pd.DataFrame)
    assert ta.features.shape[1] > ta.ohlcv.shape[1]

def test_get_ta_features():
    ta = CryptoTA(MockAPI())
    ta.get_ohlcv("BX")
    ta.calculate_ta()
    assert len(ta.get_ta_features()) > 10
    assert 'volume_fi' in ta.get_ta_features()
    assert list(ta.features.columns[5:]) == ta.get_ta_features()

def test_calculate_arima():
    ta = CryptoTA(MockAPI())
    ta.get_ohlcv("BX")
    ta.calculate_arima(order=(1,0,1))
    assert not ta.arima is None

def test_forecast():
    ta = CryptoTA(MockAPI())
    ta.get_ohlcv("BX")
    ta.calculate_arima(order=(1,0,1))
    res = ta.forecast(2)
    assert res.shape[0] == 2
    assert isinstance(ta.forecast(2).index, pd.DatetimeIndex)

def test_plot_trend_line():
    ta = CryptoTA(MockAPI())
    ta.get_ohlcv("BX")
    res = ta.plot_trend_line(output = True)
    assert len(res) == 2
