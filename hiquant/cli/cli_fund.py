# -*- coding: utf-8; py-indent-offset:4 -*-

import os, sys
import datetime as dt
import tabulate as tb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ..core import get_cn_fund_list, get_cn_fund_daily, get_cn_fund_manager
from ..utils import date_from_str, dict_from_df, datetime_today, sort_with_options, filter_with_options

def cli_fund_help():
    syntax_tips = '''Syntax:
    __argv0__ fund list [<keyword>]
    __argv0__ fund update <all | symbols | symbols.csv>
    __argv0__ fund eval <all | symbols | symbols.csv> [-sortby=...] [-desc] [-filter_column=...-...]
    __argv0__ fund plot <symbols | symbols.csv> [<options>]

Options:
    -sortby=<col> .................. sort by the column
    -sharpe=2.5- ................... sharpe value between <from> to <to>
    -max_drawdown=-20 .............. max_drawdown between <from> to <to>
    -volatility=-20 ................ volatility between <from> to <to>
    -out=file.csv .................. export fund list to .csv file
    -out=file.xlsx ................. export fund data to .xlsx file

Example:
    __argv0__ fund list 多因子
    __argv0__ fund list 广发 -out=output/guangfa_funds.csv
    __argv0__ fund update data/myfunds.csv
    __argv0__ fund eval data/myfunds.csv -days=365 -sortby=sharpe -desc -limit=20 -out=output/top20_funds.xlsx
    __argv0__ fund plot 002943 005669 000209 -days=365
    __argv0__ fund plot data/funds.csv -days=365
    __argv0__ fund plot data/funds.csv -days=1095 -mix
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    print( syntax_tips )

def date_limit_from_options(options):
    limit = 0
    date_from = None
    date_to = None
    days = None
    for option in options:
        if option.startswith('-days='):
            days = int(option.replace('-days=',''))
            date_from = date_from_str('{} days ago'.format(days))
            date_to = datetime_today()
        if option.startswith('-date='):
            date_range = option.replace('-date=','').split('-')
            date_from = date_from_str(date_range[0])
            date_to = date_from_str(date_range[1]) if len(date_range[1])>0 else datetime_today()
        if option.startswith('-limit='):
            limit = int(option.replace('-limit=',''))

    if date_from is None:
        days = 365 * 1
        date_from = date_from_str('{} days ago'.format(days))
        date_to = datetime_today()

    return date_from, date_to, limit

def csv_xlsx_from_options(options):
    csv = ''
    xlsx = ''
    for k in options:
        if k.startswith('-out='):
            if k.endswith('.csv'):
                csv = k.replace('-out=', '')
            if k.endswith('.xlsx'):
                xlsx = k.replace('-out=', '')
    return csv, xlsx

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

    out_csv_file, out_xls_file = csv_xlsx_from_options(options)

    if out_csv_file:
        df = df[['symbol', 'name']]
        df.to_csv(out_csv_file, index= False)
        print('Exported to:', out_csv_file)
        print(df)

def cli_fund_manager(params, options):
    df = get_cn_fund_manager(check_date= datetime_today())
    selected = total = df.shape[0]
    if len(params) > 0:
        df = df[ df['name'].str.contains(params[0], na=False) ]
    for option in options:
        if option.startswith('-fund='):
            fund = option.replace('-fund=','')
            df = df[ df['fund'].str.contains(fund, na=False) ]
    selected = df.shape[0]
    print( tb.tabulate(df, headers='keys') )
    print( selected, 'of', total, 'funds selected.')

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

def eval_fund_list(df_fund_list, date_from, date_to):
    days = (date_to - date_from).days
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
        if fund_start > date_from:
            continue

        df = df[ df.index >= date_from ]
        df = df[ df.index < date_to ]

        try:
            df['pct_cum'] = (df['pct_change'] * 0.01 +1).cumprod()
            pct_cum = df['pct_cum'].iloc[-1] - 1.0
            pct_cum = round(pct_cum * 100, 2)
        except (KeyError, ValueError, IndexError) as err:
            #print('error calculating', param, name, ', skip.')
            continue

        risk_free_rate = 3.0 / 365
        daily_sharpe_ratio = (df['pct_change'].mean() - risk_free_rate) / df['pct_change'].std()
        sharpe_ratio = round(daily_sharpe_ratio * (252 ** 0.5), 2)

        max_drawdown = (1 - df['pct_cum'] / df['pct_cum'].cummax()).max()
        max_drawdown = round(100 * max_drawdown, 2)

        logreturns = np.diff( np.log(df['pct_cum']) )
        volatility = np.std(logreturns)
        annualVolatility = volatility * (252 ** 0.5)
        annualVolatility = round(annualVolatility * 100, 2)
        eval_table.append([param, name, days, pct_cum, sharpe_ratio, max_drawdown, annualVolatility, buy_state, sell_state, fee, fund_start, round(fund_days/365.0,1)])

    en_cols = ['symbol', 'name', 'calc_days', 'pct_cum', 'sharpe', 'max_drawdown', 'volatility', 'buy_state', 'sell_state', 'fee', 'fund_start', 'fund_years']
    df = pd.DataFrame(eval_table, columns=en_cols)
    df['fund_start'] = df['fund_start'].dt.strftime('%Y-%m-%d')
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

    date_from, date_to, limit = date_limit_from_options(options)

    df_eval = eval_fund_list(df_fund_list, date_from= date_from, date_to= date_to)

    df_eval = df_eval[ df_eval['buy_state'].isin(['限大额','开放申购']) ]
    df_eval = filter_with_options(df_eval, options)
    df_eval = sort_with_options(df_eval, options, by_default='sharpe')
    if limit > 0:
        df_eval = df_eval.head(limit)

    print('\r', end= '', flush= True)
    print( tb.tabulate(df_eval, headers='keys') )

    out_csv_file, out_xls_file = csv_xlsx_from_options(options)

    if out_csv_file:
        df = df_eval[['symbol', 'name']]
        df.to_csv(out_csv_file, index= False)
        print('Exported to:', out_csv_file)
        print(df)

    if out_xls_file:
        df_eval.columns = ['基金代码', '基金简称', '计算天数', '累计收益率', '夏普比率', '最大回撤', '波动率', '申购状态', '赎回状态', '手续费', '起始日期', '基金年数']
        df_eval.to_excel(excel_writer= out_xls_file)
        print('Exported to:', out_xls_file)

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

    date_from, date_to, limit = date_limit_from_options(options)
    if limit == 0:
        limit = 100

    df_funds = None
    i = 0
    for param in params:
        i += 1
        if i > limit:
            break

        if param in fund_symbol_names:
            name = param + ' - ' + fund_symbol_names[ param ]
        else:
            name = param
        print( name )

        df = get_cn_fund_daily(symbol= param)
        df = df[ df.index >= date_from ]
        df = df[ df.index < date_to ]
        df['pct_cum'] = round(((df['pct_change'] * 0.01 +1).cumprod() - 1.0) * 100.0, 1)
        if df_funds is None:
            df_funds = df[['pct_cum']]
            df_funds.columns = [ name ]
        else:
            df_funds[ name ] = df['pct_cum']
        #print(df)

    print(df_funds)

    df_funds.index = df_funds.index.strftime('%Y-%m-%d')
    if '-mix' in options:
        n = df_funds.shape[1]
        df_funds = df_funds.fillna(0)
        df = df_funds.copy() / n
        df['portfolio'] = 0.0
        for col in df_funds.columns:
            df['portfolio'] += df[col]
        df[['portfolio']].plot(kind='line', ylabel='return (%)', figsize=(10,6))
    else:
        df_funds.plot(kind='line', ylabel='return (%)', figsize=(10,6))
    plt.show()

    pass

def cli_fund_backtest(params, options):
    if len(params) == 0:
        cli_fund_help()
        return

    date_from, date_to, limit = date_limit_from_options(options)
    if limit == 0:
        limit = 20

    period = 90
    for option in options:
        if option.startswith('-period='):
            period = int(option.replace('-period=', ''))

    df_fund_list = get_cn_fund_list()
    if params[0] == 'all':
        pass
    elif params[0].endswith('.csv'):
        params = cli_fund_read_fund_symbols(params[0])
        df_fund_list = df_fund_list[ df_fund_list['symbol'].isin(params) ]
    else:
        df_fund_list = df_fund_list[ df_fund_list['symbol'].isin(params) ]

    returns = []
    d = date_from
    while d < date_to:
        print('-'*20, d, '-'*20)
        df_eval = eval_fund_list(df_fund_list, (d - dt.timedelta(days= period)), d)
        df_eval = filter_with_options(df_eval, ['-pct_cum=3.0-'])
        #df_eval = sort_with_options(df_eval, ['-sortby=sharpe','-desc'], by_default='sharpe').head(limit)
        df_eval = sort_with_options(df_eval, ['-sortby=sharpe','-desc'], by_default='sharpe').head(100)
        df_eval = sort_with_options(df_eval, ['-sortby=pct_cum','-desc'], by_default='sharpe').head(limit)
        print('\r', end= '', flush= True)
        print( tb.tabulate(df_eval, headers='keys') )

        d2 = min(d + dt.timedelta(days= period), date_to)
        n = df_eval.shape[0]
        period_pct_change = 0
        for i, row in df_eval.iterrows():
            symbol = row['symbol']
            df = get_cn_fund_daily(symbol)
            df = df[ df.index >= d ]
            df = df[ df.index < d2 ]
            if df.shape[0] < 1:
                continue
            df['pct_cum'] = ((df['pct_change'] * 0.01 +1).cumprod() - 1.0) * 100.0
            period_pct_change += df['pct_cum'].iloc[-1] / n

        period_pct_change -= 0.15 + 0.5 + 1.75 / 365 * period
        print(d, d2, 'return =', period_pct_change)
        returns.append([d, d2, period_pct_change])

        d += dt.timedelta(days= period)
        pass

    df_returns = pd.DataFrame(returns, columns=['date1', 'date2', 'pct_change'])
    df_returns.index = df_returns['date2']
    df_returns['pct_cum'] = ((df_returns['pct_change'] * 0.01 +1).cumprod() - 1.0) * 100.0

    print(df_returns)
    df_returns[['pct_cum']].plot(kind='line', ylabel='return (%)', figsize=(10,6))
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

    if action == 'manager':
        cli_fund_manager(params, options)

    elif action == 'update':
        cli_fund_update(params, options)

    elif action in ['eval']:
        cli_fund_eval(params, options)

    elif action in ['backtest']:
        cli_fund_backtest(params, options)

    elif action in ['plot', 'show']:
        cli_fund_plot(params, options)

    else:
        print('invalid action:', action)
        cli_fund_help()
