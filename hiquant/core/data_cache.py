# -*- coding: utf-8; py-indent-offset:4 -*-

import os
#import random
import datetime as dt
import numpy as np
import pandas as pd

from ..utils import get_file_modify_time, datetime_today, symbol_normalize, symbol_market, dict_from_df

from ..data_source import *

def get_cached_download_df(csv_file, download_func, param = None, check_date = None):
    if type(param) == str:
        csv_file = csv_file.replace('{param}', param)

    # like ^GSPC.csv, will cause trouble when manually delete
    csv_file = csv_file.replace('^','_').replace('$','_')

    need_update = False
    if os.path.isfile(csv_file):
        if check_date is not None:
            modified_time = get_file_modify_time(csv_file)
            need_update = modified_time < check_date
        else:
            need_update = False
    else:
        need_update = True

    if need_update:
        for i in range(3):
            try:
                df = download_func(param)
            except (ValueError, IndexError) as err:
                _DOWNLOAD_RETRY_DELAY = 300
                print('downloading failed, try again after {} min'.format(_DOWNLOAD_RETRY_DELAY // 60))
                time.sleep(_DOWNLOAD_RETRY_DELAY)
                df = None

            if df is not None:
                df.to_csv(csv_file, index= bool(df.index.name))
                return df

        if df is None:
            print('downloading failed after 3 tries, loading cached data')

    df = pd.read_csv(csv_file, dtype=str)
    return df

def get_cn_stock_list_df():
    return get_cached_download_df('cache/cn_stock_list.csv', download_cn_stock_list, check_date= datetime_today())

def get_hk_stock_list_df():
    return get_cached_download_df('cache/hk_stock_list.csv', download_hk_stock_list, check_date= datetime_today())

def get_us_stock_list_df():
    return get_cached_download_df('cache/us_stock_list.csv', download_us_stock_list, check_date= datetime_today())

def get_cn_index_list_df():
    return get_cached_download_df('cache/cn_index_list.csv', download_cn_index_list, check_date= datetime_today())

def get_hk_index_list_df():
    return get_cached_download_df('cache/hk_index_list.csv', download_hk_index_list, check_date= datetime_today())

def get_us_index_list_df():
    return get_cached_download_df('cache/us_index_list.csv', download_us_index_list, check_date= datetime_today())

def get_world_index_list_df():
    return get_cached_download_df('cache/world_index_list.csv', download_world_index_list, check_date= None)

_market_funcs_get_stock_list_df = {
    'cn': get_cn_stock_list_df,
    'hk': get_hk_stock_list_df,
    'us': get_us_stock_list_df,
}

_market_funcs_get_index_list_df = {
    'cn': get_cn_index_list_df,
    'hk': get_hk_index_list_df,
    'us': get_us_index_list_df,
}

_market_funcs_download_index_daily_df = {
    'cn': download_cn_index_daily,
    'hk': download_cn_index_daily,
    'us': download_us_index_daily,
}

_enabled_markets = ['cn', 'hk', 'us']

def get_supported_market():
    return list(_market_funcs_get_stock_list_df.keys())

def enable_market(markets):
    if len(markets) == 0:
        raise ValueError('Must select at least one market')
    for market in markets:
        if market not in get_supported_market():
            raise ValueError('Market not supported yet: ' + market)
    _enabled_markets = markets

def get_enabled_market():
    return _enabled_markets

def get_all_stock_list_df():
    df = pd.DataFrame([],  columns=['symbol', 'name'])
    for market in _enabled_markets:
        func = _market_funcs_get_stock_list_df[ market ]
        market_df = func()[['symbol', 'name']]
        df = df.append(market_df, ignore_index=True)
    return df.reset_index(drop= True)

def get_all_index_list_df():
    df = pd.DataFrame([],  columns=['symbol', 'name'])
    df = df.append(get_world_index_list_df(), ignore_index= True)
    for market in _enabled_markets:
        func = _market_funcs_get_index_list_df[ market ]
        market_df = func()[['symbol', 'name']]
        df = df.append(market_df, ignore_index=True)
    return df.reset_index(drop= True)

def get_cn_stock_symbol_name():
    return dict_from_df(get_cn_stock_list_df(), 'symbol', 'name')

def get_all_symbol_name():
    symbol_name = dict_from_df(get_all_stock_list_df(), 'symbol', 'name')
    symbol_name.update(dict_from_df(get_all_index_list_df(), 'symbol', 'name'))

    df_cn_fund_list = get_cn_fund_list()
    df_cn_fund_list['fundsymbol'] = 'F.' + df_cn_fund_list['symbol']
    symbol_name.update( dict_from_df(df_cn_fund_list, 'fundsymbol', 'name') )

    return symbol_name

def get_symbol_name_dict(symbols):
    return dict_from_df(download_us_stock_quote(symbols), 'symbol', 'shortName')

def get_symbol_name(symbol):
    symbol_name = get_symbol_name_dict([symbol])
    return symbol_name[ symbol ] if (symbol in symbol_name) else symbol

def symbol_to_name(symbol):
    all_symbol_name = get_all_symbol_name()
    if type(symbol) == str:
        if symbol in all_symbol_name:
            return all_symbol_name[ symbol ]
        else:
            return get_symbol_name(symbol)
    elif type(symbol) == list:
        symbol_name = {}
        other_symbols = []
        for sym in symbol:
            if sym in all_symbol_name:
                symbol_name[ sym ] = all_symbol_name[ sym ]
            else:
                other_symbols.append( sym )
        if len(other_symbols) > 0:
            symbol_name.update( get_symbol_name_dict(other_symbols) )
        return symbol_name
    else:
        raise ValueError('invalid type for symbol: ' + type(symbol))

def get_stockpool_df(symbols):
    if type(symbols) == str:
        if symbols.endswith('.csv'):
            return pd.read_csv(symbols, dtype=str)
        else:
            symbols = symbols.replace(' ','').split(',')
    elif type(symbols) == list:
        pass
    else:
        raise ValueError('Exptected: symbols as .csv, str, or list')

    symbols = symbol_normalize(symbols)

    symbol_name = symbol_to_name(symbols)
    df = pd.DataFrame([], columns=['symbol','name'])
    df['symbol'] = list(symbol_name.keys())
    df['name'] = list(symbol_name.values())
    return df

def get_index_daily( symbol ):
    market = symbol_market( symbol )
    func = _market_funcs_download_index_daily_df[ market ]
    df = get_cached_download_df('cache/market/{param}_1d.csv', download_func= func, param= symbol, check_date= datetime_today())

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace= True, drop= True)
        df = df.astype(float)

    return df

def get_daily( symbol ):
    if symbol.startswith('F.'):
        sym = symbol.replace('F.','')
        df = get_cn_fund_daily( sym )
        df['adj_close'] = df['close'] = df['value']
        df['open'] = df['value'].shift(1)
        df['open'].iloc[0] = df['value'].iloc[0]
        df['high'] = np.maximum(df['open'], df['close'])
        df['low'] = np.minimum(df['open'], df['close'])
        df['volume'] = 1.0
    elif symbol.startswith('sh') or symbol.startswith('sz') or symbol.startswith('^'):
        return get_index_daily( symbol )
    else:
        # we get stock daily from yahoo, including us, cn, hk, etc.
        symbol = symbol_yahoo_style( symbol )
        #func = download_us_stock_daily
        func = download_cn_stock_daily
        df = get_cached_download_df('cache/market/{param}_1d.csv', download_func= func, param= symbol, check_date= datetime_today())

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace= True, drop= True)
        df = df.astype(float)

    return df

