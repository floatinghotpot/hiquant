# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys

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


