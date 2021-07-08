# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant.data_source.sina import download_cn_stock_spot

def test_download_spot():
    df = download_cn_stock_spot(['600036', '00700'])
    print(df)

if __name__ == "__main__":
    test_download_spot()
