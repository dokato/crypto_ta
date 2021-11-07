import pytest
import pandas as pd
import numpy as np
from crypto_ta.utils import binance_raw_to_ohlcv, col_to_vector

MOCK_BINANCE_RESP = [[1502928000000, '4261.48', '4485.39', '4200.74000000', '4285.08', '795.150377',
    1503014399999, '3454770.05073206', 3427, '616.24854100', '2678216.40060401', '8733.91139481'],
 [1503014400000, '4285.09', '4371.52', '3938.77', '4108.37', '1199.888264',
    1503100799999, '5086958.30617151', 5233, '972.86871', '4129123.31651808', '9384.14140858']
]

def test_binance_raw_to_ohlcv():
    res = binance_raw_to_ohlcv(MOCK_BINANCE_RESP, silent=True)
    assert isinstance(res, pd.DataFrame)
    assert res.shape[0] == 2
    assert list(res.columns) == ['open', 'high', 'low', 'close', 'volume']
    assert res.low.dtype == float

def test_col_to_vector():
    df = pd.DataFrame(data= {'col1': [1, 2], 'col2': [3, 4]})
    assert all(col_to_vector(df, 'col1') == np.array([1., 2.]))
