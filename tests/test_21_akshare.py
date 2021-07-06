# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant import *

def test_download_szse():
    df = download_cn_stock_list(None)
    print(df)
    df = download_cn_index_list(None)
    print(df)

def test_download_sina():
    df = download_cn_stock_daily('600036')
    df = download_stock_daily_adjust_factor('600036')
    df = download_cn_index_daily('sh000300')

    df = download_cn_stock_spot(['600036','000002'])

    df = download_finance_balance_report('600036')
    df = download_finance_income_report('600036')
    df = download_finance_cashflow_report('600036')

    df = download_ipo('600036')
    df = download_dividend_history('600036')
    df = download_rightissue_history('600036')

def test_download_legu():
    df = download_stock_pepb_history('600036')

def XXX_test_macro_bank_data():
    df = download_macro_bank_interest_rate('china')
    df = download_macro_bank_interest_rate('usa')
    df = download_macro_bank_interest_rate('euro')

def test_download_spot():
    df = download_cn_stock_spot(['600036', 'hk0700'])

if __name__ == "__main__":
    test_download_szse()
    test_download_sina()
    test_download_legu()
    test_download_spot()
