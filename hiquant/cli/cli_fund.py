# -*- coding: utf-8; py-indent-offset:4 -*-

import os, sys
import tabulate as tb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ..core import get_cn_fund_list, get_cn_fund_daily
from ..utils import date_from_str, dict_from_df, datetime_today, sort_with_options, filter_with_options

def cli_fund_help():
    syntax_tips = '''Syntax:
    __argv0__ fund list [<keyword>]
    __argv0__ fund update <all | symbols | symbols.csv>
    __argv0__ fund eval <all | symbols | symbols.csv> [-sortby=...] [-desc] [-filter_column=...-...]
    __argv0__ fund view <symbols | symbols.csv>
    __argv0__ fund plot <symbols | symbols.csv> [<options>]

Options:
    -sortby=<col> .................. sort by the column
    -sharpe=2.5- ................... sharpe value between <from> to <to>
    -max_drawdown=-20 .............. max_drawdown between <from> to <to>
    -volatility=-20 ................ volatility between <from> to <to>

Example:
    __argv0__ fund list 多因子
    __argv0__ fund update data/myfunds.csv
    __argv0__ fund eval data/myfunds.csv -sortby=sharpe -desc -limit=20
    __argv0__ fund view 002943 005669 -days=365
    __argv0__ fund plot 002943 005669 000209 -days=365
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    print( syntax_tips )

# hiquant fund list
# hiquant fund list 多因子
def cli_fund_list(params, options):
    df = get_cn_fund_list(check_date= datetime_today())
    selected = total = df.shape[0]
    if len(params) > 0:
        df = df[ df['name'].str.contains(params[0], na=False) ]
        selected = df.shape[0]
    print( tb.tabulate(df, headers='keys') )
    print( selected, 'of', total, 'funds selected.')

    out_csv_file = ''
    for k in options:
        if k.startswith('-out=') and k.endswith('.csv'):
            out_csv_file = k.replace('-out=', '')
    if out_csv_file:
        df = df[['symbol', 'name']]
        df.to_csv(out_csv_file, index= False)
        print('Exported to:', out_csv_file)
        print(df)

def cli_fund_read_fund_symbols(csv_file):
    df = pd.read_csv(csv_file, dtype=str)
    if 'symbol' in df:
        return df['symbol'].tolist()
    else:
        return []

# hiquant fund update <symbols>
# hiquant fund update <symbols.csv>
# hiquant fund update all
def cli_fund_update(params, options):
    if len(params) == 0:
        cli_fund_help()
        return

    df_fund_list = get_cn_fund_list(check_date= datetime_today())
    fund_symbol_names = dict_from_df(df_fund_list, 'symbol', 'name')

    if params[0] == 'all':
        params = df_fund_list['symbol'].tolist()
    elif params[0].endswith('.csv'):
        params = cli_fund_read_fund_symbols(params[0])

    i = 0
    n = len(params)
    for param in params:
        i += 1
        name = param + ' - ' + fund_symbol_names[ param ]
        print('{}/{} - updating {} ...'.format(i, n, name))
        try:
            df = get_cn_fund_daily(symbol= param, check_date= datetime_today())
        except (KeyError, ValueError, IndexError) as err:
            print('error downloading', name)
            pass

    print('Done.')

def eval_fund_list(df_fund_list, days):
    date_from = date_from_str('{} days ago'.format(days))
    eval_table = []
    for index, row in df_fund_list.iterrows():
        param = row['symbol']
        name = row['name']
        buy_state = row['buy_state']
        sell_state = row['sell_state']
        fee = row['fee']
        print('\r', index, '-', param, '-', name, '...', end='', flush= True)

        try:
            df = get_cn_fund_daily(symbol= param)
        except (KeyError, ValueError, IndexError) as err:
            print('\nerror downloading', name, ', skip.')
            continue

        fund_start = min(df.index)
        fund_days = (datetime_today() - fund_start).days

        if fund_days < days:
            continue

        df = df[ df.index >= date_from ]

        try:
            pct_cum = df['value'].iloc[-1] / df['value'].iloc[0] - 1.0
            pct_cum = round(pct_cum * 100, 2)
        except (KeyError, ValueError, IndexError) as err:
            print('error calculating', param, name, ', skip.')
            continue

        risk_free_rate = 0.03
        daily_sharpe_ratio = (df['pct_change'].mean() - risk_free_rate) / df['pct_change'].std()
        sharpe_ratio = round(daily_sharpe_ratio * (252 ** 0.5), 2)

        max_drawdown = (1 - df['value'] / df['value'].cummax()).max()
        max_drawdown = round(100 * max_drawdown, 2)

        logreturns = np.diff( np.log(df['value']) )
        volatility = np.std(logreturns)
        annualVolatility = volatility * (252 ** 0.5)
        annualVolatility = round(annualVolatility * 100, 2)
        eval_table.append([param, name, fund_start, fund_days, days, pct_cum, sharpe_ratio, max_drawdown, annualVolatility, buy_state, sell_state, fee])

    df = pd.DataFrame(eval_table, columns=['symbol', 'name', 'fund_start', 'fund_days', 'calc_days', 'pct_cum', 'sharpe', 'max_drawdown', 'volatility', 'buy_state', 'sell_state', 'fee'])
    df['fund_start'] = df['fund_start'].dt.date
    return df

# hiquant fund eval 002943 005669
# hiquant fund eval 002943 005669 -days=365
# hiquant fund eval data/myfunds.csv -days=365
# hiquant fund eval all -days=365 -sortby=sharpe -desc
def cli_fund_eval(params, options):
    if len(params) == 0:
        cli_fund_help()
        return

    df_fund_list = get_cn_fund_list()

    if params[0] == 'all':
        pass
    elif params[0].endswith('.csv'):
        params = cli_fund_read_fund_symbols(params[0])
        df_fund_list = df_fund_list[ df_fund_list['symbol'].isin(params) ]
    else:
        df_fund_list = df_fund_list[ df_fund_list['symbol'].isin(params) ]

    limit = 0
    days = None
    for option in options:
        if option.startswith('-days='):
            days = int(option.replace('-days=',''))
        if option.startswith('-years='):
            days = int(option.replace('-years=','')) * 365
        if option.startswith('-limit='):
            limit = int(option.replace('-limit=',''))
    if days is None:
        days = 365 * 1

    df_eval = eval_fund_list(df_fund_list, days)

    df_eval = df_eval[ df_eval['buy_state'].isin(['限大额','开放申购']) ]
    df_eval = filter_with_options(df_eval, options)
    df_eval = sort_with_options(df_eval, options, by_default='sharpe')
    if limit > 0:
        df_eval = df_eval.head(limit)

    print('\r', end= '', flush= True)
    print( tb.tabulate(df_eval, headers='keys') )

    out_csv_file = ''
    for k in options:
        if k.startswith('-out=') and k.endswith('.csv'):
            out_csv_file = k.replace('-out=', '')
    if out_csv_file:
        df = df_eval[['symbol', 'name']]
        df.to_csv(out_csv_file, index= False)
        print('Exported to:', out_csv_file)
        print(df)

# hiquant fund view 002943
# hiquant fund view 002943 005669
# hiquant fund view 002943 005669 -days=365
def cli_fund_view(params, options):
    if len(params) == 0:
        cli_fund_help()
        return

    if params[0].endswith('.csv'):
        params = cli_fund_read_fund_symbols(params[0])

    df_fund_list = get_cn_fund_list()
    fund_symbol_names = dict_from_df(df_fund_list, 'symbol', 'name')

    days = None
    for option in options:
        if option.startswith('-days='):
            days = int(option.replace('-days=',''))
        if option.startswith('-years='):
            days = int(option.replace('-years=','')) * 365
    if days is None:
        days = 365 * 1
    date_from = date_from_str('{} days ago'.format(days))

    for param in params:
        if param in fund_symbol_names:
            name = param + ' - ' + fund_symbol_names[ param ]
        else:
            name = param
        print( '\n-----', name, '-----' )
        df = get_cn_fund_daily(symbol= param)
        df = df[ df.index >= date_from ]
        df['value_trend'] = round(df['value'] / df['value'].iloc[0], 4)
        df['pct_cum'] = round((df['value_trend'] - 1.0) * 100.0, 1)
        print(df)

    pass

# hiquant fund plot 002943
# hiquant fund plot 002943 005669
# hiquant fund plot 002943 005669 -days=365
def cli_fund_plot(params, options):
    if len(params) == 0:
        cli_fund_help()
        return

    if params[0].endswith('.csv'):
        params = cli_fund_read_fund_symbols(params[0])

    df_fund_list = get_cn_fund_list()
    fund_symbol_names = dict_from_df(df_fund_list, 'symbol', 'name')

    days = None
    for option in options:
        if option.startswith('-days='):
            days = int(option.replace('-days=',''))
        if option.startswith('-years='):
            days = int(option.replace('-years=','')) * 365
    if days is None:
        days = 365 * 1
    date_from = date_from_str('{} days ago'.format(days))

    df_funds = None
    for param in params:
        if param in fund_symbol_names:
            name = param + ' - ' + fund_symbol_names[ param ]
        else:
            name = param
        print( name )
        df = get_cn_fund_daily(symbol= param)
        df = df[ df.index >= date_from ]
        df['value_trend'] = round(df['value'] / df['value'].iloc[0], 4)
        df['pct_cum'] = round((df['value_trend'] - 1.0) * 100.0, 1)
        if df_funds is None:
            df_funds = df[['pct_cum']]
            df_funds.columns = [ name ]
        else:
            df_funds[ name ] = df['pct_cum']
        #print(df)

    print(df_funds)

    df_funds.index = df_funds.index.strftime('%Y-%m-%d')
    df_funds.plot(kind='line', ylabel='return (%)', figsize=(10,6))
    plt.show()

    pass

def cli_fund(params, options):
    if (len(params) == 0) or (params[0] == 'help'):
        cli_fund_help()
        return

    action = params[0]
    params = params[1:]

    if action == 'list':
        cli_fund_list(params, options)

    elif action == 'update':
        cli_fund_update(params, options)

    elif action in ['eval']:
        cli_fund_eval(params, options)

    elif action in ['view']:
        cli_fund_view(params, options)

    elif action in ['plot', 'show']:
        cli_fund_plot(params, options)

    else:
        print('invalid action:', action)
        cli_fund_help()
