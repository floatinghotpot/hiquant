# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant import *

def test_data_cache():
    df = get_all_stock_list_df()
    print(df)
    df = get_all_index_list_df()
    print(df)
    symbol_name = get_all_symbol_name()

    df = get_stockpool_df(['600036','00700','600036.SS','0700.HK','AAPL'])
    print(df)

    df = get_index_daily('sh000300')
    print(df)

    df = get_index_daily('^GSPC')
    print(df)

    df = get_daily('600036')
    print(df)

    df = get_stock_spot(['600036','000002'])
    print(df)

    df = create_finance_abstract_df('600036')
    print(df)
    df = get_finance_abstract_df('600036')
    print(df)

    df = get_ipoinfo_df('600036')
    print(df)
    df = get_dividend_history('600036')
    print(df)

    row = get_finance_indicator('600036')
    df = get_finance_indicator_df(['600036','000002'])
    print(df)
    #df = get_finance_indicator_all()

    row = get_stock_pepb_history('600036')
    df = get_pepb_symmary_df(['600036','000002'])
    print(df)
    #df = get_pepb_symmary_all()

if __name__ == "__main__":
    test_data_cache()
