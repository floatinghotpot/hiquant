# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
import datetime as dt
import configparser

from ..core import seconds_from_str, date_from_str
from ..core import Market, Trader, Fund

def get_fund_conf_template():
    return '''
[main]
tick_period = 5 min
compare_index = sh000300

[fund_list]
1 = fund_1

[fund_1]
name = My Fun No.1
start_cash = 1000000.00
agent = agent_1
strategy = strategy/mystrategy.py

[agent_1]
agent_type = human
account = account_1
portfolio_load = data/{account}_portfolio_load.csv
portfolio_save = data/{account}_portfolio_save.csv
order = data/{account}_order.csv
push_to = email_1

[email_1]
push_type = email
mailto = your_name@gmail.com
sender = no-reply@gmail.com
server = 192.168.0.200
user = 
passwd =
'''

def cli_fund_create(params, options):
    template_content = get_fund_conf_template()

    file_to_create = params[0]
    fp = open(file_to_create, 'w')
    fp.write(template_content)
    fp.close()

    print('-' * 80)
    print( template_content )
    print('-' * 80)

    print( 'Fund configuration file created:\n  ', os.path.abspath(file_to_create))
    print( '\nPlease edit file content before running.' )

def cli_run_fund(config_file, start, end, options):
    # read config file
    print( 'reading config from from:', config_file)
    if not os.path.isfile(config_file):
        print('Error:', config_file, 'not eixsts\n')
        exit()

    global_config = configparser.ConfigParser()
    global_config.read(config_file, encoding='utf-8')

    print('-' * 80)
    main_conf = {}
    print('[main]')
    for k, v in global_config.items('main'):
      main_conf[ k ] = v
      print(k, '=', v)

    fund_list_conf = {}
    print('[fund]')
    for k, v in global_config.items('fund_list'):
      fund_list_conf[ k ] = v
      print(k, '=', v)
    print('-' * 80)

    date_start = date_from_str( start )
    date_end = date_from_str( end )

    start_tick = dt.datetime.now()

    # market is a global singleton
    market = Market(date_start - dt.timedelta(days=90), date_end)
    market.verbose = '-v' in options

    trader = Trader(global_config, market)
    trader.verbose = '-v' in options

    for k, fund_id in fund_list_conf.items():
        fund = Fund(global_config, market, trader, fund_id)
        # Fund.set_agent()
        # Fund.add_strategy()

        fund.verbose = '-v' in options
        trader.add_fund(fund)

    tick_period = seconds_from_str( main_conf['tick_period'] ) if ('tick_period' in main_conf) else 60
    trader.run_fund(date_start, date_end, tick_period = tick_period)

    trader.print_report()

    end_tick = dt.datetime.now()
    print('time used:', (end_tick - start_tick))

    # compare with an index
    compare_index = main_conf['compare_index'] if ('compare_index' in main_conf) else None
    trader.plot(compare_index= compare_index)

    print('Done.\n')

def cli_fund_backtrade(params, options):
    config_file = params[0]
    start = params[1] if len(params) > 1 else '3 years ago'
    end = params[2] if len(params) > 2 else 'yesterday'
    if '-q' in options:
        start = '3 months ago'
        end = '1 week ago'
    cli_run_fund(config_file, start, end, options)

def cli_fund_run(params, options):
    config_file = params[0]
    cli_run_fund(config_file, 'today', 'future', options)

def cli_fund(params, options):
    syntax_tips = '''Syntax:
    __argv0__ fund <action> <my-fund.conf> [options]

<my-fund.conf> ............ config file for one or multiple funds
<action> .................. actions to create, backtrade, or run realtime
    create ................ create a config file from template
    backtrade ............. backtrade test during a past date period
    run ................... run realtime from today to future

Example:
    __argv0__ fund create myfund.conf
    __argv0__ fund backtrade myfund.conf 20180101 20210101
    __argv0__ fund run myfund.conf
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    if (len(params) == 0) or (params[0] == 'help'):
        print( syntax_tips )
        return

    action = params[0]
    params = params[1:]

    fund_tools = {
        'create': cli_fund_create,
        'backtrade': cli_fund_backtrade,
        'run': cli_fund_run,
    }
    if action in fund_tools.keys():
        if (len(params) == 0) or (not (params[0].endswith('.conf'))):
            print('\nError: A config file ending with .conf is expected.\n')
            return
        func = fund_tools[ action ]
        func(params, options)
    else:
        print('\nError: unknown action:', action)
        print( syntax_tips )
