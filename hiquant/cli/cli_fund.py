# -*- coding: utf-8; py-indent-offset:4 -*-

import os, sys
import datetime as dt
import tabulate as tb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ..core import get_cn_fund_list, get_cn_fund_daily, get_cn_fund_manager, get_cn_fund_company, get_all_symbol_name, get_daily
from ..utils import dict_from_df, datetime_today, sort_with_options, filter_with_options, date_range_from_options, range_from_options, csv_xlsx_from_options, symbols_from_params
from ..core import LANG

def cli_fund_help():
    syntax_tips = '''Syntax:
    __argv0__ fund update <all | symbols | symbols.csv>
    __argv0__ fund list <all | symbols | symbols.csv> [-include=... -exclude=... -same=...]
    __argv0__ fund manager [<keyword>] [-s | -d] [-sortby=...] [-desc] [-filter_column=...-...]
    __argv0__ fund company [<keyword>]
    __argv0__ fund eval <all | symbols | symbols.csv> [-sortby=...] [-desc] [-filter_column=...-...]
    __argv0__ fund plot <symbols | symbols.csv> [<options>]
    __argv0__ fund backtest  <all | symbols | symbols.csv> [-ref=...] [-days=...] [-date=yyyymmdd-yyyymmdd]

Options:
    -sortby=<col> .................. sort by the column
    -sharpe=2.5- ................... sharpe value between <from> to <to>
    -drawdown_max=-20 .............. drawdown_max between <from> to <to>
    -volatility=-20 ................ volatility between <from> to <to>
    -out=file.csv .................. export fund list to .csv file
    -out=file.xlsx ................. export fund data to .xlsx file

    -s ............................. display symbol of the funds managed
    -d ............................. display symbol and name of the funds managed

Example:
    __argv0__ fund list
    __argv0__ fund list -include=广发 -exclude=债 -out=output/myfunds.csv

    __argv0__ fund pool 1.csv 2.csv -exclude=3.csv -same=4.csv -out=5.csv

    __argv0__ fund update data/myfunds.csv

    __argv0__ fund company 华安
    __argv0__ fund manager -belongto=华夏基金

    __argv0__ fund eval all -days=365 -sortby=sharpe -desc -limit=20 -out=output/top20_funds.xlsx
    __argv0__ fund plot 002943 005669 000209 -days=365

    __argv0__ fund plot data/funds.csv -days=365
    __argv0__ fund plot data/funds.csv -years=3 -mix

    __argv0__ fund backtest all -year=2018 -mix
    __argv0__ fund backtest all -year=2010-2020 -mix
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    print( syntax_tips )

def get_fund_symbol_name():
    df = get_cn_fund_list(check_date= datetime_today())
    return dict_from_df(df, 'symbol', 'name')

def get_fund_name_symbol():
    df = get_cn_fund_list(check_date= datetime_today())
    return dict_from_df(df, 'name', 'symbol')

def get_fund_company_mapping():
    df = get_cn_fund_manager(check_date= datetime_today())
    return dict_from_df(df, 'fund', 'company')

def get_manager_size_mapping():
    df = get_cn_fund_manager(check_date= datetime_today())
    df['manager'] = df['company'] + df['name']
    return dict_from_df(df, 'manager', 'size')

def get_fund_manager_mapping():
    df = get_cn_fund_manager(check_date= datetime_today())
    fund_manager = {}
    for i, row in df.iterrows():
        name = row['name']
        fund = row['fund']
        if fund in fund_manager:
            if name not in fund_manager[ fund ]:
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
        name = row['company'] + row['name']
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
# hiquant fund list -include=多因子
def cli_fund_list(params, options):
    df = get_cn_fund_list(check_date= datetime_today())

    selected = total = df.shape[0]
    if len(params) > 0:
        symbols = symbols_from_params(params)
        df = df[ df['symbol'].isin(symbols) ]

    for option in options:
        if option.startswith('-exclude='):
            keywords = option.replace('-exclude=','').split(',')
            for k in keywords:
                df = df[ ~ df['name'].str.contains(k) ]
            pass
        elif option.startswith('-include='):
            keywords = option.replace('-include=','').split(',')
            filters = None
            for k in keywords:
                filter = df['name'].str.contains(k, na=False)
                if filters is None:
                    filters = filter
                else:
                    filters = filters | filter
            df = df[ filters ]
            pass
        elif option.startswith('-belongto='):
            keyword = option.replace('-belongto=','')
            if option.endswith('.csv'):
                df_filter = pd.read_csv(keyword, dtype=str)
                companies = df_filter['company'].tolist()
            else:
                companies = [ keyword ]
            df_fund_manager = get_cn_fund_manager(check_date= datetime_today())
            df_fund_manager = df_fund_manager[ df_fund_manager['company'].isin(companies) ]
            funds = list(set(df_fund_manager['fund'].tolist()))
            df = df[ df['name'].isin(funds) ]
            pass
        elif option.startswith('-managedby='):
            keyword = option.replace('-managedby=','')
            if option.endswith('.csv'):
                df_filter = pd.read_csv(keyword, dtype=str)
                df_filter['manager'] = df_filter['company'] + df_filter['name']
                managers = df_filter['manager'].tolist()
            else:
                managers = [ keyword ]
            df_fund_manager = get_cn_fund_manager(check_date= datetime_today())
            df_fund_manager['manager'] = df_fund_manager['company'] + df_fund_manager['name']
            df_fund_manager = df_fund_manager[ df_fund_manager['manager'].isin(managers) ]
            funds = list(set(df_fund_manager['fund'].tolist()))
            df = df[ df['name'].isin(funds) ]
            pass
        pass

    df = filter_with_options(df, options)
    df = sort_with_options(df, options, by_default='symbol')

    selected = df.shape[0]

    print( tb.tabulate(df, headers='keys') )
    print( selected, 'of', total, 'funds selected.')

    out_csv_file, out_xls_file = csv_xlsx_from_options(options)

    if out_csv_file:
        df = df[['symbol', 'name']]
        df.to_csv(out_csv_file, index= False)
        print('Exported to:', out_csv_file)
        print( tb.tabulate(df, headers='keys') )

    if '-update' in options:
        cli_fund_update(df['symbol'].tolist(), options)

    if '-eval' in options:
        cli_fund_eval(df['symbol'].tolist(), options)
        return

    if '-plot' in options:
        cli_fund_plot(df['symbol'].tolist(), options + ['-man'])

# hiquant fund pool params -out=myfunds.csv
# hiquant fund pool params -same=other.csv -out=myfunds.csv
# hiquant fund pool params -exclude=other.csv -out=myfunds.csv
def cli_fund_pool(params, options):
    df = get_cn_fund_list(check_date= datetime_today())
    symbols = symbols_from_params(params)
    df = df[ df['symbol'].isin(symbols) ].reset_index(drop= True)

    for option in options:
        if option.startswith('-same='):
            other_arg = option.replace('-same=','')
            other_symbols = symbols_from_params( [ other_arg ])
            df = df[ df['symbol'].isin(other_symbols) ]
        elif option.startswith('-exclude='):
            other_arg = option.replace('-exclude=','')
            other_symbols = symbols_from_params( [ other_arg ])
            df = df[ ~ df['symbol'].isin(other_symbols) ]

    print( tb.tabulate(df, headers='keys') )

    df = filter_with_options(df, options)
    df = sort_with_options(df, options, by_default='symbol')
    range_from, range_to = range_from_options(options)
    limit = range_to - range_from
    if limit > 0:
        df = df.head(limit)

    out_csv_file, out_xlsx_file = csv_xlsx_from_options(options)

    if out_csv_file:
        df = df[['symbol', 'name']]
        df.to_csv(out_csv_file, index= False)
        print('Exported to:', out_csv_file)

    if out_xlsx_file:
        df = df[['symbol', 'name']]
        df.to_excel(out_xlsx_file, index= False)
        print('Exported to:', out_xlsx_file)

def cli_fund_company(params, options):
    df = get_cn_fund_company()

    limit = 0
    yeartop = ''
    manager_out_csv = ''
    for k in options:
        if k.startswith('-limit='):
            limit = int(k.replace('-limit=',''))
        if k.startswith('-yeartop='):
            yeartop = k.replace('-yeartop=','')
        if k.startswith('-manager_out=') and k.endswith('.csv'):
            manager_out_csv = k.replace('-manager_out=','')

    if yeartop:
        df_top_managers = cli_fund_manager([], ['-yeartop='+yeartop])
        df_yeartop = df_top_managers[['company']].groupby(['company']).size().reset_index(name='yeartopn')
        company_yeartop = dict_from_df(df_yeartop, 'company', 'yeartopn')
        df['yeartopn'] = [company_yeartop[c] if (c in company_yeartop) else 0 for c in df['company'].tolist()]

        company_managers = {}
        df_top_managers = df_top_managers.sort_values(by= 'best_return', ascending= False)
        for i, row in df_top_managers.iterrows():
            manager = row['name']
            company = row['company']
            if company in company_managers:
                company_managers[company].append(manager)
            else:
                company_managers[company] = [ manager ]

        df['names'] = ''
        for i, row in df.iterrows():
            company = row['company']
            if company in company_managers:
                names = ','.join( company_managers[company] )
                df['names'].iloc[i] = names

    if len(params) > 0:
        if '.csv' in params[0]:
            company_names = pd.read_csv(params[0], dtype=str)['company'].tolist()
            df = df[ df['company'].isin(company_names) ]
        else:
            keyword = params[0]
            df = df[ df['company'].str.contains(keyword, na=False) ]

    selected = total = df.shape[0]
    df = filter_with_options(df, options)

    for k in options:
        if k.startswith('-sortby='):
            df = sort_with_options(df, options, by_default='managers')

    if limit > 0:
        df = df.head(limit)

    selected = df.shape[0]
    df = df.reset_index(drop= True)
    print( tb.tabulate(df, headers='keys') )
    print( selected, 'of', total, 'fund companies.')

    out_csv_file, out_xls_file = csv_xlsx_from_options(options)

    if manager_out_csv:
        table = []
        for i, row in df.iterrows():
            company = row['company']
            names = row['names'].split(',')
            for name in names:
                table.append([company, name])
        df_manager = pd.DataFrame(table, columns=['company','name'])
        df_manager.to_csv(manager_out_csv, index=False)
        print('Managers exported to:', manager_out_csv)

    if out_csv_file:
        df_com = df[['company']]
        df_com.to_csv(out_csv_file, index=False)
        print( tb.tabulate(df_com, headers='keys') )
        print('Exported to:', out_csv_file)

    if out_xls_file:
        df_com = df.rename(columns= {
            'company_start': '成立日期',
            'size': '管理规模\n(亿)',
            'funds': '基金\n总数',
            'managers': '基金经理\n人数',
            'yeartopn': '业绩前列\n经理人数',
            'names': '业绩优秀 基金经理 姓名',
        })
        del df_com['update_date']
        df_com.to_excel(excel_writer= out_xls_file)
        print( tb.tabulate(df_com, headers='keys') )
        print('Exported to:', out_xls_file)

    if '-plot' in options:
        df_company_tmp = df.copy()
        for i, row in df_company_tmp.iterrows():
            company = row['company']
            cli_fund_list([], options + ['-belongto=' + company, '-exclude=C,债,FOF,QDII,LOF', '-eval', '-one_per_manager', '-limit=10', '-png=output/' + company + '.png'])

def get_fund_area(name):
    fund_areas = {
        'QDII': ['QDII','美国','全球','现钞','现汇','人民币','纳斯达克','标普'],
        'ETF': ['ETF','指数','联接'],
        '债券': ['债'],
        '量化': ['量化'],
        '新能源': ['能源','双碳','低碳','碳中和','新经济','环保','环境','气候','智能汽车'],
        '高端制造': ['制造','智造','战略','新兴产业'],
        '信息技术': ['信息','互联网','芯片','半导体','集成电路','云计算'],
        '医疗': ['医疗','养老','医药','健康'],
        '军工': ['军工','国防','安全'],
        '消费': ['消费','品质','白酒'],
        '周期': ['周期','资源','钢铁','有色','金融','地产'],
        '中小盘': ['中小盘','成长','创新'],
        '价值': ['蓝筹','价值','龙头','优势','核心'],
        '灵活配置': ['灵活配置','均衡'],
    }
    for k in fund_areas:
        keywords = fund_areas[k]
        for kk in keywords:
            if kk in name:
                return k
    return ''

def cli_fund_manager(params, options):
    df = get_cn_fund_manager(check_date= datetime_today())
    selected = total = df.shape[0]

    if len(params) > 0:
        keyword = params[0]
        if ',' in keyword:
            keyword = keyword.replace(',', '')
        if keyword.endswith('.csv') or keyword.endswith('.xlsx'):
            df_filter = pd.read_csv(keyword, dtype= str) if keyword.endswith('.csv') else pd.read_excel(keyword, dtype= str)
            if 'name' in df_filter.columns:
                df_filter['manager'] = df_filter['company'] + df_filter['name']
                df1 = df.copy()
                df1['manager'] = df['company'] + df['name']
                df = df1[ df1['manager'].isin(df_filter['manager'].tolist()) ].drop(columns=['manager'])
            else:
                df = df[ df['company'].isin(df_filter['company'].tolist()) ]
        else:
            df1 = df.copy()
            df1['keywords'] = df1['company'] + df1['name'] + ' ' + df1['fund']
            df = df1[ df1['keywords'].str.contains(keyword, na=False) ].drop(columns=['keywords'])

    yeartop = ''
    limit = 0
    belongto = ''
    for k in options:
        if k.startswith('-limit='):
            limit = int(k.replace('-limit=',''))
        if k.startswith('-yeartop='):
            yeartop = k.replace('-yeartop=', '')
        if k.startswith('-fund='):
            fund = k.replace('-fund=','')
            df = df[ df['fund'].str.contains(fund, na=False) ]
        if k.startswith('-belongto='):
            belongto = k.replace('-belongto=', '')

    df_company = get_cn_fund_company()
    company_managers = dict_from_df(df_company, 'company', 'managers')
    company_funds = dict_from_df(df_company, 'company', 'funds')

    group = '-f' not in options
    if group and (df.shape[0] > 0):
        df_tmp = df.drop(columns=['fund'])
        table = []
        name = ''
        for i, row in df_tmp.iterrows():
            c = row['company']
            manager = c + row['name']
            if name == manager:
                continue
            else:
                name = manager
                data = list(row.values)

                managers = company_managers[c] if (c in company_managers) else 0
                funds = company_funds[c] if (c in company_funds) else 0
                data.insert(2, managers)
                data.insert(3, funds)

                table.append( data )

        cols = list(row.keys())
        cols.insert(2, 'managers')
        cols.insert(3, 'funds')
        df = pd.DataFrame(table, columns=cols)

    df['annual'] = round((np.power((df['best_return'] * 0.01 + 1), 1.0/(np.maximum(365.0,df['days'])/365.0)) - 1.0) * 100.0, 1)

    if yeartop:
        df1 = df[ df['days'] >= 3650 ].sort_values(by='best_return', ascending=False)
        if '%' in yeartop:
            yeartopn = int(yeartop.replace('%','')) * df1.shape[0] // 100
        else:
            yeartopn = int(yeartop)
        df1 = df1.head(yeartopn)

        for i in range(9,0,-1):
            df2 = df[ (df['days'] >= (i*365)) & (df['days'] < ((i+1))*365) ].sort_values(by='best_return', ascending=False)
            if '%' in yeartop:
                yeartopn = int(yeartop.replace('%','')) * df2.shape[0] // 100
            else:
                yeartopn = int(yeartop)
            df2 = df2.head( yeartopn )
            df1 = pd.concat([df1, df2], ignore_index=True)
        df = df1

    df.insert(5, 'years', round(df['days'] / 365.0, 1))

    selected = total = df.shape[0]
    df = filter_with_options(df, options)

    if belongto:
        if belongto.endswith('.csv'):
            belongto = pd.read_csv(belongto, dtype= str)['company'].tolist()
        elif ',' in belongto:
            belongto = belongto.split(',')
        else:
            belongto = [ belongto ]
        df = df[ df['company'].isin(belongto) ]

    for k in options:
        if k.startswith('-sortby='):
            df = sort_with_options(df, options, by_default='best_return')
            break
    if limit > 0:
        df = df.head(limit)

    if 'fund' in df.columns:
        fund_name_symbol = get_fund_name_symbol()
        df.insert(2, 'symbol', [(fund_name_symbol[fund] if fund in fund_name_symbol else '') for fund in df['fund'].tolist()])
        df = df[ df['symbol'] != '' ]
    elif ('-s' in options) and ('name'in df.columns):
        manager_fundsymbol = get_manager_fundsymbol_mapping()
        managers = (df['company'] + df['name']).tolist()
        df['symbol'] = [(','.join(manager_fundsymbol[manager]) if manager in manager_fundsymbol else '') for manager in managers]
    elif ('-sd' in options) and ('name'in df.columns):
        manager_fund = get_manager_fund_mapping()
        managers = (df['company'] + df['name']).tolist()
        df['fund'] = [('\n'.join(manager_fund[manager]) if manager in manager_fund else '') for manager in managers]
        df['area'] = df['fund'].apply(get_fund_area)

    df = df.reset_index(drop= True)
    selected = df.shape[0]
    print( tb.tabulate(df, headers='keys') )
    print( selected, 'of', total, 'selected.')

    out_csv_file, out_xls_file = csv_xlsx_from_options(options)

    if out_csv_file:
        df_csv = df[['name','company']]
        df_csv.to_csv(out_csv_file, index= False)
        print( tb.tabulate(df_csv, headers='keys') )
        print('Exported to:', out_csv_file)

    if out_xls_file:
        if 'days' in df.columns:
            df = df.drop(columns=['days'])
        df = df.rename(columns= {
            'managers': '基金经理人数',
            'funds': '基金总数',
            'fund': '基金',
            'area': '投资方向',
            'years': '管理年限',
            'size': '基金规模',
            'best_return': '最佳回报',
            'annual': '年化收益',
        })
        df.to_excel(excel_writer= out_xls_file)
        print( tb.tabulate(df, headers='keys') )
        print('Exported to:', out_xls_file)

    if '-plot' in options:
        for i, row in df.iterrows():
            manager = row['company'] + row['name']
            cli_fund_show([manager], ['-png=output/' + manager + '.png'])

    return df

def cli_fund_read_fund_symbols(excel_file):
    if excel_file.endswith('.csv'):
        df = pd.read_csv(excel_file, dtype=str)
    elif excel_file.endswith('.xlsx'):
        df = pd.read_excel(excel_file, dtype=str)

    return df['symbol'].tolist() if ('symbol' in df) else []

# hiquant fund update <symbols>
# hiquant fund update <symbols.csv>
# hiquant fund update all -range=500-
def cli_fund_update(params, options):
    if len(params) == 0:
        cli_fund_help()
        return

    range_from, range_to = range_from_options(options)

    df_fund_list = get_cn_fund_list(check_date= datetime_today())

    if params[0] == 'all':
        symbols = df_fund_list['symbol'].tolist()
    else:
        symbols = symbols_from_params(params)
        df_fund_list = df_fund_list[ df_fund_list['symbol'].isin(symbols) ]

    fund_symbol_names = dict_from_df(df_fund_list, 'symbol', 'name')

    i = 0
    n = len(symbols)
    for symbol in symbols:
        i += 1
        if range_from > 0 and i < range_from:
            continue
        if range_to > 0 and i > range_to:
            break

        name = symbol + ' - ' + fund_symbol_names[ symbol ]
        print('{}/{} - updating {} ...'.format(i, n, name))
        try:
            df = get_cn_fund_daily(symbol= symbol, check_date= datetime_today())
        except (KeyError, ValueError, IndexError) as err:
            print('error downloading', name)
            pass

    print('Done.')

def eval_fund_list(df_fund_list, date_from, date_to, ignore_new = False):
    fund_manager = get_fund_manager_mapping()
    fund_company = get_fund_company_mapping()
    manager_size = get_manager_size_mapping()

    days = (date_to - date_from).days
    eval_table = []
    for index, row in df_fund_list.iterrows():
        symbol = row['symbol']
        name = row['name']
        buy_state = row['buy_state']
        sell_state = row['sell_state']
        fee = row['fee']
        print('\r', index, '-', symbol, '-', name, '...', end='', flush= True)

        try:
            df = get_cn_fund_daily(symbol= symbol)
        except (KeyError, ValueError, IndexError) as err:
            print('\nerror downloading', name, ', skip.')
            continue

        fund_start = min(df.index)
        fund_days = (datetime_today() - fund_start).days

        if ignore_new and (fund_start > date_from):
            continue

        df = df[ df.index >= date_from ]
        df = df[ df.index < date_to ]
        if df.shape[0] == 0:
            continue

        # skip the fund if data not reasonable, pct_change > 10.0%
        pct_change_max = df['pct_change'].max()
        if pct_change_max > 20.0:
            print('pct_change_max', pct_change_max)
            continue

        try:
            df['earn'] = (df['pct_change'] * 0.01 +1).cumprod()
            earn = df['earn'].iloc[-1] - 1.0
            earn = round(earn * 100, 2)
            earn_max = df['earn'].max() - 1.0
            earn_max = round(earn_max * 100, 2)
        except (KeyError, ValueError, IndexError) as err:
            print('error calculating', symbol, name, ', skip.')
            continue

        risk_free_rate = 3.0 / 365
        daily_sharpe_ratio = (df['pct_change'].mean() - risk_free_rate) / df['pct_change'].std()
        sharpe_ratio = round(daily_sharpe_ratio * (252 ** 0.5), 2)

        drawdown = df['earn'] / df['earn'].cummax() - 1.0
        drawdown_max = round(100 * drawdown.min(), 2)
        drawdown_now = round(100 * drawdown.iloc[-1], 2)
        drawdown_percent = round(drawdown_now / drawdown_max * 100) if (drawdown_max < 0) else 100

        logreturns = np.diff( np.log(df['earn']) )
        volatility = np.std(logreturns)
        annualVolatility = volatility * (252 ** 0.5)
        annualVolatility = round(annualVolatility * 100, 2)

        managers = fund_manager[name] if (name in fund_manager) else []
        manager = managers[0] if len(managers) > 0 else ''
        manager2 = managers[1] if len(managers) > 1 else ''
        manager3 = managers[2] if len(managers) > 2 else ''

        company = fund_company[name] if (name in fund_company) else ''

        if name not in fund_manager:
            print('name not in fund manager')
            continue
        key_manager = company + manager
        size = manager_size[key_manager] if (key_manager in manager_size) else 0

        eval_table.append([symbol, name, company, manager, manager2, manager3, size, min(days, fund_days), earn, earn_max, drawdown_now, drawdown_max, drawdown_percent, sharpe_ratio, buy_state, sell_state, fee, fund_start, round(fund_days/365.0,1)])

    en_cols = ['symbol', 'name', 'company', 'manager', 'manager2', 'manager3', 'size', 'calc_days', 'earn', 'earn_max', 'drawdown', 'drawdown_max', 'drawdown_pct', 'sharpe', 'buy_state', 'sell_state', 'fee', 'fund_start', 'fund_years']
    df = pd.DataFrame(eval_table, columns=en_cols)

    df['annual'] = round((np.power((df['earn'] * 0.01 + 1), 1.0/(df['calc_days']/365.0)) - 1.0) * 100.0, 1)
    #df['annual'] = df[['earn', 'annual']].min(axis= 1)
    df['score'] = round(df['earn'] * df['sharpe'] * 0.1, 1)
    df['score2'] = round(- df['earn'] * df['sharpe'] / df['drawdown_max'], 1)

    return df

# hiquant fund eval 002943 005669
# hiquant fund eval 002943 005669 -days=365
# hiquant fund eval data/myfunds.csv -days=365
# hiquant fund eval all -days=365 -sortby=sharpe -desc
def cli_fund_eval(params, options):
    if len(params) == 0:
        cli_fund_help()
        return

    yeartop = 0
    manager_out_csv = ''
    managedby = ''
    belongto = ''
    myfunds = ''
    for k in options:
        if k.startswith('-yeartop='):
            yeartop = int(k.replace('-yeartop=', ''))
        if k.startswith('-manager_out=') and k.endswith('.csv'):
            manager_out_csv = k.replace('-manager_out=', '')
        if k.startswith('-managedby='):
            managedby = k.replace('-managedby=', '')
        if k.startswith('-belongto='):
            belongto = k.replace('-belongto=', '')
        if k.startswith('-myfunds='):
            myfunds = k.replace('-myfunds=', '')

    df_fund_list = get_cn_fund_list()

    if myfunds:
        params.append( myfunds )

    if params[0] == 'all':
        pass
    else:
        symbols = symbols_from_params(params)
        df_fund_list = df_fund_list[ df_fund_list['symbol'].isin(symbols) ]

    date_from, date_to = date_range_from_options(options)
    range_from, range_to = range_from_options(options)

    if '-nc' in options:
        df_fund_list = df_fund_list[ df_fund_list['buy_state'].isin(['限大额','开放申购']) ]

        for k in ['C','E','持有']:
            df_fund_list = df_fund_list[ ~ df_fund_list['name'].str.contains(k) ]

        for k in ['债','油','黄金','商品','资源','周期','通胀','全球','美元','美汇','美钞','美国','香港','恒生','海外','亚太','亚洲','四国','QDII','纳斯达克','标普']:
            df_fund_list = df_fund_list[ ~ df_fund_list['name'].str.contains(k) ]

        for k in ['ETF','指数','联接','中证']:
            df_fund_list = df_fund_list[ ~ df_fund_list['name'].str.contains(k) ]

    if yeartop > 0:
        symbols = []
        days = (date_to - date_from).days
        for i in range(0, days, 365):
            print('\ryear', i // 365)
            eval_from = date_from + dt.timedelta(days = i)
            eval_to = min(eval_from + dt.timedelta(days= 365), date_to)
            df_eval = eval_fund_list(df_fund_list, date_from= eval_from, date_to= eval_to)
            df_eval = sort_with_options(df_eval, options, by_default='earn')
            if yeartop > 0:
                df_eval = df_eval.head(yeartop)
            symbols += df_eval['symbol'].tolist()
        df_fund_list = df_fund_list[ df_fund_list['symbol'].isin(set(symbols)) ]

    df_eval = eval_fund_list(df_fund_list, date_from= date_from, date_to= date_to)

    if myfunds:
        if myfunds.endswith('.csv'):
            df_myfunds = pd.read_csv(myfunds, dtype=str)
        elif myfunds.endswith('.xlsx'):
            df_myfunds = pd.read_excel(myfunds, dtype=str)
        df_eval['total'] = 0
        for i in range(10):
            k = 'account' + str(i)
            if k in df_myfunds.columns:
                symbol_account = dict_from_df(df_myfunds, 'symbol', k)
                df_eval[k] = np.nan
                for i, row in df_eval.iterrows():
                    symbol = row['symbol']
                    if symbol in symbol_account:
                        df_eval[k].iloc[i] = float(symbol_account[symbol])
                df_eval[k] = df_eval[k].fillna(0)
                df_eval['total'] += df_eval[k]

    if managedby:
        if managedby.endswith('.csv') or managedby.endswith('.xlsx'):
            df_manager = pd.read_csv(managedby, dtype= str) if managedby.endswith('.csv') else pd.read_excel(managedby, dtype=str)
            managedby = (df_manager['company'] + df_manager['name']).tolist()
            df_tmp = df_eval.copy()
            df_tmp['manager'] = df_tmp['company'] + df_tmp['manager']
            df_tmp['manager2'] = df_tmp['company'] + df_tmp['manager2']
            df_tmp['manager3'] = df_tmp['company'] + df_tmp['manager3']
            df_tmp = df_tmp[ df_tmp['manager'].isin(managedby) | df_tmp['manager2'].isin(managedby) | df_tmp['manager3'].isin(managedby)  ]
            symbols = df_tmp['symbol'].tolist()
            df_eval = df_eval[ df_eval['symbol'].isin(symbols) ]
        else:
            if ',' in managedby:
                managedby = managedby.split(',')
            else:
                managedby = [ managedby ]
            df_eval = df_eval[ df_eval['manager'].isin(managedby) | df_eval['manager2'].isin(managedby) | df_eval['manager3'].isin(managedby)  ]

    if belongto:
        if belongto.endswith('.csv'):
            df_company = pd.read_csv(belongto, dtype= str)
            belongto = df_company['company'].tolist()
        elif belongto.endswith('.xlsx'):
            df_company = pd.read_excel(belongto, dtype= str)
            belongto = df_company['company'].tolist()
        else:
            if ',' in belongto:
                belongto = belongto.split(',')
            else:
                belongto = [ belongto ]
        df_eval = df_eval[ df_eval['company'].isin(belongto) ]

    df_eval = filter_with_options(df_eval, options)
    df_eval = sort_with_options(df_eval, options, by_default='earn')

    if '-one_per_manager' in options:
        manager_symbol = {}
        for i, row in df_eval.iterrows():
            symbol = row['symbol']
            manager = row['company'] + row['manager']
            if manager in manager_symbol:
                continue
            else:
                manager_symbol[ manager ] = symbol
        df_eval = df_eval[ df_eval['symbol'].isin(manager_symbol.values()) ]

    if '-one_per_company' in options:
        company_symbol = {}
        for i, row in df_eval.iterrows():
            symbol = row['symbol']
            company = row['company']
            if company in company_symbol:
                continue
            else:
                company_symbol[ company ] = symbol
        df_eval = df_eval[ df_eval['symbol'].isin(company_symbol.values()) ]

    if range_to:
        df_eval = df_eval.head(range_to)
    if range_from:
        df_eval = df_eval.tail(range_to - range_from)

    df_eval = df_eval.reset_index(drop= True)

    df_eval.insert(2, 'area', df_eval['name'].apply(get_fund_area))

    df_eval['fund_start'] = df_eval['fund_start'].dt.strftime('%Y-%m-%d')

    print('\r', end= '', flush= True)
    print( tb.tabulate(df_eval, headers='keys') )

    out_csv_file, out_xls_file = csv_xlsx_from_options(options)

    if out_csv_file:
        df = df_eval[['symbol', 'name']]
        df.to_csv(out_csv_file, index= False)
        print('Exported to:', out_csv_file)
        print(df)

    if manager_out_csv:
        managers = {}
        for i, row in df_eval.iterrows():
            company = row['company']
            name = row['name']
            managers[ company + ' ' + name ] = 1

        table = []
        for k in managers.keys():
            items = k.split(' ')
            table.append([items[0], items[1]])
        df_manager = pd.DataFrame(table, columns=['company','name'])
        df_manager.to_csv(manager_out_csv, index= False)
        print( tb.tabulate(df_manager, headers='keys') )

    if out_xls_file:
        years = round((date_to - date_from).days / 365.0, 1)
        df_eval = df_eval.drop(columns=['calc_days','sell_state','fund_start'])
        df_eval = df_eval.rename(columns= {
            'name': '基金简称',
            'company': '基金公司',
            'manager': '基金经理',
            'manager2': '基金经理',
            'manager3': '基金经理',
            'size': '管理规模',
            'earn': str(years) + '年\n收益率',
            'sharpe': '夏普比率',
            'drawdown_max': '最大回撤',
            'drawdown_now': '目前回撤',
            'volatility': '波动率',
            'buy_state': '申购状态',
            'sell_state': '赎回状态',
            'fee': '手续费',
            'fund_start': '起始日期',
            'fund_years': '基金年数',
            'annual': '年化收益',
            'score': '评分',
            'score2': '保守评分',
            'area': '投资方向',
        })
        df_eval.to_excel(excel_writer= out_xls_file, index= False)
        print( tb.tabulate(df_eval, headers='keys') )
        print('Exported to:', out_xls_file)

    if '-plot' in options:
        cli_fund_plot(df_eval['symbol'].tolist(), options + ['-man'], sizes = dict_from_df(df_eval, 'symbol', 'size'), pcts = dict_from_df(df_eval, 'symbol', 'earn'))

    elif '-plot_company' in options:
        companies = list(set(df_eval['company'].tolist()))
        options.append('-limit=5')
        for company in companies:
            df_funds = df_eval[ df_eval['company'] == company ]
            cli_fund_plot(df_funds['symbol'].tolist(), options, png= 'output/' + company + '.png')

# hiquant fund plot 002943
# hiquant fund plot 002943 005669
# hiquant fund plot 002943 005669 -days=365
def cli_fund_plot(params, options, title= None, mark_date = None, png = None, sizes = None, pcts = None):
    if len(params) == 0:
        cli_fund_help()
        return

    df_fund_list = get_cn_fund_list()

    if params[0] == 'all':
        pass
    else:
        symbols = symbols_from_params(params)
        df_fund_list = df_fund_list[ df_fund_list['symbol'].isin(symbols) ]

    params = df_fund_list['symbol'].tolist()

    fund_symbol_names = dict_from_df(df_fund_list, 'symbol', 'name')
    fund_manager_mapping = get_fund_manager_mapping()

    date_from, date_to = date_range_from_options(options)
    range_from, range_to = range_from_options(options)
    limit = range_to - range_from
    if limit == 0:
        limit = 100

    df_funds = None
    i = 0
    for symbol in params:
        if symbol in fund_symbol_names:
            name = fund_symbol_names[ symbol ]
            if '-man' in options:
                name = name + '(' + (','.join(fund_manager_mapping[name])) + ')'
            display_name = symbol + ',' + name
        else:
            display_name = symbol
        if (pcts is not None) and (symbol in pcts):
            display_name += ',' + str(int(pcts[ symbol ])) + '%'
        if (sizes is not None) and (symbol in sizes):
            display_name += ',' + str(int(sizes[ symbol ])) + '亿'
        print( display_name )
        
        i += 1
        if i > limit:
            break

        try:
            df = get_cn_fund_daily(symbol= symbol, check_date= datetime_today())
            #df = get_cn_fund_daily(symbol= param, check_date= None)
        except:
            continue

        df = df[ df.index >= date_from ]
        df = df[ df.index < date_to ]
        df['earn'] = round(((df['pct_change'] * 0.01 +1).cumprod() - 1.0) * 100.0, 1)
        if df_funds is None:
            df_funds = df[['earn']]
            df_funds.columns = [ display_name ]
        else:
            df_funds = pd.concat([df_funds, df['earn'].copy().rename(display_name).to_frame()], axis=1)

    if '-mix' in options:
        df_funds = df_funds.mean(axis=1).to_frame()
        df_funds.columns = ['平均收益']
    else:
        if df_funds.shape[0] > 0:
            col = df_funds.iloc[-1].copy()
            col.name = 'earn'
            df_cmp = col.to_frame()
            df_cmp.insert(0, 'symbol', df_cmp.index)
            df_cmp = df_cmp.sort_values(by='earn', ascending= False)
            df_cmp.reset_index(drop= True, inplace= True)
            df_funds = df_funds[ df_cmp['symbol'].tolist() ]
        pass

    base = 'sh000300'
    for k in options:
        if k.startswith('-base='):
            base = k.replace('-base=', '')
        if k.startswith('-png='):
            png = k.replace('-png=', '')

    symbol_names = get_all_symbol_name()
    bases = base.split(',') if (',' in base) else [ base ]
    for base in bases:
        df_base = get_daily( base )
        df_base = df_base[ df_base.index >= min(df_funds.index) ]
        df_base = df_base[ df_base.index < date_to ]
        df_base['earn'] = (df_base['close'] / df_base['close'].iloc[0] - 1.0) * 100.0
        base_name = symbol_names[ base ] if base in symbol_names else base
        df_funds[ base_name ] = df_base['earn']

    #df_funds.index = df_funds.index.strftime('%Y-%m-%d')
    if title is None:
        title = LANG('return on investment')
    df_funds.plot(kind='line', ylabel=LANG('return(%)'), xlabel=LANG('date'), figsize=(10,6), title= title)

    if mark_date:
        #mark_x = mark_date.strftime('%Y-%m-%d')
        mark_x = mark_date
        df_tmp = df_funds[ df_funds.index >= mark_x ]
        if df_tmp.shape[0] > 0:
            mark_x = np.datetime64(mark_x)
            mark_y = max(list(df_tmp.iloc[0]))
            if np.isnan(mark_y):
                mark_y = 0.0
            max_y = max(list(df_tmp.iloc[-1]))
            plt.annotate('更换\n基金经理\n(' + mark_date.strftime('%Y-%m-%d') + ')',
                xy= (mark_x, mark_y + (max_y - mark_y)/20),
                xycoords= 'data',
                xytext= (mark_x, mark_y + (max_y - mark_y)/3),
                arrowprops= dict(arrowstyle='->', color='red'),
                ha= 'center',
                va= 'center',
                fontsize= 12,
            )

    plt.xticks(rotation=15)
    plt.legend(loc='upper left')
    if png is None:
        plt.show()
    else:
        plt.savefig(png)

def cli_fund_show(params, options):
    if len(params) == 2:
        if params[1].endswith('基金'):
            params = [ params[1] + params[0] ]
        else:
            params = [ params[0] + params[1] ]

    df = cli_fund_manager(params, ['-s'])

    n = df.shape[0]
    if n == 0:
        print('Not found')
    elif n > 1:
        print('Found more than one, please specify exactly company and name, like 南方基金张磊')
    else:
        row = df.iloc[0]
        symbols = row['symbol']
        mark_date = datetime_today() - dt.timedelta(days= int(row['days']))
        title = row['company'] + ' - ' + row['name']
        cli_fund_plot([symbols], options, title= title, mark_date = mark_date)

def filter_fund_list_simple_top(df_fund_list, date_from, ref_period):
    df_eval = eval_fund_list(df_fund_list, (date_from - dt.timedelta(days= ref_period)), date_from)
    years = (datetime_today() - date_from).days / 365.0
    eval_years = ref_period / 365.0
    df_eval = df_eval[ df_eval['fund_years'] > years + eval_years ]
    df_eval = df_eval[ df_eval['earn'] > 10.0 ]
    return df_eval

def filter_fund_list_4433(df_fund_list, date_from, ref_period):
    conditions = {
        '5': 0.25,
        '3': 0.25,
        '2': 0.25,
        '1': 0.25,
        '0.5': 0.33,
        '0.25': 0.33,
    }
    symbols = []
    for ref_str, top_percent in conditions.items():
        ref_n = float(ref_str) * 365.0
        df_eval = eval_fund_list(df_fund_list, (date_from - dt.timedelta(days= ref_n)), date_from, ignore_new = True)
        years = (datetime_today() - date_from).days / 365.0
        eval_years = ref_n / 365.0
        df_eval = df_eval[ df_eval['fund_years'] > years + eval_years ]
        df_eval = df_eval.sort_values(by= 'earn', ascending= False)
        top_N = int(df_eval.shape[0] * top_percent)
        df_eval = df_eval.head( top_N )
        if len(symbols) == 0:
            symbols = df_eval['symbol'].tolist()
        else:
            symbols = list(set(symbols) & set(df_eval['symbol'].tolist()))

    return eval_fund_list(df_fund_list, (date_from - dt.timedelta(days= ref_period)), date_from)

def cli_fund_backtest(params, options):
    if len(params) == 0:
        cli_fund_help()
        return

    date_from, date_to = date_range_from_options(options)
    range_from, range_to = range_from_options(options)
    limit = range_to - range_from
    if limit == 0:
        limit = 20

    ref_period = 365 * 5
    keyword = ''
    company = ''
    manager = ''
    for k in options:
        if k.startswith('-ref='):
            ref_period = int(float(k.replace('-ref=', '')) * 365)
        if k.startswith('-keyword='):
            keyword = k.replace('-keyword=', '')
        if k.startswith('-company='):
            company = k.replace('-company=', '')
        if k.startswith('-manager='):
            manager = k.replace('-manager=', '')

    df_fund_list = get_cn_fund_list()

    if params[0] == 'all':
        pass
    else:
        symbols = symbols_from_params(params)
        df_fund_list = df_fund_list[ df_fund_list['symbol'].isin(symbols) ]

    for k in ['C','持有']:
        df_fund_list = df_fund_list[ ~ df_fund_list['name'].str.contains(k) ]

    for k in ['债','金','油','商品','通胀','全球','美元','美国','香港','恒生','海外','亚太','亚洲','四国','QDII','纳斯达克','标普']:
        df_fund_list = df_fund_list[ ~ df_fund_list['name'].str.contains(k) ]

    for k in ['LOF']:
        df_fund_list = df_fund_list[ ~ df_fund_list['name'].str.contains(k) ]

    for k in ['ETF','指数','联接']:
        df_fund_list = df_fund_list[ ~ df_fund_list['name'].str.contains(k) ]

    df_eval = filter_fund_list_4433(df_fund_list, date_from, ref_period)

    if keyword:
        df_eval = df_eval[ df_eval['name'].str.contains(keyword) ]

    if company:
        if company.endswith('.csv'):
            company = pd.read_csv(company, dtype= str)['company'].tolist()
        elif ',' in company:
            company = company.split(',')
        else:
            company = [ company ]
        df_eval = df_eval[ df_eval['company'].isin(company) ]

    if manager:
        if manager.endswith('.csv'):
            manager = pd.read_csv(manager, dtype= str)['name'].tolist()
        elif ',' in manager:
            manager = manager.split(',')
        else:
            manager = [ manager ]
        df_eval = df_eval[ df_eval['manager'].isin(manager) | df_eval['manager2'].isin(manager) | df_eval['manager3'].isin(manager)  ]

    df_eval = sort_with_options(df_eval, options, by_default='earn')
    symbols = []
    managers = []
    for i, row in df_eval.iterrows():
        if row['manager'] not in managers:
            managers.append( row['manager'])
            symbols.append(row['symbol'])
        if len(symbols) >= limit:
            break
    df_eval = df_eval[ df_eval['symbol'].isin(symbols) ]
    print('\n')
    print( tb.tabulate(df_eval, headers='keys') )
    print( ','.join(df_eval['symbol'].tolist()) )

    title = str(date_from.year) + '年初TOP' + str(limit) + '基金 ' + str(date_from.year) + '-' + str(date_to.year) + '年表现'
    cli_fund_plot(df_eval['symbol'].tolist(), options, title= '基金回测 - ' + title)

def cli_fund(params, options):
    if (len(params) == 0) or (params[0] == 'help'):
        cli_fund_help()
        return

    action = params[0]
    params = params[1:]

    if action == 'list':
        cli_fund_list(params, options)

    elif action == 'pool':
        cli_fund_pool(params, options)

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
        cli_fund_show(params, options)

    else:
        print('invalid action:', action)
        cli_fund_help()
