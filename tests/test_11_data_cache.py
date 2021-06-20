# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant import *

def test_data_cache():
    df = get_all_stock_list_df()
    df = get_all_index_list_df()
    symbol_name = get_all_stock_symbol_name()

    df = get_stockpool_df(['600036','000002'])

    df = get_index_daily('sh000300')

    df = get_daily('600036')
    factor_df = get_daily_adjust_factor('600036')
    adjusted_df = adjust_daily_with_factor(df, factor_df)
    adjusted_df = adjust_daily('600036', df)

    df = get_stock_spot(['600036','000002'])

    df = create_finance_abstract_df('600036')
    df = get_finance_abstract_df('600036')

    df = get_ipoinfo_df('600036')
    df = get_dividend_history('600036')

    row = get_finance_indicator('600036')
    df = get_finance_indicator_df(['600036','000002'])
    #df = get_finance_indicator_all()

    row = get_stock_pepb_history('600036')
    df = get_pepb_symmary_df(['600036','000002'])
    #df = get_pepb_symmary_all()
