# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant import *

def test_download_nasdaq():
    df = get_us_stock_list_df()
    print(df[['symbol','name']])

    df = get_us_index_list_df()
    print(df[['symbol','name']])

def test_download_yahoo():
    df = download_us_stock_daily('600036.SS', start='2020-01-01')
    print(df)

    df = get_daily('AAPL')
    print(df)

    df = download_us_stock_spot(['NFLX','AAPL','MSFT','DIDI','SONY'])
    print(df)

if __name__ == "__main__":
    test_download_nasdaq()
    test_download_yahoo()
