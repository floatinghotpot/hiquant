# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant.data_source.yahoo import *

def _test_download_world_index_list():
    df = download_world_index_list()
    print(df)

def _test_download_us_stock_daily():
    df = download_us_stock_daily('AAPL', start='2020-01-01')
    print(df)

def _test_download_us_stock_spot():
    df = download_us_stock_spot(['NFLX','AAPL','MSFT','DIDI','SONY','600036.SS','000002.SZ','0700.HK'])
    print(df)

if __name__ == "__main__":
    #_test_download_world_index_list()
    _test_download_us_stock_daily()
    #_test_download_us_stock_spot()
