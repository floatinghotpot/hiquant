# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
from tabulate import tabulate
import configparser

from ..core import list_signal_indicators, dict_from_df, get_all_stock_list_df
from ..core import date_from_str, Market, Stock, OrderCost

def cli_stock(params, options):
    syntax_tips = '''Syntax:
    __argv0__ stock list [update]
    __argv0__ stock <symbol> [<from_date>] [<to_date>] [<options>]

<symbol> ....................... stock symbol, like 600036
<from_date> .................... default from 3 year ago
<to_date> ...................... default to yesterday

<options> ...................... options to plot the stock
    -ma, -macd, -kdj, etc. ..... add some indicators
    -all ....................... add all indicators
    -mix ....................... show trade result if mix trade signal of the indicators
    -top5 ...................... show only top 5 indicators according to result

Example:
    __argv0__ stock 600036 -ma
    __argv0__ stock 600036 20180101 -ma -macd -kdj
    __argv0__ stock 600036 20180101 20210101 -ma -macd -kdj
    __argv0__ stock 600036 -ma -macd -mix
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    if (len(params) == 0) or (params[0] == 'help'):
        print( syntax_tips )
        return

    if params[0] == 'list':
        force_update = False
        if len(params) > 1 and (params[1] == 'update'):
            force_update = True
        if '-update' in options or '-u' in options:
            force_update = True
        df = get_all_stock_list_df(force_update= force_update)
        print( tabulate(df, headers='keys', showindex=False, tablefmt='psql') )
        print( 'Totally', df.shape[0], 'rows.\n')
        return

    symbol_name = dict_from_df(get_all_stock_list_df(), 'symbol', 'name')

    symbol = params[0]
    if symbol in symbol_name:
        name = symbol_name[ symbol ]
    else:
        print('\nError: symbol not found in stock list:', symbol)
        return

    date_start = date_from_str(params[1] if len(params) > 1 else '3 years ago')
    date_end = date_from_str(params[2] if len(params) > 2 else 'yesterday')

    market = Market(date_start, date_end)
    df = market.get_daily(symbol, start = date_start, end = date_end)
    stock = Stock(symbol, name, df)

    all_indicators = list_signal_indicators()

    indicators = []
    topN = 5
    inplace = True
    for option in options:
        if option.startswith('-top'):
            topN = int(option.replace('-top',''))
        else:
            k = option.replace('-','')
            if (k in all_indicators) and (not k in indicators):
                indicators.append(k)
    if '-all' in options:
        indicators = all_indicators
        inplace = False

    mix = '-mix' in options

    config_file = 'hiquant.conf'
    if os.path.isfile(config_file):
        print( 'reading config from from:', config_file)
        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')
        order_cost_conf = {}
        print('[order_cost]')
        for k, v in config.items('order_cost'):
            order_cost_conf[k] = v
            print(k, '=', v)
        print('-' * 80)
        order_cost = OrderCost(
            float(order_cost_conf['close_tax']),
            float(order_cost_conf['open_commission']),
            float(order_cost_conf['close_commission']),
            float(order_cost_conf['min_commission']),
        )
    else:
        order_cost = OrderCost(0.001, 0.0003, 0.0003, 5.0)

    # add indicators and calculate performance
    stock.add_indicator(indicators, mix=mix, inplace= inplace, order_cost = order_cost)

    rank_df = stock.rank_indicator(by = 'final')
    if rank_df.shape[0] > 0:
        print(rank_df)

    # find top indicators
    ranked_indicators = rank_df['indicator'].tolist()
    other_indicators = ranked_indicators[topN:]
    df.drop(columns = other_indicators, inplace=True)

    stock.plot()
