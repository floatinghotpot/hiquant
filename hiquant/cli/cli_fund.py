# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
import tabulate as tb
import mplfinance as mpf
import matplotlib.pyplot as plt
from cycler import cycler

from ..core import get_cn_fund_list, get_cn_fund_daily

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

def cli_fund_list(params, options):
    df = get_cn_fund_list()
    selected = total = df.shape[0]
    if len(params) > 0:
        df = df[ df['基金简称'].str.contains(params[0], na=False) ]
        selected = df.shape[0]
    print( tb.tabulate(df, headers='keys') )
    print( selected, 'of', total, 'funds selected.')

def cli_fund_plot(params, options):
    if len(params) == 0:
        cli_fund_help()
        return

    df = get_cn_fund_daily(symbol= params[0])
    print(df)
    pass

def cli_fund(params, options):
    if (len(params) == 0) or (params[0] == 'help'):
        cli_fund_help()
        return

    action = params[0]
    params = params[1:]

    if action == 'list':
        cli_fund_list(params, options)

    elif action in ['plot', 'view', 'show']:
        cli_fund_plot(params, options)

    else:
        print('invalid action:', action)
        cli_fund_help()
