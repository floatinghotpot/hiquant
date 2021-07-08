# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant import *

def test_download_yahoo():
    df = download_world_index_list()
    print(df)

    df = download_us_stock_daily('AAPL', start='2020-01-01')
    print(df)

    df = download_us_stock_spot(['NFLX','AAPL','MSFT','DIDI','SONY','600036.SS','000002.SZ','0700.HK'])
    print(df)

if __name__ == "__main__":
    test_download_yahoo()