def get_market_fund_flow_daily():
    return get_cached_download_df('cache/market/cn_market_ff.csv', download_func= download_cn_market_fund_flow, param= None, check_date= datetime_today())

def get_stock_fund_flow_daily(symbol):
    market = symbol_market( symbol )
    if market == 'cn':
        df = get_cached_download_df('cache/market/{param}_ff.csv', download_func= download_cn_stock_fund_flow, param= symbol, check_date= datetime_today())
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace= True, drop= True)
            df = df.astype(float)
        return df

    else:
        return None

def get_cn_stock_fund_flow_rank(days = '1d'):
    return download_cn_stock_fund_flow_rank(days)

def get_cn_sector_fund_flow_rank(days= '1d', sector= 'industry'):
    return download_cn_sector_fund_flow_rank(days, sector)

def get_stock_spot(symbols, verbose = False):
    cn_symbols = []
    us_symbols = []
    for symbol in symbols:
        market = symbol_market(symbol)
        if market in ['cn', 'hk']:
            cn_symbols.append( symbol )
        elif market in ['us']:
            us_symbols.append( symbol )
    df = pd.DataFrame([], columns=[
            'symbol', 'name',
            'open', 'prevclose',
            'close', 'high', 'low',
            'volume', 
            'date',
        ])
    if len(cn_symbols) > 0:
        cn_df = download_cn_stock_spot(cn_symbols, verbose)
        df = df.append(cn_df, ignore_index= True)
    if len(us_symbols) > 0:
        us_df = download_us_stock_spot(us_symbols, verbose)
        df = df.append(us_df, ignore_index= True)
    return df

