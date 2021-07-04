# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant.core.data_cache import get_daily, get_us_stock_list_df
from hiquant.core.data_source_yfinance import *

def test_get_us_stock_list():
    df = get_us_stock_list_df()
    print(df[['symbol','name']])

def test_yfinance():
    df = get_daily('AAPL')
    print(df)
    pass

if __name__ == "__main__":
    test_get_us_stock_list()
    test_yfinance()
