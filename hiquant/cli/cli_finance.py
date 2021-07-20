# -*- coding: utf-8; py-indent-offset:4 -*-
import os
import sys
import datetime as dt
import pandas as pd
import tabulate as tb

from ..core.data_cache import get_finance_indicator_df
from ..utils import sort_with_options, filter_with_options, date_from_str, datetime_today

def cli_finance_help():
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
    __argv0__ finance view 600036 000002 600276
    __argv0__ finance view my-stocks.csv
    __argv0__ finance view all -ipo_years=1- -earn_ttm=1.0- -roe=0.15- -3yr_grow_rate=0.15- -sortby=roe -out=good_stock.csv
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    print(syntax_tips)

def cli_finance_update(params, options):
    if len(params) > 0:
        check_date = date_from_str(params[0])
    else:
        # first day of this quarter
        today = datetime_today()
        quarter_first_month = (today.month -1) // 3 * 3 + 1
        check_date = dt.datetime(today.year, quarter_first_month, 1)
        print('checking date:', check_date)

    df = get_finance_indicator_df(check_date= check_date)
    print(df)

def cli_finance_view(params, options):
    df = get_finance_indicator_df()

    if (len(params) == 0) or (params[0] == 'all'):
        pass
    else:
        if params[0].endswith('.csv'):
            stock_df = pd.read_csv(params[0], dtype=str)
            symbols = stock_df['symbol'].tolist()
        else:
            symbols = params
        df = df[ df['symbol'].isin(symbols) ]

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

def cli_finance(params, options):
    if (len(params) == 0) or (params[0] == 'help'):
        cli_finance_help()
        return

    action = params[0]
    params = params[1:]

    if action not in ['update', 'view', 'show', 'filter']:
        print('\nError: invalid action: ', action)
        return

    if action == 'update':
        cli_finance_update(params, options)
        return
    elif action in ['view', 'show', 'filter']:
        cli_finance_view(params, options)
    else:
        print('invalid action:', action)
        cli_finance_help()
