# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant.data_source.akshare_eastmoney import *

def test_fund_flow():
    df = download_cn_market_fund_flow()
    print(df)

    df = download_cn_sector_fund_flow_rank()
    print(df)

    df = download_cn_stock_fund_flow_rank()
    print(df)

    df = download_cn_stock_fund_flow('600036')
    print(df)

    df = download_cn_stock_fund_flow('000002')
    print(df)


if __name__ == "__main__":
    test_fund_flow()
