#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
import os
sys.path.append(os.getcwd())

from ..core import parse_params_options
from ..version import __version__

from .cli_create import cli_create
from .cli_finance import cli_finance
from .cli_pepb import cli_pepb
from .cli_stockpool import cli_stockpool
from .cli_strategy import cli_strategy
from .cli_fund import cli_fund

from .cli_stock import cli_stock
from .cli_index import cli_index
from .cli_pattern import cli_pattern
from .cli_indicator import cli_indicator

def cli_main():
    # parse command line arguments
    syntax_tips = '''Syntax:
    __argv0__ <command> [options]

Global Commands:
    help ................... Get help for a command
    create ................. Create a hiquant project

Project Commands:
    list ................... List stock, index, indicator, pattern, strategy

    finance ................ Finance analysis on stock pool
    pepb ................... PE/PE analysis on stock pool
    symbol ................. Create or edit symbol list .csv file
    strategy ............... Create or bench a strategy
    fund ................... Back trade or run real-time one or multiple funds

    stock .................. Plot a stock with indicators
    index .................. Plot index with indicators
    pattern ................ Draw K-line patterns
    indicator .............. List indicators

Options:
    -v, --version .......... print out the version
    -d, --verbose .......... debug mode produces verbose log output

Example:
    __argv0__ create myFund
    cd myFund

    __argv0__ list stock
    __argv0__ list index

    __argv0__ stockpool create my_stocks.csv 600036 000002 600276 300357
    __argv0__ finance view my_stocks.csv
    __argv0__ pepb view my_stocks.csv

    __argv0__ stock 600036 -ma -macd -kdj

    __argv0__ strategy create my_strategy.py
    ... modify my_strategy.py ...

    __argv0__ fund create my_fund.conf my_strategy.py
    ... modify my_fund.conf ...

    __argv0__ fund backtrade my_fund.conf

    __argv0__ fund run my_fund.conf
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    cli_tools = {
        'create': cli_create,
        'finance': cli_finance,
        'pepb': cli_pepb,
        'stockpool': cli_stockpool,
        'strategy': cli_strategy,
        'fund': cli_fund,
        'stock': cli_stock,
        'index': cli_index,
        'indicator': cli_indicator,
        'pattern': cli_pattern,
    }

    params, options = parse_params_options(sys.argv)
    if ('-v' in options) or ('--version' in options):
        print( __version__ )
        return

    if len(params) == 0:
        print( syntax_tips )
        return

    command, params = params[0], params[1:]

    if command == 'help':
        if (len(params) > 0) and (params[0] in cli_tools):
                func = cli_tools[ params[0] ]
                func(['help'], options)
        else:
            print( syntax_tips )

    elif command == 'list':
        tools_with_list = ['stock', 'index', 'indicator', 'pattern', 'strategy']
        if (len(params) > 0) and (params[0] in tools_with_list):
            func = cli_tools[ params[0] ]
            func(['list'], options)
        else:
            print('''Syntax:
    __argv0__ list [stock | index | indicator | pattern | strategy]
'''.replace('__argv0__',os.path.basename(sys.argv[0])))

    elif command in cli_tools:
        func = cli_tools[ command ]
        func(params, options)
    else:
        print( syntax_tips )

    print('')

if __name__ == "__main__":
    cli_main()
