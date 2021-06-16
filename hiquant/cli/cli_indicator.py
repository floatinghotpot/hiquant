# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
import pandas as pd
from tabulate import tabulate

from ..utils import date_from_str
from ..core import get_all_signal_indicators
from ..core import Market, Stock

def cli_indicator(params, options):
    syntax_tips = '''Syntax:
    __argv0__ indicator list
    __argv0__ indicator bench <stockpool.csv> [<start>] [<end>] [<options>]

Actions:
    list ....................... list indicators supported in this tool
    bench ...................... bench indicators for the given stockpool

Symbols:
    <stockpool.csv> ................ stock pool csv file

Options:
    -rankby=final | overall ........ rank by final or overall performance
    -topN .......................... keep top N indicators, by default -top2

    -out=<out.csv> ................. export selected stocks into <out.csv> file

Example:
    __argv0__ indicator list
    __argv0__ indicator bench mystock.csv -top1 -out=mystock_idx.csv
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    if (len(params) == 0) or (params[0] == 'help'):
        print( syntax_tips )
        return

    action = params[0]
    params = params[1:]

    if action == 'list':
        indicators = get_all_signal_indicators()
        table = []
        for k, values in indicators.items():
            table.append([k, values['type'], values['label'], ', '.join(values['cols'])])
        df = pd.DataFrame(table, columns=['indicator', 'type', 'label', 'data'])
        print( tabulate(df, headers='keys', tablefmt='psql') )
        return

    if action not in ['bench']:
        print('\nError: invalid action: ', action)
        return

    if (len(params) == 0) or ('.csv' not in params[0]):
        print('\nError: A filename with .csv is expected.\n')
        return

    csv_file = params[0]
    stock_df = pd.read_csv(csv_file, dtype=str)

    start = params[1] if (len(params) > 1) else '3 years ago'
    end = params[2] if (len(params) > 2) else '1 week ago'
    date_start = date_from_str(start)
    date_end = date_from_str(end)

    rankby = 'overall' if '-rankby=overall' in options else 'final'

    topN = 2
    for k in options:
        if k.startswith('-top'):
            topN = int(k.replace('-top',''))

    symbols = stock_df['symbol'].tolist()
    if 'cash' in symbols:
        symbols.remove('cash')
    market = Market(date_start, date_end)
    market.watch(symbols)

    all_indicators = get_all_signal_indicators().keys()
    indicators = []
    n = stock_df.shape[0]
    for i, row in stock_df.iterrows():
        symbol = row['symbol']
        name = row['name']
        if symbol == 'cash':
            indicators.append('')
            continue
        df = market.get_daily(symbol, start=date_start, end=date_end)
        stock = Stock(symbol, name, df)
        stock.add_indicator(all_indicators, mix=False, inplace=False)
        rank_df = stock.rank_indicator(by = rankby)
        if '-v' in options:
            print('-' * 20, symbol, name, '-' * 20)
            print(df)
            print('-' * 60)
            print(rank_df)
            print('-' * 60)
        else:
            print('\r...', i+1, '/', n, '... ', end = '', flush = True)

        # find top indicators
        ranked_indicators = rank_df['indicator'].tolist()
        indicators.append( ' + '.join( ranked_indicators[:topN] ).replace('.','') )
    stock_df['indicators'] = indicators
    print('\n')

    print( tabulate(stock_df, headers='keys', tablefmt='psql') )

    out_csv_file = ''
    for k in options:
        if k.startswith('-out=') and k.endswith('.csv'):
            out_csv_file = k.replace('-out=', '')
    if out_csv_file:
        stock_df.to_csv(out_csv_file, index= False)
        print('Exported to:', out_csv_file)

    print('')
