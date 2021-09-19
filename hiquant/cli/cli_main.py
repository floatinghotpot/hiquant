#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
import os
sys.path.append(os.getcwd())
sys.path.append(os.getcwd()+'/strategy')

import configparser

from ..version import __version__
from ..utils import parse_params_options, dict_from_config_items
from ..core import set_lang, get_hiquant_conf

from .cli_init import cli_init
from .cli_finance import cli_finance
from .cli_pepb import cli_pepb
from .cli_stockpool import cli_stockpool
from .cli_strategy import cli_strategy
from .cli_trade import cli_trade
from .cli_fund import cli_fund
from .cli_stock import cli_stock
from .cli_index import cli_index
from .cli_indicator import cli_indicator
from .cli_fundflow import cli_fundflow

def cli_main_help():
    syntax_tips = '''Syntax:
    __argv0__ <command>
    __argv0__ <module> <action> [options]

Global Commands:
    help ................... Get help for a command
    init ................. init a hiquant project

Modules:
    finance ................ Finance analysis on stock pool
    pepb ................... PE/PE analysis on stock pool
    stockpool .............. Create or edit stock pool .csv file
    strategy ............... Create or bench a strategy

    stock .................. Plot a stock with indicators
    index .................. Plot index with indicators
    fund ................... List or plot open funds
    indicator .............. List indicators
    fundflow ............... View main fundflow of stocks

Options:
    -v, --version .......... print out the version
    -d, --verbose .......... debug mode produces verbose log output

Example:
    __argv0__ init myFund
    cd myFund

    __argv0__ stock list us
    __argv0__ index list world

    __argv0__ stockpool create stockpool/mystocks.csv 600036 000002 600276 300357

    __argv0__ stock plot AAPL -macd
    __argv0__ stock plot AAPL -ma -macd -kdj

    __argv0__ fund list
    __argv0__ fund plot 005669 000209

    __argv0__ strategy create strategy/mystrategy.py
    ... modify my_strategy.py ...
    __argv0__ backtest strategy/mystrategy.py

    __argv0__ trade create etc/myfund.conf
    ... modify my_fund.conf ...
    __argv0__ backtrade etc/myfund.conf
    __argv0__ run etc/myfund.conf
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    print(syntax_tips)

def cli_main_params_options(params, options):
    # parse command line arguments
    cli_tools = {
        'init': cli_init,
        'finance': cli_finance,
        'pepb': cli_pepb,
        'stockpool': cli_stockpool,
        'strategy': cli_strategy,
        'trade': cli_trade,
        'fund': cli_fund,
        'stock': cli_stock,
        'index': cli_index,
        'indicator': cli_indicator,
        'fundflow': cli_fundflow,
    }

    if ('-v' in options) or ('--version' in options):
        print( __version__ )
        return

    if len(params) == 0:
        cli_main_help()
        return

    config = get_hiquant_conf()
    main_conf = dict_from_config_items(config.items('main'))
    if 'lang' in main_conf:
        set_lang(main_conf['lang'])
    else:
        lang = os.getenv('LANG')
        if lang is not None:
            set_lang(lang[:2])

    command = params[0]

    if command == 'help':
        if (len(params) > 1) and (params[1] in cli_tools):
                func = cli_tools[ params[1] ]
                func(['help'], options)
        elif (len(params) > 1) and (params[1] in ['backtest']):
                cli_strategy(['help'], options)
        elif (len(params) > 1) and (params[1] in ['backtrade', 'run']):
                cli_trade(['help'], options)
        else:
            cli_main_help()

    elif command == 'backtest':
        cli_strategy(params, options)

    elif command in ['backtrade', 'run']:
        cli_trade(params, options)

    elif command in cli_tools:
        func = cli_tools[ command ]
        func(params[1:], options)
    else:
        cli_main_help()

def cli_main():
    params, options = parse_params_options(sys.argv)
    cli_main_params_options(params, options)

if __name__ == "__main__":
    cli_main()
