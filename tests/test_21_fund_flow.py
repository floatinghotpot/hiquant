# -*- coding: utf-8; py-indent-offset:4 -*-

from six import assertCountEqual
import tabulate as tb
from hiquant import *

def test_fund_flow():
    df = download_cn_market_fund_flow()
    print(df)

    df = download_cn_sector_fund_flow_rank()
    print(df)

    df = download_cn_stock_fund_flow_rank()
    print(df)

def test_stock_fund_flow():
    df = download_cn_stock_fund_flow('600036')
    print(df)

    df = download_cn_stock_fund_flow('000002')
    print(df)

    df = download_cn_stock_fund_flow('300357')
    print(df)

def test_my_stock_mffi():
    df = download_cn_stock_fund_flow_rank()
    my_df = get_stockpool_df('stockpool/realtime_trade.csv')
    df = df[ df.symbol.isin( my_df.symbol.tolist() ) ]
    df = df.sort_values(by='main_pct', ascending=False).reset_index(drop=True)
    print( tb.tabulate(df, headers='keys', tablefmt='psql') )

if __name__ == "__main__":
    test_fund_flow()
    test_stock_fund_flow()
    test_my_stock_mffi()
