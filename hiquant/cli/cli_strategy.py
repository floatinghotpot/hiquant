# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
import datetime as dt

from ..utils import date_from_str, datetime_today
from ..core import Market, Trader, Fund, SimulatedAgent

def get_strategy_template():
    return '''
# -*- coding: utf-8; py-indent-offset:4 -*-
import pandas as pd
import talib
import hiquant as hq

class MyStrategy( hq.BasicStrategy ):
    def __init__(self, fund):
        super().__init__(fund, __file__)
        self.max_stocks = 10
        self.max_weight = 1.2
        self.stop_loss = 1 + (-0.10)
        self.stop_earn = 1 + (+0.20)

    def select_stock(self):
        return ['AAPL', 'MSFT', 'AMZN', 'TSLA', '0700.HK']

    def gen_trade_signal(self, symbol, init_data = False):
        market = self.fund.market
        if init_data:
            df = market.get_daily(symbol)
        else:
            df = market.get_daily(symbol, end = market.current_date, count = 26+9)

        dif, dea, macd_hist = talib.MACD(df.close, fastperiod=12, slowperiod=26, signalperiod=9)
        return pd.Series( hq.CROSS(dif, dea), index=df.index )

    def get_signal_comment(self, symbol, signal):
        return 'MACD golden cross' if (signal > 0) else 'MACD dead cross'

def init(fund):
    strategy = MyStrategy(fund)

if __name__ == '__main__':
    backtest_args = dict(
        #start_cash= 1000000.00,
        #date_start= hq.date_from_str('3 years ago'),
        #date_end= hq.date_from_str('yesterday'),
        #out_file= 'output/demo.png',
        #parallel= True,
        compare_index= '^GSPC',
    )
    hq.backtest_strategy( MyStrategy, **backtest_args )

'''

def cli_strategy_create(params, options):
    template_content = get_strategy_template()

    file_to_create = params[0]
    if os.path.isfile(file_to_create):
        print('\nError: file already exists:', file_to_create)
        return

    fp = open(file_to_create, 'w')
    fp.write(template_content)
    fp.close()

    print('-' * 80)
    print( template_content )
    print('-' * 80)

    print( 'Strategy file created:\n  ', os.path.abspath(file_to_create))
    print( '\nPlease edit file content before running.' )

def cli_strategy_backtest(params, options):
    strategy_file = params[0]
    start = params[1] if len(params) > 1 else '3 years ago'
    end = params[2] if len(params) > 2 else 'yesterday'
    if '-q' in options:
        start = '3 months ago'
        end = '1 week ago'
    verbose = '-d' in options
    date_start = date_from_str( start )
    date_end = date_from_str( end )

    start_tick = dt.datetime.now()

    # market is a global singleton
    market = Market(date_start - dt.timedelta(days=90), date_end)
    trader = Trader(market)

    fund_conf = {
        'strategy': strategy_file,
    }
    fund = Fund(market, trader, fund_conf)
    agent = SimulatedAgent(market)
    fund.set_agent(agent)
    fund.set_name( os.path.basename(strategy_file) )
    fund.set_start_cash( 1000000.00 )
    trader.add_fund(fund)
    market.set_verbose( verbose )
    trader.set_verbose( verbose )
    trader.run_fund(date_start, date_end)
    trader.print_report()
    end_tick = dt.datetime.now()
    print('time used:', (end_tick - start_tick))

    compare_index = '^GSPC'
    out_file = None
    for option in options:
        if option.startswith('-out=') and option.endswith('.png'):
            out_file = option.replace('-out=', '')
        elif option.startswith('-cmp='):
            compare_index = option.replace('-cmp=', '')

    # compare with an index
    trader.plot(compare_index= compare_index, out_file= out_file)

    print('Done.\n')

def cli_strategy(params, options):
    syntax_tips = '''Syntax:
    __argv0__ strategy <action> <my_strategy.py> [options]

Actions:
    create ................ create a strategy python file from template
    backtest .............. backtest a strategy with default settings

<my_strategy.py> ............ a strategy python file

[options]
    -cmp=<compare index> .... compare with the index
    -out=<output.png> ....... output the plot to png file

Example:
    __argv0__ strategy create strategy/my_strategy.py
    __argv0__ strategy backtest strategy/my_strategy.py 20180101 -cmp=sh000300 -out=output/backtest.png

Alias:
    __argv0__ backtest strategy/my_strategy.py 20180101
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    if (len(params) == 0) or (params[0] == 'help'):
        print( syntax_tips )
        return

    action = params[0]
    params = params[1:]

    fund_tools = {
        'create': cli_strategy_create,
        'backtest': cli_strategy_backtest,
    }
    if action in fund_tools.keys():
        if (len(params) == 0) or (not (params[0].endswith('.py'))):
            print('\nError: A strategy filename ending with .py is expected.\n')
            return
        func = fund_tools[ action ]
        func(params, options)
    else:
        print('\nError: unknown action:', action)
        print( syntax_tips )


