# -*- coding: utf-8; py-indent-offset:4 -*-

#from hiquant.data_source.sina import download_cn_stock_spot
from hiquant.data_source.akshare_stock import download_cn_stock_spot, download_cn_stock_daily

def test_download_spot():
    #df = download_cn_stock_spot(['600036', '00700'])
    #print(df)
    pass

def test_download_cn_stock_daily():
    #df = download_cn_stock_daily('600036')
    #print(df)
    pass

if __name__ == "__main__":
    test_download_spot()
    test_download_cn_stock_daily()
