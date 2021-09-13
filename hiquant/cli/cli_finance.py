# -*- coding: utf-8; py-indent-offset:4 -*-
import os
import sys
import datetime as dt
import pandas as pd
import tabulate as tb

from ..core.data_cache import get_cn_index_list_df, get_finance_indicator_df, update_finance_indicator_df, get_pepb_symmary_df
from ..utils import sort_with_options, filter_with_options

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
    __argv0__ finance update 600036 000002 600276
    __argv0__ finance update my-stocks.csv
    __argv0__ finance update all

    __argv0__ finance view 600036 000002 600276
    __argv0__ finance view my-stocks.csv
    __argv0__ finance view all -ipo_years=1- -earn_ttm=1.0- -roe=0.15- -3yr_grow_rate=0.15- -sortby=roe -out=good_stock.csv
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    print(syntax_tips)

def cli_finance_update(params, options):
    if len(params) == 0:
        cli_finance_help()
        return
    elif params[0] == 'all':
        symbols = get_cn_index_list_df()['symbol'].tolist()
    else:
        if params[0].endswith('.csv'):
            stock_df = pd.read_csv(params[0], dtype=str)
            symbols = stock_df['symbol'].tolist()
        else:
            symbols = params
    print(symbols)

    df = update_finance_indicator_df(symbols)
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
        df = df.set_index('symbol', drop= True)

        df['earn_speed'] = df['earn_speed'].round(3)
        df['earn_yoy'] = df['earn_yoy'].round(3)

        if '-pepb' in options:
            df_pepb = get_pepb_symmary_df(symbols)[['symbol','pe','pb','pe_pos','pb_pos']]
            df_pepb = df_pepb.set_index('symbol', drop= True)
            df = pd.concat([df, df_pepb], axis=1)
            df['peg'] = (df['pe'] / df['earn_yoy'] * 0.01).round(2)
            df['pe'] = df['pe'].round(1)
            df['pb'] = df['pb'].round(1)
            df.insert(0, 'symbol', df.index)
            df = df.reset_index(drop= True)

    total_n = df.shape[0]

    # now filter
    df = filter_with_options(df, options)
    filtered_n = df.shape[0]

    # now sort
    df = sort_with_options(df, options, by_default='roe')

    if '-tab' in options:
        print( tb.tabulate(df, headers='keys') )
    else:
        print('-' * 80)
        print(df)
        print('-' * 80)


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
        df_stocks = df[['symbol', 'name']]
        df_stocks.to_csv(out_csv_file, index= False)
        print('Exported to:', out_csv_file)
        print(df)

    if out_xlsx_file:
        name_col = df.pop('name')
        df.insert(1, 'name', name_col)
        df = df.drop(columns=['grow', 'share_grow', 'start_bvps', 'now_bvps', 'eps','assets','equity','shares'])
        df = df.rename(columns={
            'symbol':'代码',
            'name':'名称',
            'ipo_date':'上市日期',
            'ipo_years': '上市年数',
            'last_report': '最新财报',
            '3yr_grow_rate': '近3年增长率',
            'grow_rate': '平均增长率',
            'roe': 'ROE',
            '3yr_roe': '近3年ROE',
            'avg_roe': '平均ROE',
            'earn_speed': '利润环比增速',
            'earn_yoy': '利润同比增速',
            'debt_ratio': '资产负债率',
            'cash_ratio': '现金占比',
            'earn_ttm': '盈利TTM',
            'pe': 'PE',
            'pb': 'PB',
            'pe_pos': 'PE百分位',
            'pb_pos': 'PB百分位',
            'peg': 'PEG',
        })
        print( tb.tabulate(df, headers='keys') )
        df.to_excel(out_xlsx_file)
        print('Exported to:', out_xlsx_file)

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
