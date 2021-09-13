# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys

import pandas as pd
import tabulate as tb

from ..core.data_cache import get_pepb_symmary_df
from ..utils import filter_with_options, sort_with_options

def cli_pepb_help():
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
    __argv0__ pepb view 600036 000002 600276
    __argv0__ pepb view my-stocks.csv -pe_pos
    __argv0__ pepb view all
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    print( syntax_tips )

def cli_pepb_view(params, options, force_update = False):
    if params[0] == 'all':
        df = get_pepb_symmary_df()
    else:
        if params[0].endswith('.csv'):
            stock_df = pd.read_csv(params[0], dtype=str)
            symbols = stock_df['symbol'].tolist()
        else:
            symbols = params
        df = get_pepb_symmary_df(symbols)

    total_n = df.shape[0]

    # now filter
    df = filter_with_options(df, options)
    filtered_n = df.shape[0]

    # now sort
    df = sort_with_options(df, options, by_default='pb_pos')

    print( tb.tabulate(df, headers='keys', tablefmt='psql') )

    print('{} out of {} records selected.'.format(filtered_n, total_n))

    out_xlsx_file = ''
    out_csv_file = ''
    for k in options:
        if k.startswith('-out='):
            if k.endswith('.xlsx'):
                out_xlsx_file = k.replace('-out=', '')
            if k.endswith('.csv'):
                out_csv_file = k.replace('-out=', '')

    if out_csv_file:
        df = df[['symbol', 'name']]
        df.to_csv(out_csv_file, index= False)
        print('Exported to:', out_csv_file)
        print(df)

    if out_xlsx_file:
        name_col = df.pop('name')
        df.insert(1, 'name', name_col)
        df = df.rename(columns={
            'symbol':'代码',
            'name': '名称',
            'pe': '市盈率',
            'pb': '市净率',
            'pe_pos': '市盈率百分位',
            'pb_pos': '市净率百分位',
            'pe_ratio': '市盈率均值比率',
            'pb_ratio': '市净率均值比率',
        })
        df.to_excel(out_xlsx_file)
        print('Exported to:', out_xlsx_file)

    print('')

def cli_pepb(params, options):
    if (len(params) == 0) or (params[0] == 'help'):
        cli_pepb_help()
        return

    action = params[0]
    params = params[1:]

    if action == 'update':
        cli_pepb_view(params, options, force_update= True)

    elif action in ['view', 'show', 'filter']:
        cli_pepb_view(params, options, force_update= False)

    else:
        print('invalid action:', action)
        cli_pepb_help()
