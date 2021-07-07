# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
import datetime as dt
import configparser
import multiprocessing as mp

from ..utils import datetime_today, dict_from_config_items, seconds_from_str, date_from_str
from ..core import get_order_cost
from ..core import Market, Trader, Fund, EmailPush, SimulatedAgent, HumanAgent

def get_fund_conf_template():
    return '''
[main]
tick_period = 5 min
compare_index = ^GSPC

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
    verbose = '-d' in options

    # read config file
    print( 'reading config from from:', config_file)
    if not os.path.isfile(config_file):
        print('Error:', config_file, 'not eixsts\n')
        exit()

    global_config = configparser.ConfigParser()
    global_config.read(config_file, encoding='utf-8')

    main_conf = dict_from_config_items(global_config.items('main'), verbose= verbose)

    date_start = date_from_str( start )
    date_end = date_from_str( end )

    start_tick = dt.datetime.now()

    # market is a global singleton
    market = Market(date_start - dt.timedelta(days=90), date_end)
    trader = Trader(market)

    for k, fund_id in global_config.items('fund_list'):
        fund_conf = dict_from_config_items(global_config.items(fund_id), verbose= verbose)
        fund = Fund(market, trader, fund_conf)

        agent = None
        if (date_end > datetime_today()) and ('agent' in fund_conf):
            agent_conf = dict_from_config_items(global_config.items(fund_conf['agent']))
            agent_type = agent_conf['agent_type']
            if agent_type == 'human':
                agent = HumanAgent(market, agent_conf)
            #elif agent_type == 'automated':
            #    agent = AutomatedAgent(market, agent_conf)
            else:
                agent = SimulatedAgent(market, agent_conf)

            if (agent is not None) and ('push_to' in agent_conf):
                push_list = agent_conf['push_to'].replace(' ','').split(',')
                for push_to in push_list:
                    push_conf = dict_from_config_items(global_config.items(push_to))
                    push_type = push_conf['push_type']
                    if push_type == 'email':
                        agent.add_push_service(EmailPush(push_conf))

        if agent is None:
            agent = SimulatedAgent(market, None)
        fund.set_agent( agent, get_order_cost(global_config) )

        trader.add_fund(fund)

    market.set_verbose( verbose )
    trader.set_verbose( verbose )

    tick_period = seconds_from_str( main_conf['tick_period'] ) if ('tick_period' in main_conf) else 60
    trader.run_fund(date_start, date_end, tick_period = tick_period)

    trader.print_report()

    end_tick = dt.datetime.now()
    print('time used:', (end_tick - start_tick))

    out_file = None
    for option in options:
        if option.startswith('-out=') and option.endswith('.png'):
            out_file = option.replace('-out=', '')

    # compare with an index
    compare_index = main_conf['compare_index'] if ('compare_index' in main_conf) else None
    trader.plot(compare_index= compare_index, out_file= out_file)

    print('Done.\n')

# this func is prepared for multiprocessing
def cli_one_trader_run_one_fund(args):
    global_config, fund_id, date_start, date_end, tick_period, verbose = args

    start_tick = dt.datetime.now()

    fund_conf = dict_from_config_items(global_config.items(fund_id), verbose= verbose)

    market = Market(date_start, date_end)
    trader = Trader(market)
    fund = Fund(market, trader, fund_conf)

    agent = None
    if (date_end > datetime_today()) and ('agent' in fund_conf):
        agent_conf = dict_from_config_items(global_config.items(fund_conf['agent']))
        agent_type = agent_conf['agent_type']
        if agent_type == 'human':
            agent = HumanAgent(market, agent_conf)
        #elif agent_type == 'automated':
        #    agent = AutomatedAgent(market, agent_conf)
        else:
            agent = SimulatedAgent(market, agent_conf)

        if (agent is not None) and ('push_to' in agent_conf):
            push_list = agent_conf['push_to'].replace(' ','').split(',')
            for push_to in push_list:
                push_conf = dict_from_config_items(global_config.items(push_to))
                push_type = push_conf['push_type']
                if push_type == 'email':
                    agent.add_push_service(EmailPush(push_conf))

    if agent is None:
        agent = SimulatedAgent(market, None)

    fund.set_agent( agent, get_order_cost(global_config) )

    trader.add_fund(fund)

    market.set_verbose( verbose )
    trader.set_verbose( verbose )

    trader.run_fund(date_start, date_end, tick_period = tick_period)

    end_tick = dt.datetime.now()
    print(fund_id, 'time used:', (end_tick - start_tick))

    return trader.get_report()

def cli_run_fund_multiprocessing(config_file, start, end, options):
    verbose = '-d' in options

    # read config file
    print( 'reading config from from:', config_file)
    if not os.path.isfile(config_file):
        print('Error:', config_file, 'not eixsts\n')
        exit()

    global_config = configparser.ConfigParser()
    global_config.read(config_file, encoding='utf-8')

    main_conf = dict_from_config_items(global_config.items('main'), verbose= verbose)
    tick_period = seconds_from_str( main_conf['tick_period'] ) if ('tick_period' in main_conf) else 60
    compare_index = main_conf['compare_index'] if ('compare_index' in main_conf) else None

    date_start = date_from_str( start )
    date_end = date_from_str( end )

    start_tick = dt.datetime.now()
    fund_id_list = [fund_id for k, fund_id in global_config.items('fund_list')]
    fund_args = [[global_config, fund_id, date_start, date_end, tick_period, verbose] for fund_id in fund_id_list]
    with mp.Pool( len(fund_id_list) ) as p:
        report_list = p.map(cli_one_trader_run_one_fund, fund_args)
    end_tick = dt.datetime.now()
    print('Total time used:', (end_tick - start_tick))

    all_report = []
    for report in report_list:
        all_report += report

    out_file = None
    for option in options:
        if option.startswith('-out=') and option.endswith('.png'):
            out_file = option.replace('-out=', '')

    trader = Trader(Market(date_start, date_end))
    trader.print_report(all_report)
    trader.plot(report = all_report, compare_index= compare_index, out_file= out_file)

    print('Done.\n')

def cli_fund_backtrade(params, options):
    config_file = params[0]
    start = params[1] if len(params) > 1 else '3 years ago'
    end = params[2] if len(params) > 2 else 'yesterday'
    if '-q' in options:
        start = '3 months ago'
        end = '1 week ago'
    if '-m' in options:
        cli_run_fund_multiprocessing(config_file, start, end, options)
    else:
        cli_run_fund(config_file, start, end, options)

def cli_fund_run(params, options):
    config_file = params[0]
    cli_run_fund(config_file, 'today', 'future', options)

def cli_fund(params, options):
    syntax_tips = '''Syntax:
    __argv0__ fund <action> <my-fund.conf> [options]

<my-fund.conf> ............ config file for one or multiple funds

<action>
    create ................ create a config file from template
    backtrade ............. backtrade test during a past date period
    run ................... run realtime from today to future

<options>
    -m .................... use multi-processing to boost backtrade
    -q .................... run a shorter backtrade

Example:
    __argv0__ fund create etc/myfund.conf
    __argv0__ fund backtrade etc/myfund.conf 20180101 20210101
    __argv0__ fund run etc/myfund.conf

Alias:
    __argv0__ backtrade etc/myfund.conf 20180101 20210101
    __argv0__ run etc/myfund.conf
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
