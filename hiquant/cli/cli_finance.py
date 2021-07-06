# -*- coding: utf-8; py-indent-offset:4 -*-
import os
import sys

import pandas as pd
import tabulate as tb

from ..core.data_cache import get_finance_indicator_all, get_finance_indicator_df
from ..utils import sort_with_options, filter_with_options

def cli_finance(params, options):
    syntax_tips = '''Syntax:
    __argv0__ finance <action> <symbols | stockpool.csv | all> [options]

Action:
    update ......................... download finance reports and update finance indicators
    view ........................... view finance indicators with filters

Symbols:
    <symbols> ...................... stock symbol list, like 600036 000002
    <stockpool.csv> ................ stock pool csv file
    all ............................ all symbols

Options:
    -sortby=<col> .................. sort by the column

    -ipo_years=<from>-<to> ......... IPO years between <from> to <to>
    -earn_ttm=<from>-<to> .......... annual earn between <from> to <to>
    -roe=<from>-<to> ............... ROE between <from> to <to>
    -grow_rate=<from>-<to> ......... average yearly grow rate between <from> to <to>
    -3yr_grow_rate=<from>-<to> ..... recent 3 year grow rate between <from> to <to>

    -tab ........................... show data in table format

    -out=<out.csv> ................. export selected stocks into <out.csv> file

Example:
    __argv0__ finance show 600036 000002 600276
    __argv0__ finance show my-stocks.csv
    __argv0__ finance show all -ipo_years=1- -earn_ttm=1.0- -roe=0.15- -3yr_grow_rate=0.15- -sortby=roe -out=good_stock.csv
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    if (len(params) == 0) or (params[0] == 'help'):
        print(syntax_tips)
        return

    action = params[0]
    params = params[1:]

    if action not in ['update', 'view', 'show', 'filter']:
        print('\nError: invalid action: ', action)
        return

    if params[0] == 'all':
        df = get_finance_indicator_all(force_update= (action == 'update'))
    else:
        if params[0].endswith('.csv'):
            stock_df = pd.read_csv(params[0], dtype=str)
            symbols = stock_df['symbol'].tolist()
        else:
            symbols = params
        df = get_finance_indicator_df(symbols, force_update= (action == 'update'))

    total_n = df.shape[0]

    # now filter
    df = filter_with_options(df, options)
    filtered_n = df.shape[0]

    # now sort
    df = sort_with_options(df, options, by_default='roe')

    if '-tab' in options:
        if filtered_n > 30:
            print( tb.tabulate(df.head(15), headers='keys', tablefmt='psql') )
            print( ' ...... too many data to show ......')
            print( tb.tabulate(df.tail(15), headers='keys', tablefmt='psql') )
        else:
            print( tb.tabulate(df, headers='keys', tablefmt='psql') )
    else:
        print('-' * 80)
        print(df)
        print('-' * 80)


    print('{} out of {} records selected.'.format(filtered_n, total_n))

    out_csv_file = ''
    for k in options:
        if k.startswith('-out=') and k.endswith('.csv'):
            out_csv_file = k.replace('-out=', '')
    if out_csv_file:
        df = df[['symbol', 'name']]
        df.to_csv(out_csv_file, index= False)
        print('Exported to:', out_csv_file)
        print(df)

    print('')