def get_finance_balance_report(symbol, check_date= None):
    return get_cached_download_df('cache/finance/{param}_balance.csv', download_finance_balance_report, symbol, check_date= check_date)

def get_finance_income_report(symbol, check_date= None):
    return get_cached_download_df('cache/finance/{param}_income.csv', download_finance_income_report, symbol, check_date= check_date)

def get_finance_cashflow_report(symbol, check_date= None):
    return get_cached_download_df('cache/finance/{param}_cashflow.csv', download_finance_cashflow_report, symbol, check_date= check_date)

def get_finance_abstract_df(symbol, check_date= None):
    abstract_file = 'cache/finance/{}_abstract.csv'.format(symbol)

    if os.path.isfile(abstract_file) and (check_date is None):
        df = pd.read_csv(abstract_file, dtype= str)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace= True, drop= True)
            df = df.astype(float)
    else:
        balance_df = get_finance_balance_report(symbol, check_date= check_date)
        income_df = get_finance_income_report(symbol, check_date= check_date)
        cashflow_df = get_finance_cashflow_report(symbol, check_date= check_date)
        df = extract_abstract_from_report(symbol, balance_df, income_df, cashflow_df)
        df.to_csv(abstract_file, index= not ('date' in df.columns))

    return df

def get_ipoinfo_df(symbol, check_date= None):
    return get_cached_download_df('cache/finance/{param}_ipo.csv', download_ipo, symbol, check_date= check_date)

def get_dividend_history(symbol, check_date= None):
    return get_cached_download_df('cache/finance/{param}_dividend.csv', download_dividend_history, symbol, check_date= check_date)

def create_finance_indicator_df(check_date = None):
    print('Processing finance indicators for all stocks ...')
    symbol_name = get_cn_stock_symbol_name()
    symbols = list( symbol_name.keys() )
    symbols.sort()

    table = []
    cols = None
    i = 0
    n = len(symbols)
    for symbol in symbols:
        i += 1
        name = symbol_name[ symbol ]
        print('\r... {}/{} - {} {} ...'.format(i, n, symbol, name), end='', flush= True)

        abstract_df = get_finance_abstract_df(symbol, check_date= check_date)
        dividend_df = get_dividend_history(symbol, check_date= check_date)
        ipoinfo_df = get_ipoinfo_df(symbol, check_date= None)
        row = extract_finance_indicator_data(symbol, abstract_df, ipoinfo_df, dividend_df)

        if cols is None:
            cols = list( row.keys() )
            cols.append('name')

        row = list(row.values())
        row.append(name)

        table.append( row )

    print('')
    return pd.DataFrame(table, columns= cols)

