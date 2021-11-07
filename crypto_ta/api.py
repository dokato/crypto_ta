#    This script is part of crypto_ta
#    Copyright (C) 2021 dokato

import os
from abc import ABC, abstractmethod
from typing import Union, Optional, Sequence, List, Dict, overload
from datetime import datetime

from .utils import binance_raw_to_ohlcv

__all__ = ['BinanceAPI', 'KrakenAPI']

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

    @abstractmethod
    def init_client(self):
        """
        Authentication fo client.
        """
        pass

    @abstractmethod
    def get_ohlcv(self):
        '''
        Calculate Open High Low Close Volume values.
        '''
        pass


class BinanceAPI(API):

    def __init__(self, api_key: Optional[str] = None,
                 api_secret: Optional[str] = None) -> None:
        super().__init__(api_key, api_secret)
        try:
            from binance.client import Client
        except ImportError:
            raise ImportError(
                """For Binance API to work the latest version of
                a `binance` module is required. Install with:\n
                >>> pip install python-binance
                """)
        self.client = Client # Binance client
        self.init_client()

    def init_client(self):
        self.client = self.client(self.api_key, self.api_secret)

    def get_ohlcv(self, cpair, interval = '1w', from_date=None,
                   to_date=None, **kwargs):
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

KRAKEN_INTERVALS = {1, 5, 15, 30, 60, 240, 1440, 10080, 21600} # minutes
INTERVAL_TO_MINUTES = {'2w' : 21600, '1w' : 10080, '1d' : 1440}

class KrakenAPI(API):

    def __init__(self, api_key: Optional[str] = None,
                 api_secret: Optional[str] = None) -> None:
        super().__init__(api_key, api_secret)
        try:
            import krakenex
            from pykrakenapi import KrakenAPI
        except ImportError:
            raise ImportError(
                """For Binance API to work the latest version of
                a `binance` module is required. Install with:\n
                >>> pip install pykrakenapi
                """)
        self.client = KrakenAPI # Kraken client
        self.init_client()

    def init_client(self):
        import krakenex
        api = krakenex.API()
        self.client = self.client(api)

    def get_ohlcv(self, cpair, interval = '1w', from_date=None,
                   to_date=None, **kwargs):
        '''
        Calculate Open High Low Close Volume values.
        '''
        if not from_date is None:
            from_date = from_date.timestamp()
        if not to_date is None and isinstance(to_date, datetime):
            to_date = to_date.timestamp()
        if not interval in INTERVAL_TO_MINUTES.keys():
            if not interval in KRAKEN_INTERVALS:
                raise ValueError("Wrong interval value.")
        ohlc, _ = self.client.get_ohlc_data(
            cpair,
            interval = INTERVAL_TO_MINUTES[interval],
            since = from_date,
            ascending=True
            )
        if to_date:
            ohlc = ohlc[ohlc.index < datetime.fromtimestamp(to_date)]
        ohlc = ohlc.drop(['vwap', 'count'], axis=1)
        self.ohlcv = ohlc
        return self.ohlcv
