# -*- coding: utf-8; py-indent-offset:4 -*-

import multiprocessing as mp

from ..utils import date_from_str
from .stock_market import Market
from .trader import Trader
from .fund import Fund

def backtest_one(args):
    strategy, start_cash, date_start, date_end = args

    market = Market(date_start, date_end)
    trader = Trader(market)

    fund = Fund(market, trader)
    fund.set_name(strategy.__name__)
    fund.set_start_cash( start_cash )
    fund.add_strategy( strategy(fund) )
    trader.add_fund(fund)
    trader.run_fund(date_start, date_end)

    return trader.get_report()

def backtest_strategy(strategy, start_cash= None, date_start= None, date_end= None, compare_index= None, out_file= None, parallel= True):
    if type(strategy) != list:
        strategy = [ strategy ]

    if start_cash is None:
        start_cash = 1000000.00
    if date_start is None:
        date_start = date_from_str('3 years ago')
    if date_end is None:
        date_end = date_from_str('yesterday')

    if parallel:
        args_list = [[stra, start_cash, date_start, date_end] for stra in strategy]
        with mp.Pool(len(strategy)) as p:
            report_list = p.map(backtest_one, args_list)
        all_report = []
        for report in report_list:
            all_report += report
        trader = Trader(Market(date_start, date_end))

    else:
        market = Market(date_start, date_end)
        trader = Trader(market)
        for stra in strategy:
            fund = Fund(market, trader)
            fund.set_name(stra.__name__)
            fund.set_start_cash( start_cash )
            fund.add_strategy( stra(fund) )
            trader.add_fund(fund)
        trader.run_fund(date_start, date_end)
        all_report = trader.get_report()

    trader.print_report(all_report)
    trader.plot(report = all_report, compare_index= compare_index, out_file= out_file)
