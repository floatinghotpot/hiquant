# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
import datetime as dt

from ..utils import date_from_str, dict_from_config_items
from ..core import get_lang, get_hiquant_conf
from ..core import Market, Trader, Fund, SimulatedAgent

def get_strategy_template():
    return '''
# -*- coding: utf-8; py-indent-offset:4 -*-
import pandas as pd
import hiquant as hq

class MyStrategy( hq.BasicStrategy ):
    def __init__(self, fund):
        super().__init__(fund, __file__)
        self.max_stocks = 10
        self.max_weight = 1.2
        self.stop_loss = 1 + (-0.10)
        self.stop_earn = 1 + (+0.20)

    def schedule_task(self, trader):
        trader.run_daily(self.trade, None, time='09:30')
        trader.run_on_bar_update(self.trade, None)

    def select_stock(self):
        return ['AAPL', 'MSFT', 'AMZN', 'TSLA', '0700.HK']

    def gen_trade_signal(self, symbol, init_data = False):
        market = self.fund.market
        if init_data:
            df = market.get_daily(symbol)
        else:
            df = market.get_daily(symbol, end = market.current_date, count = 26+9)

        dif, dea, macd_hist = hq.MACD(df.close, fast=12, slow=26, signal=9)
        signal = pd.Series( hq.CROSS(dif, dea), index=df.index )

        # Notice!!! Important !!!
        # if we used the close price of the day to calc indicator,
        # to avoid "future data or function" in backtesting, it should not be used for today's trading
        # either we trade at 14:30 before market close
        # or, shift(1) and trade next morning
        return signal.shift(1).fillna(0)

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
    if (len(params) == 0) or (not (params[0].endswith('.py'))):
        print('\nError: A strategy filename ending with .py is expected.\n')
        return

    file_to_create = params[0]
    if os.path.isfile(file_to_create):
        print('\nError: file already exists:', file_to_create)
        return

    template_content = get_strategy_template()
    fp = open(file_to_create, 'w')
    fp.write(template_content)
    fp.close()

    print('-' * 80)
    print( template_content )
    print('-' * 80)

    print( 'Strategy file created:\n  ', os.path.abspath(file_to_create))
    print( '\nPlease edit file content before running.' )

def cli_strategy_backtest(params, options):
    if (len(params) == 0) or (not (params[0].endswith('.py'))):
        print('\nError: A strategy filename ending with .py is expected.\n')
        return

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

    config = get_hiquant_conf()
    main_conf = dict_from_config_items(config.items('main'))
    if 'compare_index' in main_conf:
        compare_index = main_conf[ 'compare_index' ]
    else:
        compare_index = 'sh000300' if (get_lang() == 'zh') else '^GSPC'

    out_file = None
    for option in options:
        if option.startswith('-out=') and option.endswith('.png'):
            out_file = option.replace('-out=', '')
        elif option.startswith('-cmp='):
            compare_index = option.replace('-cmp=', '')

    # compare with an index
    trader.plot(compare_index= compare_index, out_file= out_file)

    print('Done.\n')

def cli_strategy_help():
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

    print( syntax_tips )

def cli_strategy(params, options):
    if (len(params) == 0) or (params[0] == 'help'):
        cli_strategy_help()
        return

    action = params[0]
    params = params[1:]

    if action == 'create':
        cli_strategy_create(params, options)

    elif action == 'backtest':
        cli_strategy_backtest(params, options)

    else:
        print('\nError: unknown action:', action)
        cli_strategy_help()
