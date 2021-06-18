# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant import *

def XXX_test_data_source_akshare():
    df = download_stock_list(None)
    df = download_index_list(None)

    df = download_index_daily('sh000300')

    df = download_stock_daily('600036')
    df = download_stock_daily_adjust_factor('600036')

    df = download_stock_spot(['600036','000002'])

    df = download_finance_balance_report('600036')
    df = download_finance_income_report('600036')
    df = download_finance_cashflow_report('600036')

    df = download_ipo('600036')
    df = download_dividend_history('600036')
    df = download_rightissue_history('600036')
    df = download_stock_pepb_history('600036')

    df = download_macro_bank_interest_rate('china')
    df = download_macro_bank_interest_rate('usa')
    df = download_macro_bank_interest_rate('euro')