def get_finance_indicator_df(symbols = None, check_date = None):
    df = get_cached_download_df('cache/cn_stock_indicator.csv', create_finance_indicator_df, param= check_date, check_date = check_date)
    df = df.astype({
        'ipo_years': 'float64',
        '3yr_grow_rate': 'float64',
        'grow_rate': 'float64',
        'grow': 'float64',
        'share_grow': 'float64',
        'start_bvps': 'float64',
        'now_bvps': 'float64',
        'eps': 'float64',
        'roe': 'float64',
        '3yr_roe': 'float64',
        'avg_roe': 'float64',
        'earn_speed': 'float64',
        'earn_yoy': 'float64',
        'debt_ratio': 'float64',
        'cash_ratio': 'float64',
        'earn_ttm': 'float64',
        'assets': 'float64',
        'equity': 'float64',
        'shares': 'float64',
    })
    if symbols is not None:
        df = df[ df['symbol'].isin(symbols) ].reset_index(drop= True)
    return df

def update_finance_indicator_df(symbols):
    indicator_df_file = 'cache/cn_stock_indicator.csv'
    if symbols is None:
        return
    else:
        for symbol in symbols:
            df = get_finance_abstract_df(symbol= symbol, check_date= datetime_today())
        if os.path.isfile(indicator_df_file):
            os.unlink(indicator_df_file)
        return get_finance_indicator_df(symbols)

def get_stock_pepb_history(symbol, check_date = None):
    df = get_cached_download_df('cache/pepb/{param}_pepb.csv', download_stock_pepb_history, param= symbol, check_date = check_date)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace= True, drop= True)
        df = df.astype(float)
    return df

