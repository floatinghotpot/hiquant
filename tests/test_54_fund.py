# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant import *

def test_fund():
    date_start = date_from_str('3 months ago')
    date_end = date_from_str('yesterday')
    market = Market(date_start, date_end)

    df = get_stockpool_df(['600036', '000002'])
    df.to_csv('output/mytest.csv', index= False)

    trader = Trader(market)
    fund = Fund(market, trader, 'fund_1', {
        'name': 'fund no.1',
        'start_cash': '1000000.00',
        'strategy': 'strategy/stra_001_pool_macd.py',
        'stock_pool': 'output/mytest.csv',
    })
    fund.set_verbose()
    fund.init_fund()
    fund.update_stat()
    fund.before_day()
    fund.after_day()
    fund.before_tick()
    fund.after_tick()
    fund.get_summary()
    fund.get_stat()
