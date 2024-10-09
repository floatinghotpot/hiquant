# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant.data_source import *

def test_download_cn_stock_list():
    df = download_cn_stock_list(None)
    print(df)

def test_download_cn_index_list():
    df = download_cn_index_list(None)
    print(df)

def test_download_hk_stock_list():
    df = download_hk_stock_list()
    print(df)

def test_download_cn_stock_daily():
    df = download_cn_stock_daily('600036')
    print(df)

def test_download_cn_index_daily():
    df = download_cn_index_daily('sh000300')
    print(df)

def test_download_finance_report():
    df = download_finance_balance_report('600036')
    df = download_finance_income_report('600036')
    df = download_finance_cashflow_report('600036')

    df = download_ipo('600036')
    df = download_dividend_history('600036')
    df = download_rightissue_history('600036')

def test_download_legu():
    df = download_stock_pepb_history('600036')

def test_macro_bank_data():
    #df = download_macro_bank_interest_rate('china')
    df = download_macro_bank_interest_rate('usa')
    df = download_macro_bank_interest_rate('euro')
    pass

if __name__ == "__main__":
    #test_download_cn_stock_list()
    #test_download_cn_index_list()
    #test_download_hk_stock_list()
    test_download_cn_index_daily()
    test_download_cn_stock_daily()
    #test_download_finance_report()
    #test_download_legu()
    #test_macro_bank_data()
    pass
