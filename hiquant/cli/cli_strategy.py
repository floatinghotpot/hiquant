# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys

def get_strategy_template():
    return '''
import pandas as pd
import talib

from hiquant import *

class MyStrategy( BasicStrategy ):
    def __init__(self, fund, strategy_file):
        super().__init__(fund, strategy_file)
        self.max_stocks = 10
        self.max_weight = 1.2
        self.stop_loss = 1 + (-0.10)
        self.stop_earn = 1 + (+0.20)

    def select_stock(self):
        return ['600036', '300122', '600519', '300357', '601888']

    def gen_trade_signal(self, symbol, init_data = False):
        market = self.fund.market
        if init_data:
            df = market.get_daily(symbol)
        else:
            df = market.get_daily(symbol, end = market.current_date, count = 26+9)

        dif, dea, macd_hist = talib.MACD(df.close, fastperiod=12, slowperiod=26, signalperiod=9)
        return pd.Series( CROSS(dif, dea), index=df.index )

    def get_signal_comment(self, symbol, signal):
        return 'MACD golden cross' if (signal > 0) else 'MACD dead cross'

def init(fund):
    strategy = MyStrategy(fund, __file__)

    trader = fund.trader
    trader.run_daily(before_market_open, strategy, time='before_open')
    trader.run_on_bar_update(trade, strategy)
    trader.run_daily(trade, strategy, time='14:30')
    trader.run_daily(after_market_close, strategy, time='after_close')

def before_market_open(strategy):
    pass

def trade(strategy):
    strategy.trade()

def after_market_close(strategy):
    pass
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

def cli_strategy_bench(params, options):
    pass

def cli_strategy_clone(params, options):
    pass

def cli_strategy_publish(params, options):
    pass

def cli_strategy(params, options):
    syntax_tips = '''Syntax:
    __argv0__ strategy <action> <my_strategy.py> [options]

Actions:
    create ................ create a strategy python file from template

<my_strategy.py> ............ a strategy python file

Example:
    __argv0__ strategy create strategy/my_strategy.py
    __argv0__ strategy bench strategy/my_strategy.py 20180101
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    if (len(params) == 0) or (params[0] == 'help'):
        print( syntax_tips )
        return

    action = params[0]
    params = params[1:]

    fund_tools = {
        'create': cli_strategy_create,

        'bench': cli_strategy_bench,
        'clone': cli_strategy_clone,
        'publish': cli_strategy_publish,
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