def get_pepb_summary(symbol, check_date= None, years = 10):
    today = datetime_today()
    years_ago = today - dt.timedelta(days= 365 * years)
    df = get_stock_pepb_history(symbol, check_date = check_date)
    if df.shape[0] > 0:
        df = df.loc[ pd.to_datetime(years_ago) : pd.to_datetime(today) ]
        df['pe_ttm'].fillna(method='ffill', inplace=True)
        df['pe_ttm'].fillna(method='bfill', inplace=True)
        df['pb'].fillna(method='ffill', inplace=True)
        df['pb'].fillna(method='bfill', inplace=True)
        pe_list = df['pe_ttm'].tolist()
        pb_list = df['pb'].tolist()
    else:
        pe_list = [ 22.0 ]
        pb_list = [ 1.0 ]

    pe = pe_list[-1]
    pb = pb_list[-1]
    pe_pos = round(sum([1 if i < pe else 0 for i in pe_list]) * 100.0 / len(pe_list), 1)
    pb_pos = round(sum([1 if i < pb else 0 for i in pb_list]) * 100.0 / len(pb_list), 1)
    mean_pe = sum(pe_list) / len(pe_list)
    mean_pb = sum(pb_list) / len(pb_list)
    pe_ratio = round(pe / mean_pe, 3)
    pb_ratio = round(pe / mean_pb, 3)
    pe_list.sort()
    pb_list.sort()
    pe_mid = pe_list[ len(pe_list) // 2 ]
    pb_mid = pb_list[ len(pb_list) // 2 ]

    return {
        'symbol': symbol,
        'pe': pe,
        'pb': pb,
        'pe_mid': pe_mid,
        'pb_mid': pb_mid,
        'pe_pos': pe_pos,
        'pb_pos': pb_pos,
        'pe_ratio': pe_ratio,
        'pb_ratio': pb_ratio,
    }

def create_pepb_symmary_df(symbols= None, years = 10):
    print('Processing PE/PB summary for stocks ...')
    symbol_name = get_cn_stock_symbol_name()
    if symbols is None:
        symbols = list(symbol_name.keys())

    table = []
    cols = None
    for symbol in symbols:
        if symbol not in symbol_name:
            continue
        name = symbol_name[ symbol ]
        row = get_pepb_summary(symbol, check_date = datetime_today(), years= years)
        if cols is None:
            cols = list(row.keys())
            cols.append('name')
        row = list(row.values())
        row.append(name)
        table.append( row )

    return pd.DataFrame(table, columns=cols)

def get_pepb_symmary_df(symbols = None):
    if symbols is None:
        df = get_cached_download_df('cache/cn_stock_pepb.csv', create_pepb_symmary_df, check_date = datetime_today())
        df = df.astype({
            'pe': 'float64',
            'pb': 'float64',
            'pe_pos': 'float64',
            'pb_pos': 'float64',
            'pe_ratio': 'float64',
            'pb_ratio': 'float64',
        })
    else:
        df = create_pepb_symmary_df(symbols)

    return df

def get_macro_bank_interest_rate(country):
    df = get_cached_download_df('cache/bank/{paran}_macro_interest_rate.csv', download_macro_bank_interest_rate, param= country, check_date = datetime_today())
    df['date'] = pd.to_datetime(df.index.date)
    df.set_index('date', inplace=True, drop=True)
    return df

def get_cn_fund_list(check_date= None):
    df = get_cached_download_df('cache/cn_fund_list.csv', download_cn_fund_list, check_date= check_date)
    df.columns = ['symbol', 'name', 'val_1', 'cumval_1', 'val_2', 'cumval_2', 'val_change', 'pct_change', 'buy_state', 'sell_state', 'fee']
    return df

def get_cn_etf_list(check_date= None):
    df = get_cached_download_df('cache/cn_etf_list.csv', download_cn_etf_fund_list, check_date= check_date)
    df.columns = ['symbol', 'name', 'val_1', 'cumval_1', 'val_2', 'cumval_2', 'val_change', 'pct_change', 'buy_state', 'sell_state', 'fee']
    return df

def get_cn_fund_daily(symbol, check_date= None):
    df = get_cached_download_df('cache/fund/{param}_1d.csv', download_func= download_cn_fund_info, param= symbol, check_date= check_date)
    df.columns = ['date', 'value', 'pct_change']
    df = df.astype({
        'date': 'datetime64[s]',
        'value': 'float64',
        'pct_change': 'float64',
    })
    df = df.set_index('date', drop= True)
    return df

def get_cn_etf_daily(symbol, check_date= None):
    df = get_cached_download_df('cache/fund/{param}_1d.csv', download_func= download_cn_etf_fund_info, param= symbol, check_date= check_date)
    df.columns = ['date', 'value', 'pct_change']
    df = df.astype({
        'date': 'datetime64[s]',
        'value': 'float64',
        'pct_change': 'float64',
    })
    df = df.set_index('date', drop= True)
    return df

def get_cn_fund_manager(check_date= None):
    df = get_cached_download_df('cache/cn_fund_manager.csv', download_cn_fund_manager, check_date= check_date)
    df.columns = ['index', 'name', 'company', 'fund', 'days', 'size', 'best_return']
    df = df.drop(columns=['index'])
    df = df.astype({
        'days': 'float64',
        'size': 'float64',
        'best_return': 'float64',
    })
    return df

def get_cn_fund_company(check_date= None):
    df = get_cached_download_df('cache/cn_fund_company.csv', download_cn_fund_company, check_date= check_date)
    df.columns = ['index', 'company', 'company_start', 'size', 'funds', 'managers', 'update_date']
    df = df.drop(columns=['index'])
    df = df.astype({
        'size': 'float64',
        'funds': 'int',
        'managers': 'int',
    })
    df['company_start'] = pd.to_datetime(df['company_start']).dt.date
    df['size'] = df['size'].fillna(0)
    for k in ['有限公司','有限责任公司','管理','资产','股份']:
        df['company'] = df['company'].str.replace(k, '')
    return df
