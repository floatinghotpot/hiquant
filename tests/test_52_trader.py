# -*- coding: utf-8; py-indent-offset:4 -*-

import datetime as dt
from hiquant import *

def XXXtest_backtrade():
    # test back trade
    date_start = date_from_str('1 months ago')
    date_end = date_from_str('yesterday')
    market = Market(date_start, date_end)

    df = get_stockpool_df(['600036', '000002'])
    df.to_csv('output/mytest.csv', index= False)

    trader = Trader(market)
    fund = Fund(market, trader, 'fund_1', {
        'name': 'fund no.1',
        'start_cash': '1000000.00',
        'strategy': 'strategy/001_macd.py',
        'stock_pool': 'output/mytest.csv',
    })
    trader.add_fund(fund)
    market.set_verbose()
    trader.set_verbose()
    trader.run_fund(date_start, date_end)
    trader.print_report()
    trader.plot(compare_index= 'sh000300', out_file='output/test_trader.png')

def XXXtest_run():
    date_start = date_from_str('today')
    date_end = date_from_str('tomorrow')
    market = Market(date_start, date_end)
    market.set_force_open(True)

    trader = Trader(market)
    fund = Fund(market, trader, 'fund_1', {
        'name': 'fund no.1',
        'start_cash': '1000000.00',
        'strategy': 'strategy/001_macd.py',
        'stock_pool': 'output/mytest.csv',
    })
    trader.add_fund(fund)
    market.set_verbose()
    trader.set_verbose()
    trader.run_fund(date_start, date_start + dt.timedelta(seconds=10))
    #trader.print_report()
    #trader.plot(compare_index= 'sh000300', out_file='output/trader_run.png')
