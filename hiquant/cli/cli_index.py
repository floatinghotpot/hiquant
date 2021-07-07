# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
import tabulate as tb

from ..core import symbol_normalize, symbol_to_name
from ..core import date_from_str, get_all_index_list_df, get_order_cost
from ..core import list_signal_indicators
from ..core import Market, Stock

def cli_index(params, options):
    syntax_tips = '''Syntax:
    __argv0__ index <symbol> [<from_date>] [<to_date>] [<options>]

<symbol> ....................... stock symbol, like 600036
<from_date> .................... default from 3 year ago
<to_date> ...................... default to yesterday

<options> ...................... options to plot the stock
    -ma, -macd, -kdj, etc. ..... add some indicators
    -all ....................... add all indicators
    -mix ....................... show trade result if mix trade signal of the indicators
    -top5 ...................... show only top 5 indicators according to result

Example:
    __argv0__ index sh000300 -ma
    __argv0__ index sh000300 20180101 -ma -macd -kdj
    __argv0__ index sh000300 20180101 20210101 -ma -macd -kdj
    __argv0__ index sh000300 -ma -macd -mix
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
        df = get_all_index_list_df(force_update= force_update)
        print( tb.tabulate(df, headers='keys', showindex=False, tablefmt='psql') )
        print( 'Totally', df.shape[0], 'records.\n')
        return

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
