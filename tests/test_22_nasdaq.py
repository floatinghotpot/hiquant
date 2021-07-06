# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant import *

def test_download_nasdaq():
    df = download_us_stock_list()
    print(df[['symbol','name']])

    df = download_us_index_list()
    print(df[['symbol','name']])

if __name__ == "__main__":
    test_download_nasdaq()
