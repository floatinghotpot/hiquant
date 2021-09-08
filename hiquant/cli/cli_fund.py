# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
import tabulate as tb
import numpy as np
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
from cycler import cycler

from ..core import get_cn_fund_list, get_cn_fund_daily
from ..utils import date_from_str, dict_from_df

def cli_fund_help():
    syntax_tips = '''Syntax:
    __argv0__ fund list
    __argv0__ fund plot <symbol> <symbol> [<options>]

<symbol> ....................... stock symbol, like 600036
<from_date> .................... default from 3 year ago
<to_date> ...................... default to yesterday

<options> ...................... options to plot the fund

Example:
    __argv0__ fund list
    __argv0__ fund plot
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    print( syntax_tips )

# hiquant fund list
# hiquant fund list 多因子
def cli_fund_list(params, options):
    df = get_cn_fund_list()
    selected = total = df.shape[0]
    if len(params) > 0:
        df = df[ df['基金简称'].str.contains(params[0], na=False) ]
        selected = df.shape[0]
    print( tb.tabulate(df, headers='keys') )
    print( selected, 'of', total, 'funds selected.')

def cli_fund_read_fund_symbols(csv_file):
    df = pd.read_csv(csv_file, dtype=str)
    if 'symbol' in df:
        return df['symbol'].tolist()
    else:
        return []

# hiquant fund sharpe 002943
# hiquant fund sharpe 002943 005669
# hiquant fund sharpe 002943 005669 -days=365
def cli_fund_sharpe(params, options):
    if len(params) == 0:
        cli_fund_help()
        return

    if params[0].endswith('.csv'):
        params = cli_fund_read_fund_symbols(params[0])

    df_fund_list = get_cn_fund_list()
    fund_symbol_names = dict_from_df(df_fund_list, '基金代码', '基金简称')

    date_from = date_from_str('10 years ago')
    days = 365 * 10
    for option in options:
        if option.startswith('-days='):
            days = int(option.replace('-days=',''))
            date_from = date_from_str('{} days ago'.format(days))

    for param in params:
        if param in fund_symbol_names:
            name = param + ' - ' + fund_symbol_names[ param ]
        else:
            name = param
        print( '\n-----', name, '-----' )
        df = get_cn_fund_daily(symbol= param)
        df.columns = ['date', 'value', 'pct_change']
        df = df.astype({
            'date': 'datetime64',
            'value': 'float64',
            'pct_change': 'float64',
        })
        df = df.set_index('date', drop= True)
        df = df[ df.index >= date_from ]

        risk_free_rate = 0.03
        daily_sharpe_ratio = (df['pct_change'].mean() - risk_free_rate) / df['pct_change'].std()
        sharpe_ratio = round(daily_sharpe_ratio * (252 ** 0.5), 2)

        max_drawdown = (1 - df['value'] / df['value'].cummax()).max()
        max_drawdown = round(100 * max_drawdown, 2)

        logreturns = np.diff( np.log(df['value']) )
        volatility = np.std(logreturns)
        annualVolatility = volatility * (252 ** 0.5)
        annualVolatility = round(annualVolatility * 100, 2)

        print('sharpe:', sharpe_ratio, ', max drawdown:', max_drawdown, '%', ', annual volatility:', annualVolatility, '%')

    pass

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
    fund_symbol_names = dict_from_df(df_fund_list, '基金代码', '基金简称')

    date_from = date_from_str('10 years ago')
    for option in options:
        if option.startswith('-days='):
            days = int(option.replace('-days=',''))
            date_from = date_from_str('{} days ago'.format(days))

    for param in params:
        if param in fund_symbol_names:
            name = param + ' - ' + fund_symbol_names[ param ]
        else:
            name = param
        print( '\n-----', name, '-----' )
        df = get_cn_fund_daily(symbol= param)
        df.columns = ['date', 'value', 'pct_change']
        df = df.astype({
            'date': 'datetime64',
            'value': 'float64',
            'pct_change': 'float64',
        })
        df = df.set_index('date', drop= True)
        df = df[ df.index >= date_from ]
        df['value_trend'] = round(df['value'] / df['value'].iloc[0], 4)
        df['pct_return'] = round((df['value_trend'] - 1.0) * 100.0, 1)
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
    fund_symbol_names = dict_from_df(df_fund_list, '基金代码', '基金简称')

    date_from = date_from_str('10 years ago')
    for option in options:
        if option.startswith('-days='):
            days = int(option.replace('-days=',''))
            date_from = date_from_str('{} days ago'.format(days))

    df_funds = None
    for param in params:
        if param in fund_symbol_names:
            name = param + ' - ' + fund_symbol_names[ param ]
        else:
            name = param
        print( name )
        df = get_cn_fund_daily(symbol= param)
        df.columns = ['date', 'value', 'pct_change']
        df = df.astype({
            'date': 'datetime64',
            'value': 'float64',
            'pct_change': 'float64',
        })
        df = df.set_index('date', drop= True)
        df = df[ df.index >= date_from ]
        df['value_trend'] = round(df['value'] / df['value'].iloc[0], 4)
        df['pct_return'] = round((df['value_trend'] - 1.0) * 100.0, 1)
        if df_funds is None:
            df_funds = df[['pct_return']]
            df_funds.columns = [ name ]
        else:
            df_funds[ name ] = df['pct_return']
        #print(df)

    print(df_funds)

    df_funds.index = df_funds.index.strftime('%Y-%m-%d')
    df_funds.plot(kind='line', ylabel='return (%)')
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

    elif action in ['sharpe']:
        cli_fund_sharpe(params, options)

    elif action in ['view']:
        cli_fund_view(params, options)

    elif action in ['plot', 'show']:
        cli_fund_plot(params, options)

    else:
        print('invalid action:', action)
        cli_fund_help()
