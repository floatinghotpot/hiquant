# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
import datetime as dt
import pandas as pd
import tabulate as tb
import matplotlib.pyplot as plt

from ..utils import date_from_str
from ..core import get_cn_stock_fund_flow_rank, get_all_symbol_name
from ..core import Market

def cli_fundflow_rank(symbols, options):
    days = '1d'
    for d in ['-1d', '-3d', '-5d', '-10d']:
        if d in options:
            days = d.replace('-', '')

    df = get_cn_stock_fund_flow_rank(days= days)
    df = df[ df['symbol'].isin(symbols) ]
    #df = df[ (df['main_pct'] > 3) | (df['main_pct'] < -3) ]

    fundflow_col = 'main_pct' if ('-pct' in options) else 'main_fund'
    df = df.sort_values(by=fundflow_col, ascending=False).reset_index(drop=True)
    df = df.head(50)

    df = df.drop(columns=['super_pct', 'large_pct', 'medium_pct', 'small_pct'])
    print( tb.tabulate(df, headers='keys', tablefmt='psql') )

def trim_axs(axs, N):
    """
    Reduce *axs* to *N* Axes. All further Axes are removed from the figure.
    """
    axs = axs.flat
    for ax in axs[N:]:
        ax.remove()
    return axs[:N]

def cli_fundflow_view(symbols, options):
    days = '1d'
    for d in ['-1d', '-3d', '-5d', '-10d']:
        if d in options:
            days = d.replace('-', '')

    df = get_cn_stock_fund_flow_rank(days= days)
    df = df[ df['symbol'].isin(symbols) ]
    df = df.head(100)

    fundflow_col = 'main_pct' if ('-pct' in options) else 'main_fund'
    df = df.sort_values(by= fundflow_col, ascending= False).reset_index(drop= True)

    symbols = df.symbol.tolist()
    all_symbol_name = get_all_symbol_name()

    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['SimHei'], # Chinese font
        'axes.unicode_minus': False,
        'axes.titlesize': 'medium', # large, medium, small
    })

    market = Market(start= date_from_str('3 month ago'), end=date_from_str('today'), adjust='qfq')
    market.watch( symbols )
    market.update_daily_realtime()

    figsize = (18, 9)
    cols = 10
    rows = len(symbols) // cols + 1
    axs = plt.figure(figsize=figsize, constrained_layout=True).subplots(rows, cols)
    axs = trim_axs(axs, len(symbols))
    for ax, symbol in zip(axs, symbols):
        ax.set_title(symbol + ' - ' + all_symbol_name[symbol])

        df = market.get_daily(symbol, count=30)
        df.index = df.index.strftime('%Y-%m%d')

        fundflow = df[ fundflow_col ]
        color = ['r' if v >= 0 else 'g' for v in fundflow]
        ax.bar(fundflow.index, fundflow, color=color)

        price = df['close']
        max_price, min_price = max(price), min(price)
        max_y, min_y = max(fundflow), min(fundflow)
        price_trend = (price - min_price) / (max_price - min_price) * (max_y - min_y) + min_y
        ax.plot(price_trend.index, price_trend, color='black', linewidth=0.6)

        ax.set_xticks([])

    plt.show()

def cli_fundflow(params, options):
    syntax_tips = '''Syntax:
    __argv0__ fundflow <action> <symbols | symbols.csv>

Actioin:
    rank ............................. rank the main fund flow
    view ............................. view & plot history fund flow of symbols

Options:
    -pct ............................. plot main fundflow percertage data
    -fund ............................ by default, plot main fundflow fund data
    -1d, -3d, -5d, -10d .............. rank by fund flow of the days

Example:
    __argv0__ fundflow 600036 000002 600276
    __argv0__ fundflow stockpool/realtime_trade.csv -pct

'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    action = params[0]
    params = params[1:]

    if params[0].endswith('.csv'):
        stock_df = pd.read_csv(params[0], dtype=str)
        symbols = stock_df['symbol'].tolist()
    elif params[0] == 'all':
        symbols = list(get_all_symbol_name().keys())
    else:
        symbols = params

    if action == 'rank':
        cli_fundflow_rank(symbols, options)
    elif action in ['view', 'show', 'plot']:
        cli_fundflow_view(symbols, options)
    else:
        print('\nError: invalid action: ', action)
