#    This script is part of crypto_ta
#    Copyright (C) 2021 dokato

import pandas as pd
import numpy as np

def binance_raw_to_ohlcv(raw: list, silent : bool = False) -> pd.DataFrame:
    for line in raw:
        del line[6:] # don't need this now
    df_ = pd.DataFrame(raw, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    df_.set_index('date', inplace=True)
    df_.index = pd.to_datetime(df_.index, unit='ms')
    cols = df_.columns
    df_[cols] = df_[cols].apply(pd.to_numeric, errors='coerce')
    if not silent: print(df_.head())
    return df_

def col_to_vector(df_ : pd.DataFrame, col : str = 'close') -> np.array:
    '''Extract column from a pandas dataframe and return a numpy vector'''
    val = df_[col].to_numpy()
    val = val.astype(np.float)
    return val
