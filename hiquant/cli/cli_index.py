# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
import tabulate as tb

from ..utils import symbol_normalize, date_limit_from_options
from ..data_source import download_cn_index_stocks_list
from ..core import symbol_to_name
from ..core import get_order_cost
from ..core import list_signal_indicators
from ..core import get_cn_index_list_df, get_hk_index_list_df, get_us_index_list_df, get_world_index_list_df, get_index_daily
from ..core import Stock

def cli_index_help():
    syntax_tips = '''Syntax:
    __argv0__ index list <region>
    __argv0__ index plot <symbol> [<from_date>] [<to_date>] [<options>]
    __argv0__ index stocks <symbol> [-out=<out.csv>]

<action>
    list ....................... list index, following param: world, cn, us, hk, etc.
    plot ....................... plot the index
    stocks ..................... list stocks of this index

<symbol> ....................... stock symbol, like 600036
<from_date> .................... default from 3 year ago
<to_date> ...................... default to yesterday

<options> ...................... options to plot the stock
    -ma, -macd, -kdj, etc. ..... add some indicators
    -all ....................... add all indicators
    -mix ....................... show trade result if mix trade signal of the indicators
    -top5 ...................... show only top 5 indicators according to result

Example:
    __argv0__ index list world
    __argv0__ index list cn
    __argv0__ index list us

    __argv0__ index plot sh000300 -ma
    __argv0__ index plot sh000300 20180101 -ma -macd -kdj
    __argv0__ index plot sh000300 20180101 20210101 -ma -macd -kdj

    __argv0__ index stocks sh000300 -out=stockpool/sh000300_stocks.csv

'''.replace('__argv0__',os.path.basename(sys.argv[0]))
    print(syntax_tips)

def cli_index_list(params, options):
    list_funcs = {
        'world': get_world_index_list_df,
        'cn': get_cn_index_list_df,
        'us': get_us_index_list_df,
        'hk': get_hk_index_list_df,
    }
    if (len(params) == 0) or (not (params[0] in list_funcs)):
        print('Error: index list expected param:', ', '.join(list(list_funcs.keys())))
        cli_index_help()
        return
    func = list_funcs[ params[0] ]
    df = func()
    print( tb.tabulate(df, headers='keys', showindex=True, tablefmt='psql') )
    print( 'Totally', df.shape[0], 'records.\n')

def cli_index_plot(params, options):
    symbol = symbol_normalize(params[0])
    name = symbol_to_name(symbol)

    date_start, date_end, limit = date_limit_from_options(options)

    df = get_index_daily(symbol)
    df = df[ df.index >= date_start ]
    df = df[ df.index < date_end ]

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

def cli_index_stocks(params, options):
    if len(params) > 0:
        symbol = params[0]
        if symbol.startswith('sh') or symbol.startswith('sz'):
            df = download_cn_index_stocks_list(symbol)
            print( tb.tabulate(df, headers='keys', showindex=True, tablefmt='psql') )
            print( 'Totally', df.shape[0], 'records.\n')

            for option in options:
                if ('-out=' in option) and option.endswith('.csv'):
                    out_csv_file = option.replace('-out=','')
                    df.to_csv(out_csv_file, index=False)
                    print('Saved to:', os.path.abspath(out_csv_file))
                    return
            return

    print('Expect param: China index symbol, with prefix sh or sz, like sh000300, sz399991, etc.\n')

def cli_index(params, options):

    if (len(params) == 0) or (params[0] == 'help'):
        cli_index_help()
        return

    action = params[0]
    params = params[1:]

    if action == 'list':
        cli_index_list(params, options)

    elif action in ['plot', 'view', 'show']:
        cli_index_plot(params, options)

    elif action == 'stocks':
        cli_index_stocks(params, options)

    else:
        print('invalid action:', action)
        cli_index_help()
