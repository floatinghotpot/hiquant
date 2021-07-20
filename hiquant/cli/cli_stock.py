# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
import tabulate as tb

from ..utils import date_from_str, symbol_normalize
from ..core import symbol_to_name, get_cn_stock_list_df, get_hk_stock_list_df, get_us_stock_list_df
from ..core import list_signal_indicators, get_order_cost
from ..core import Market, Stock

def cli_stock_help():
    syntax_tips = '''Syntax:
    __argv0__ stock list <market>
    __argv0__ stock plot <symbol> [<from_date>] [<to_date>] [<options>]

<market>
    cn ......................... China market
    hk ......................... Hong Kong market
    us ......................... USA market

<symbol> ....................... stock symbol, like 600036
<from_date> .................... default from 3 year ago
<to_date> ...................... default to yesterday

<options> ...................... options to plot the stock
    -ma, -macd, -kdj, etc. ..... add some indicators
    -all ....................... add all indicators
    -mix ....................... show trade result if mix trade signal of the indicators
    -top5 ...................... show only top 5 indicators according to result

Example:
    __argv0__ stock list cn
    __argv0__ stock plot 600036 -ma
    __argv0__ stock plot 600036 20180101 -ma -macd -kdj
    __argv0__ stock plot 600036 20180101 20210101 -ma -macd -kdj
    __argv0__ stock plot 600036 -ma -macd -mix
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    print( syntax_tips )

def cli_stock_list(params, options):
    list_funcs = {
        'cn': get_cn_stock_list_df,
        'us': get_us_stock_list_df,
        'hk': get_hk_stock_list_df,
    }
    if (len(params) == 0) or (not (params[0] in list_funcs)):
        print('Error: stock list expected param:', ', '.join(list(list_funcs.keys())))
        cli_stock_help()
        return
    func = list_funcs[ params[0] ]
    df = func()
    df['name'] = df['name'].str.slice(stop=60)
    print( tb.tabulate(df, headers='keys', showindex=False, tablefmt='psql') )
    print( 'Totally', df.shape[0], 'rows.\n')

def cli_stock_plot(params, options):
    symbol = symbol_normalize(params[0])
    name = symbol_to_name(symbol)

    date_start = date_from_str(params[1] if len(params) > 1 else '3 years ago')
    date_end = date_from_str(params[2] if len(params) > 2 else 'yesterday')

    market = Market(date_start, date_end)
    df = market.get_daily(symbol, start = date_start, end = date_end)
    stock = Stock(symbol, name, df)

    all_indicators = list_signal_indicators()

    indicators = []
    topN = 5
    inplace = True
    out_file = None
    for option in options:
        if option.startswith('-top'):
            topN = int(option.replace('-top',''))
        elif option.startswith('-out=') and (option.endswith('.png') or option.endswith('.jpg')):
            out_file = option.replace('-out=', '')
        else:
            k = option.replace('-','')
            if (k in all_indicators) and (not k in indicators):
                indicators.append(k)
    if '-all' in options:
        indicators = all_indicators
        inplace = False

    mix = '-mix' in options

    # add indicators and calculate performance
    stock.add_indicator(indicators, mix=mix, inplace= inplace, order_cost = get_order_cost())

    rank_df = stock.rank_indicator(by = 'final')
    if rank_df.shape[0] > 0:
        print(rank_df)

    # find top indicators
    ranked_indicators = rank_df['indicator'].tolist()
    other_indicators = ranked_indicators[topN:]
    df.drop(columns = other_indicators, inplace=True)

    stock.plot(out_file= out_file)

def cli_stock(params, options):
    if (len(params) == 0) or (params[0] == 'help'):
        cli_stock_help()
        return

    action = params[0]
    params = params[1:]

    if action == 'list':
        cli_stock_list(params, options)

    elif action in ['plot', 'view', 'show']:
        cli_stock_plot(params, options)

    else:
        print('invalid action:', action)
        cli_stock_help()
