# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys

import pandas as pd
import tabulate as tb

from ..core.data_cache import get_pepb_symmary_all, get_pepb_symmary_df
from ..utils import filter_with_options, sort_with_options

def cli_pepb(params, options):
    syntax_tips = '''Syntax:
    __argv0__ pepb <action> <symbols | symbos.csv | all> [options]

Action:
    update ................................. download PE/PB data and update PE/PE calculation
    view ................................... view PE/PB data with filters

Symbols:
    <symbols> .............................. stock symbol list, like 600036 000002
    <symbols.csv> .......................... stock symbol list csv file
    all .................................... all symbols

Options:
    -sortby=<col> .......................... sort by the column

    -pe=<from>-<to> ........................ sort by PE
    -pb=<from>-<to> ........................ sort by PB
    -pe_pos=<from>-<to> .................... sort by PE % position
    -pb_pos=<from>-<to> .................... sort by PB % position

    -out=<out.csv> ......................... export selected stocks into <out.csv> file

Example:
    __argv0__ pepb show 600036 000002 600276
    __argv0__ pepb show my-stocks.csv -pe_pos
    __argv0__ pepb show all
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    if (len(params) == 0) or (params[0] == 'help'):
        print( syntax_tips )
        return

    action = params[0]
    params = params[1:]

    if action not in ['update', 'view', 'show', 'filter']:
        print('\nError: invalid action: ', action)
        return

    if params[0] == 'all':
        df = get_pepb_symmary_all(force_update= (action == 'update'))
    else:
        if params[0].endswith('.csv'):
            stock_df = pd.read_csv(params[0], dtype=str)
            symbols = stock_df['symbol'].tolist()
        else:
            symbols = params
        df = get_pepb_symmary_df(symbols, force_update= (action == 'update'))

    total_n = df.shape[0]

    # now filter
    df = filter_with_options(df, options)
    filtered_n = df.shape[0]

    # now sort
    df = sort_with_options(df, options, by_default='pb_pos')

    print( tb.tabulate(df, headers='keys', tablefmt='psql') )

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
