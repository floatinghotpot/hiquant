# -*- coding: utf-8; py-indent-offset:4 -*-

import os, sys
import datetime as dt
import tabulate as tb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ..core import get_cn_fund_list, get_cn_fund_daily, get_cn_fund_manager, get_cn_index_list_df, get_index_daily
from ..utils import dict_from_df, datetime_today, sort_with_options, filter_with_options, date_limit_from_options, csv_xlsx_from_options

def cli_fund_help():
    syntax_tips = '''Syntax:
    __argv0__ fund update <all | symbols | symbols.csv>
    __argv0__ fund list [<keyword>] [-sortby=...] [-desc] [-filter_column=...-...]
    __argv0__ fund manager [<keyword>] [-s | -d] [-sortby=...] [-desc] [-filter_column=...-...]
    __argv0__ fund company [<keyword>]
    __argv0__ fund eval <all | symbols | symbols.csv> [-sortby=...] [-desc] [-filter_column=...-...]
    __argv0__ fund plot <symbols | symbols.csv> [<options>]
    __argv0__ fund backtest  <all | symbols | symbols.csv> [-period=90] [-days=...] [-date=yyyymmdd-yyyymmdd]

Options:
    -sortby=<col> .................. sort by the column
    -sharpe=2.5- ................... sharpe value between <from> to <to>
    -max_drawdown=-20 .............. max_drawdown between <from> to <to>
    -volatility=-20 ................ volatility between <from> to <to>
    -out=file.csv .................. export fund list to .csv file
    -out=file.xlsx ................. export fund data to .xlsx file

    -s ............................. display symbol of the funds managed
    -d ............................. display symbol and name of the funds managed

Example:
    __argv0__ fund list 多因子
    __argv0__ fund list 广发 -out=output/myfunds.csv
    __argv0__ fund company 华安
    __argv0__ fund update data/myfunds.csv
    __argv0__ fund eval all -days=365 -sortby=sharpe -desc -limit=20 -out=output/top20_funds.xlsx
    __argv0__ fund plot 002943 005669 000209 -days=365
    __argv0__ fund plot data/funds.csv -days=365
    __argv0__ fund plot data/funds.csv -days=1095 -mix
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    print( syntax_tips )

def get_fund_symbol_name():
    df = get_cn_fund_list(check_date= datetime_today())
    return dict_from_df(df, 'symbol', 'name')

def get_fund_name_symbol():
    df = get_cn_fund_list(check_date= datetime_today())
    return dict_from_df(df, 'name', 'symbol')

def get_fund_manager_mapping():
    df = get_cn_fund_manager(check_date= datetime_today())
    fund_manager = {}
    for i, row in df.iterrows():
        name = row['name']
        fund = row['fund']
        if fund in fund_manager:
            fund_manager[ fund ].append( name )
            pass
        else:
            fund_manager[ fund ] = [ name ]
    return fund_manager

def get_manager_fundname_mapping():
    df = get_cn_fund_manager(check_date= datetime_today())
    manager_fund = {}
    for i, row in df.iterrows():
        name = row['company'] + ' ' + row['name']
        fund = row['fund']
        if name in manager_fund:
            manager_fund[ name ].append( fund )
        else:
            manager_fund[ name ] = [ fund ]
    return manager_fund

def get_manager_fundsymbol_mapping():
    fund_symbol = dict_from_df(get_cn_fund_list(check_date= datetime_today()), 'name', 'symbol')
    df = get_cn_fund_manager(check_date= datetime_today())
    manager_fund = {}
    for i, row in df.iterrows():
        name = row['company'] + ' ' + row['name']
        fund = row['fund']
        symbol = fund_symbol[fund] if (fund in fund_symbol) else ''
        if symbol == '':
            continue
        if name in manager_fund:
            manager_fund[ name ].append( symbol )
        else:
            manager_fund[ name ] = [ symbol ]
    return manager_fund

def get_manager_fund_mapping():
    fund_symbol = dict_from_df(get_cn_fund_list(check_date= datetime_today()), 'name', 'symbol')
    df = get_cn_fund_manager(check_date= datetime_today())
    manager_fund = {}
    for i, row in df.iterrows():
        name = row['company'] + ' ' + row['name']
        fund = row['fund']
        symbol = fund_symbol[fund] if (fund in fund_symbol) else ''
        if symbol == '':
            continue
        if name in manager_fund:
            manager_fund[ name ].append( symbol + ' - ' + fund )
        else:
            manager_fund[ name ] = [ symbol + ' - ' + fund ]
    return manager_fund

# hiquant fund list
# hiquant fund list 多因子
def cli_fund_list(params, options):
    df = get_cn_fund_list(check_date= datetime_today())
    selected = total = df.shape[0]
    if len(params) > 0:
        df = df[ df['name'].str.contains(params[0], na=False) ]
        selected = df.shape[0]

    df = filter_with_options(df, options)
    df = sort_with_options(df, options, by_default='symbol')

    limit = 0
    for option in options:
        if option.startswith('-limit='):
            limit = int(option.replace('-limit=',''))
    if limit > 0:
        df = df.head(limit)

    print( tb.tabulate(df, headers='keys') )
    print( selected, 'of', total, 'funds selected.')

    out_csv_file, out_xls_file = csv_xlsx_from_options(options)

    if out_csv_file:
        df = df[['symbol', 'name']]
        df.to_csv(out_csv_file, index= False)
        print('Exported to:', out_csv_file)
        print(df)

def get_cn_fund_company(keyword = None):
    df = get_cn_fund_manager(check_date= datetime_today())
    if keyword is not None:
        df = df[ df['company'].str.contains(keyword, na=False) ]

    mapping = {}
    for i, row in df.iterrows():
        fund = row['fund']
        manager = row['name']
        company = row['company']
        if company in mapping:
            funds = mapping[ company ]['funds']
            managers = mapping[ company ]['managers']
            if fund not in funds:
                funds.append( fund )
            if manager not in managers:
                managers.append( manager )
        else:
            mapping[ company ] = {
                'funds': [ fund ],
                'managers': [ manager ],
            }
    table = []
    for company, v in mapping.items():
        funds = v['funds']
        managers = v['managers']
        table.append( [company, len(managers), len(funds)] )
    return pd.DataFrame(table, columns=['company','managers','funds']).sort_values(by= 'funds', ascending= False).reset_index(drop= True)

def cli_fund_company(params, options):
    keyword = params[0] if len(params) > 0 else None
    df = get_cn_fund_company(keyword)

    selected = total = df.shape[0]
    df = filter_with_options(df, options)
    limit = 0
    for k in options:
        if k.startswith('-limit='):
            limit = int(k.replace('-limit=',''))
        if k.startswith('-sortby='):
            df = sort_with_options(df, options, by_default='managers')
    if limit > 0:
        df = df.head(limit)

    selected = df.shape[0]
    print( tb.tabulate(df, headers='keys') )
    print( selected, 'of', total, 'fund companies.')

    out_csv_file, out_xls_file = csv_xlsx_from_options(options)
    if out_xls_file:
        df = df.rename(columns= {
            'company': '基金公司',
            'managers': '基金经理人数',
            'funds': '基金总数',
        })
        df.to_excel(excel_writer= out_xls_file)
        print('Exported to:', out_xls_file)

def cli_fund_manager(params, options):
    df = get_cn_fund_manager(check_date= datetime_today())
    selected = total = df.shape[0]

    if len(params) > 0:
        keyword = params[0]
        if keyword.endswith('.csv'):
            df1 = df.copy()
            df1['manager'] = df['company'] + ' ' + df['name']
            df_manager = pd.read_csv(keyword, dtype= str)
            df_manager['manager'] = df_manager['company'] + ' ' + df_manager['name']
            df = df1[ df1['manager'].isin(df_manager['manager'].tolist()) ].drop(columns=['manager'])
        else:
            df1 = df.copy()
            df1['keywords'] = df1['company'] + df1['name'] + ' ' + df1['fund']
            df = df1[ df1['keywords'].str.contains(keyword, na=False) ].drop(columns=['keywords'])

    yeartop = 0
    limit = 0
    for k in options:
        if k.startswith('-limit='):
            limit = int(k.replace('-limit=',''))
        if k.startswith('-yeartop='):
            yeartop = int(k.replace('-yeartop=', ''))
        if k.startswith('-fund='):
            fund = k.replace('-fund=','')
            df = df[ df['fund'].str.contains(fund, na=False) ]

    df_company = get_cn_fund_company()
    company_managers = dict_from_df(df_company, 'company', 'managers')
    company_funds = dict_from_df(df_company, 'company', 'funds')

    group = '-d' not in options
    if group and (df.shape[0] > 0):
        df_tmp = df.drop(columns=['fund'])
        table = []
        name = ''
        for i, row in df_tmp.iterrows():
            company = row['company']
            manager = company + row['name']
            if name == manager:
                continue
            else:
                name = manager
                data = list(row.values)

                managers = company_managers[company] if (company in company_managers) else 0
                funds = company_funds[company] if (company in company_funds) else 0
                data.insert(2, managers)
                data.insert(3, funds)

                table.append( data )

        cols = list(row.keys())
        cols.insert(2, 'managers')
        cols.insert(3, 'funds')
        df = pd.DataFrame(table, columns=cols)

    df['annual'] = round((np.power((df['best_return'] * 0.01 + 1), 1.0/(df['days']/365.0)) - 1.0) * 100.0, 1)
    df['annual'] = df[['best_return', 'annual']].min(axis= 1)

    if yeartop > 0:
        df1 = df[ df['days'] >= 3650 ].sort_values(by='best_return', ascending=False).head(yeartop)
        for i in range(9,-1,-1):
            df2 = df[ (df['days'] >= (i*365)) & (df['days'] < ((i+1))*365) ].sort_values(by='best_return', ascending=False).head(yeartop)
            df1 = pd.concat([df1, df2], ignore_index=True)
        df = df1

    df.insert(5, 'years', round(df['days'] / 365.0, 1))

    selected = total = df.shape[0]
    df = filter_with_options(df, options)
    for k in options:
        if k.startswith('-sortby='):
            df = sort_with_options(df, options, by_default='best_return')
            break
    if limit > 0:
        df = df.head(limit)

    if 'fund' in df.columns:
        fund_name_symbol = get_fund_name_symbol()
        df['fund'] = [(fund_name_symbol[fund] if fund in fund_name_symbol else '') for fund in df['fund'].tolist()] + (' - ' + df['fund'])
    elif ('-s' in options) and ('name'in df.columns):
        manager_fundsymbol = get_manager_fundsymbol_mapping()
        managers = (df['company'] + ' ' + df['name']).tolist()
        df['symbol'] = [(','.join(manager_fundsymbol[manager]) if manager in manager_fundsymbol else '') for manager in managers]
    elif ('-sd' in options) and ('name'in df.columns):
        manager_fund = get_manager_fund_mapping()
        managers = (df['company'] + ' ' + df['name']).tolist()
        df['funds'] = [('\n'.join(manager_fund[manager]) if manager in manager_fund else '') for manager in managers]

    selected = df.shape[0]
    print( tb.tabulate(df, headers='keys') )
    print( selected, 'of', total, 'selected.')

    out_csv_file, out_xls_file = csv_xlsx_from_options(options)

    if out_csv_file:
        df.to_csv(out_csv_file, index= False)
        print('Exported to:', out_csv_file)

    if out_xls_file:
        if 'days' in df.columns:
            df = df.drop(columns=['days'])
        df = df.rename(columns= {
            'name': '基金经理',
            'company': '基金公司',
            'managers': '基金经理人数',
            'funds': '基金总数',
            'fund': '基金',
            'years': '管理年限',
            'size': '基金规模',
            'best_return': '最佳回报',
            'annual': '年化收益',
        })
        df.to_excel(excel_writer= out_xls_file)
        print( tb.tabulate(df, headers='keys') )
        print('Exported to:', out_xls_file)

    return df

def cli_fund_read_fund_symbols(csv_file):
    df = pd.read_csv(csv_file, dtype=str)
    return df['symbol'].tolist() if ('symbol' in df) else []

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
    elif ',' in params[0]:
        params = params[0].split(',')

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

def eval_fund_list(df_fund_list, date_from, date_to, alpha_base = None):
    fund_manager = get_fund_manager_mapping()
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
        #if fund_start > date_from:
        #    continue

        df = df[ df.index >= date_from ]
        df = df[ df.index < date_to ]

        try:
            df['pct_cum'] = (df['pct_change'] * 0.01 +1).cumprod()
            pct_cum = df['pct_cum'].iloc[-1] - 1.0
            pct_cum = round(pct_cum * 100, 2)
        except (KeyError, ValueError, IndexError) as err:
            #print('error calculating', param, name, ', skip.')
            continue

        if alpha_base is not None:
            df_base = get_index_daily( alpha_base )
            df_base = df_base[ df_base.index >= date_from ]
            df_base = df_base[ df_base.index < date_to ]
            df_base['pct_cum'] = df_base['close'] / df_base['close'].iloc[0]
            df['pct_cum'] -= df_base['pct_cum']

        risk_free_rate = 3.0 / 365
        daily_sharpe_ratio = (df['pct_change'].mean() - risk_free_rate) / df['pct_change'].std()
        sharpe_ratio = round(daily_sharpe_ratio * (252 ** 0.5), 2)

        max_drawdown = (1 - df['pct_cum'] / df['pct_cum'].cummax()).max()
        max_drawdown = round(100 * max_drawdown, 2)

        logreturns = np.diff( np.log(df['pct_cum']) )
        volatility = np.std(logreturns)
        annualVolatility = volatility * (252 ** 0.5)
        annualVolatility = round(annualVolatility * 100, 2)
        manager = ','.join(fund_manager[name]) if (name in fund_manager) else ''
        eval_table.append([param, name, manager, min(days, fund_days), pct_cum, sharpe_ratio, max_drawdown, buy_state, sell_state, fee, fund_start, round(fund_days/365.0,1)])

    en_cols = ['symbol', 'name', 'manager', 'calc_days', 'pct_cum', 'sharpe', 'max_drawdown', 'buy_state', 'sell_state', 'fee', 'fund_start', 'fund_years']
    df = pd.DataFrame(eval_table, columns=en_cols)

    df['annual'] = round((np.power((df['pct_cum'] * 0.01 + 1), 1.0/(df['calc_days']/365.0)) - 1.0) * 100.0, 1)
    df['annual'] = df[['pct_cum', 'annual']].min(axis= 1)
    df['score'] = round(df['pct_cum'] * df['sharpe'] * 0.1, 1)
    df['score2'] = round(df['pct_cum'] * df['sharpe'] / df['max_drawdown'], 1)

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
    else:
        if params[0].endswith('.csv'):
            params = cli_fund_read_fund_symbols(params[0])
        elif ',' in params[0]:
            params = params[0].split(',')
        else:
            pass
        df_fund_list = df_fund_list[ df_fund_list['symbol'].isin(params) ]

    date_from, date_to, limit = date_limit_from_options(options)

    alpha_base = None
    yeartop = 0
    for k in options:
        if k.startswith('-alpha='):
            alpha_base = k.replace('-alpha=', '')
        if k.startswith('-yeartop='):
            yeartop = int(k.replace('-yeartop=', ''))
    
    df_fund_list = df_fund_list[ df_fund_list['buy_state'].isin(['限大额','开放申购']) ]

    if '-nc' in options:
        df_fund_list = df_fund_list[ ~ df_fund_list['name'].str.contains('C') ]
    if '-nlof' in options:
        df_fund_list = df_fund_list[ ~ df_fund_list['name'].str.contains('LOF') ]
    if '-netf' in options:
        df_fund_list = df_fund_list[ ~ df_fund_list['name'].str.contains('ETF') ]

    if yeartop > 0:
        symbols = []
        days = (date_to - date_from).days
        for i in range(0, days, 365):
            print('\ryear', i // 365)
            eval_from = date_from + dt.timedelta(days= i)
            df_eval = eval_fund_list(df_fund_list, date_from= eval_from, date_to= date_to)
            df_eval = df_eval.sort_values(by='pct_cum', ascending=False)
            if yeartop > 0:
                df_eval = df_eval.head(yeartop)
            symbols += df_eval['symbol'].tolist()
        df_fund_list = df_fund_list[ df_fund_list['symbol'].isin(set(symbols)) ]

    df_eval = eval_fund_list(df_fund_list, date_from= date_from, date_to= date_to, alpha_base= alpha_base)

    if '-smart' in options:
        df_eval = filter_with_options(df_eval, options)
        df_eval = sort_with_options(df_eval, ['-sortby=score', '-desc'], by_default='score')
        if limit > 0:
            df_eval = df_eval.head(limit)
    else:
        df_eval = filter_with_options(df_eval, options)
        df_eval = sort_with_options(df_eval, options, by_default='pct_cum')
        if limit > 0:
            df_eval = df_eval.head(limit)

    df_eval['fund_start'] = df_eval['fund_start'].dt.strftime('%Y-%m-%d')

    print('\r', end= '', flush= True)
    print( tb.tabulate(df_eval, headers='keys') )

    out_csv_file, out_xls_file = csv_xlsx_from_options(options)

    if out_csv_file:
        df = df_eval[['symbol', 'name']]
        df.to_csv(out_csv_file, index= False)
        print('Exported to:', out_csv_file)
        print(df)

    if out_xls_file:
        years = round((date_to - date_from).days / 365.0, 1)
        df_eval = df_eval.drop(columns=['calc_days','sell_state','fund_start'])
        df_eval = df_eval.rename(columns= {
            'symbol': '基金代码',
            'name': '基金简称',
            'manager': '基金经理',
            'pct_cum': str(years) + '年收益率',
            'sharpe': '夏普比率',
            'max_drawdown': '最大回撤',
            'volatility': '波动率',
            'buy_state': '申购状态',
            'sell_state': '赎回状态',
            'fee': '手续费',
            'fund_start': '起始日期',
            'fund_years': '基金年数',
            'annual': '年化收益',
            'score': '评分',
            'score2': '保守评分',
        })
        df_eval.to_excel(excel_writer= out_xls_file)
        print( tb.tabulate(df_eval, headers='keys') )
        print('Exported to:', out_xls_file)

# hiquant fund plot 002943
# hiquant fund plot 002943 005669
# hiquant fund plot 002943 005669 -days=365
def cli_fund_plot(params, options, title= None):
    if len(params) == 0:
        cli_fund_help()
        return

    df_fund_list = get_cn_fund_list()

    if params[0] == 'all':
        pass
    else:
        if params[0].endswith('.csv'):
            params = cli_fund_read_fund_symbols(params[0])
        elif ',' in params[0]:
            params = params[0].split(',')
        else:
            pass
        df_fund_list = df_fund_list[ df_fund_list['symbol'].isin(params) ]

    params = df_fund_list['symbol'].tolist()

    fund_symbol_names = dict_from_df(df_fund_list, 'symbol', 'name')

    date_from, date_to, limit = date_limit_from_options(options)
    if limit == 0:
        limit = 100

    df_funds = None
    i = 0
    for param in params:
        if param in fund_symbol_names:
            name = param + ' - ' + fund_symbol_names[ param ]
        else:
            name = param
        print( name )
        
        i += 1
        if i > limit:
            break

        try:
            df = get_cn_fund_daily(symbol= param)
        except:
            continue

        df = df[ df.index >= date_from ]
        df = df[ df.index < date_to ]
        df['pct_cum'] = round(((df['pct_change'] * 0.01 +1).cumprod() - 1.0) * 100.0, 1)
        if df_funds is None:
            df_funds = df[['pct_cum']]
            df_funds.columns = [ name ]
        else:
            df_funds = pd.concat([df_funds, df['pct_cum'].copy().rename(name).to_frame()], axis=1)

    base = 'sh000300'
    for k in options:
        if k.startswith('-base='):
            base = k.replace('-base=', '')
    df_base = get_index_daily( base )
    df_base = df_base[ df_base.index >= min(df_funds.index) ]
    df_base = df_base[ df_base.index < date_to ]
    df_base['pct_cum'] = (df_base['close'] / df_base['close'].iloc[0] - 1.0) * 100.0

    if '-alpha' in options:
        table = []
        for k in df_funds.columns:
            df_funds[ k ] -= df_base['pct_cum']
            pct_change = df_funds[k].pct_change(1)
            daily_sharpe_ratio = pct_change.mean() / pct_change.std()
            sharpe_ratio = round(daily_sharpe_ratio * (252 ** 0.5), 2)
            table.append([k, sharpe_ratio])
        df = pd.DataFrame(table, columns=['fund', 'sharpe'])
        df = df.sort_values(by= 'sharpe', ascending= False)
        df_funds = df_funds[ df['fund'].tolist() ]
    else:
        index_symbol_names = dict_from_df( get_cn_index_list_df() )
        base_name = index_symbol_names[ base ] if base in index_symbol_names else base
        df_funds[ base_name ] = df_base['pct_cum']

    df_funds.index = df_funds.index.strftime('%Y-%m-%d')
    if '-mix' in options:
        df = df_funds[ [ base_name ] ]
        df_funds = df_funds.drop(columns=[ base_name ])
        df['mix'] = df_funds.mean(axis=1)
        df.plot(kind='line', ylabel='return (%)', figsize=(10,6), title= title)
    else:
        df_funds.plot(kind='line', ylabel='return (%)', figsize=(10,6), title= title)
    plt.xticks(rotation=15)
    plt.show()

    pass

def cli_fund_plot_man(params, options):
    df = cli_fund_manager(params, ['-s'])
    n = df.shape[0]
    if n == 0:
        print('Not found')
    elif n > 1:
        print('Found more than one, please specify exactly company and name, like 南方基金张磊')
    else:
        row = df.iloc[0]
        symbols = row['symbol']
        title = row['company'] + ' - ' + row['name']
        cli_fund_plot([symbols], options, title= title)

def cli_fund_backtest(params, options):
    if len(params) == 0:
        cli_fund_help()
        return

    date_from, date_to, limit = date_limit_from_options(options)
    if limit == 0:
        limit = 20

    eval_period = 365 * 3
    keyword = ''
    for k in options:
        if k.startswith('-period='):
            eval_period = int(k.replace('-period=', ''))
        if k.startswith('-keyword='):
            keyword = k.replace('-keyword=', '')

    df_fund_list = get_cn_fund_list()
    if params[0] == 'all':
        pass
    elif params[0].endswith('.csv'):
        params = cli_fund_read_fund_symbols(params[0])
        df_fund_list = df_fund_list[ df_fund_list['symbol'].isin(params) ]
    else:
        df_fund_list = df_fund_list[ df_fund_list['symbol'].isin(params) ]

    df_eval = eval_fund_list(df_fund_list, (date_from - dt.timedelta(days= eval_period)), date_from)
    years = (datetime_today() - date_from).days / 365.0
    df_eval = df_eval[ df_eval['fund_years'] > (years + eval_period/365.0) ]
    df_eval = df_eval[ df_eval['annual'] > 10 ]

    if keyword:
        df_eval = df_eval[ df_eval['name'].str.contains(keyword) ]

    #for k in ['债','油','美元','商品','指数','美国','标普','纳斯达克','全球','ETF','通胀','互联网','行业','量化','C']:
    #    df_eval = df_eval[ ~ df_eval['name'].str.contains(k) ]

    df_eval = sort_with_options(df_eval, options, by_default='symbol').head(limit) #head(limit*2).tail(limit)
    print('\n')
    print( tb.tabulate(df_eval, headers='keys') )

    cli_fund_plot(df_eval['symbol'].tolist(), options)

def cli_fund(params, options):
    if (len(params) == 0) or (params[0] == 'help'):
        cli_fund_help()
        return

    action = params[0]
    params = params[1:]

    if action == 'list':
        cli_fund_list(params, options)

    elif action == 'manager':
        cli_fund_manager(params, options)

    elif action == 'company':
        cli_fund_company(params, options)

    elif action == 'update':
        cli_fund_update(params, options)

    elif action in ['eval']:
        cli_fund_eval(params, options)

    elif action in ['backtest']:
        cli_fund_backtest(params, options)

    elif action in ['plot']:
        cli_fund_plot(params, options)

    elif action in ['show']:
        cli_fund_plot_man(params, options)

    else:
        print('invalid action:', action)
        cli_fund_help()
