
import os
import datetime as dt
import pandas as pd

from ..utils import get_file_modify_time, datetime_today
from ..data_source import *
from .symbol import symbol_normalize

def get_cached_download_df(csv_file, download_func, param = None, check_date = False):
    if type(param) == str:
        csv_file = csv_file.replace('{param}', param)

    # like ^GSPC.csv, will cause trouble when manually delete
    csv_file = csv_file.replace('^','_').replace('$','_')

    need_update = False
    if os.path.isfile(csv_file):
        if check_date:
            modified_time = get_file_modify_time(csv_file)
            need_update = modified_time < datetime_today()
        else:
            need_update = False
    else:
        need_update = True

    if need_update:
        df = download_func(param)
        df.to_csv(csv_file, index= bool(df.index.name))
    else:
        df = pd.read_csv(csv_file, dtype=str)

    return df

def get_cn_stock_list_df(force_update= False):
    return get_cached_download_df('cache/cn_stock_list.csv', download_cn_stock_list, check_date= force_update)

def get_hk_stock_list_df(force_update= False):
    return get_cached_download_df('cache/hk_stock_list.csv', download_hk_stock_list, check_date= force_update)

def get_us_stock_list_df(force_update= False):
    return get_cached_download_df('cache/us_stock_list.csv', download_us_stock_list, check_date= force_update)

def get_cn_index_list_df(force_update= False):
    return get_cached_download_df('cache/cn_index_list.csv', download_cn_index_list, check_date= force_update)

def get_hk_index_list_df(force_update= False):
    return get_cached_download_df('cache/hk_index_list.csv', download_hk_index_list, check_date= force_update)

def get_us_index_list_df(force_update= False):
    return get_cached_download_df('cache/us_index_list.csv', download_us_index_list, check_date= force_update)

def get_world_index_list_df(force_update= False):
    return get_cached_download_df('cache/world_index_list.csv', download_world_index_list, check_date= force_update)

_market_funcs_get_stock_df = {
    'cn': get_cn_stock_list_df,
    'hk': get_hk_stock_list_df,
    'us': get_us_stock_list_df,
}

_market_funcs_get_index_df = {
    'cn': get_cn_index_list_df,
    'hk': get_hk_index_list_df,
    'us': get_us_index_list_df,
}

_market_funcs_download_stock_daily_df = {
    'cn': download_cn_stock_daily,
    'hk': download_cn_stock_daily,
    'us': download_us_stock_daily,
}

_market_funcs_download_index_daily_df = {
    'cn': download_cn_index_daily,
    'hk': download_cn_index_daily,
    'us': download_us_index_daily,
}

_enabled_markets = ['cn', 'hk', 'us']

def get_supported_market():
    return list(_market_funcs_get_stock_df.keys())

def enable_market(markets):
    if len(markets) == 0:
        raise ValueError('Must select at least one market')
    for market in markets:
        if market not in get_supported_market():
            raise ValueError('Market not supported yet: ' + market)
    _enabled_markets = markets

def get_enabled_market():
    return _enabled_markets

def get_all_stock_list_df(force_update= False):
    df = pd.DataFrame([],  columns=['symbol', 'name'])
    for market in _enabled_markets:
        func = _market_funcs_get_stock_df[ market ]
        market_df = func(force_update= force_update)[['symbol', 'name']]
        df = df.append(market_df, ignore_index=True)
    return df.reset_index(drop= True)

def get_all_index_list_df(force_update= False):
    df = pd.DataFrame([],  columns=['symbol', 'name'])
    df = df.append(get_world_index_list_df(), ignore_index= True)
    for market in _enabled_markets:
        func = _market_funcs_get_index_df[ market ]
        market_df = func(force_update= force_update)[['symbol', 'name']]
        df = df.append(market_df, ignore_index=True)
    return df.reset_index(drop= True)

def get_cn_stock_symbol_name():
    return dict_from_df(get_cn_stock_list_df(), 'symbol', 'name')

def get_all_symbol_name():
    symbol_name = dict_from_df(get_all_stock_list_df(), 'symbol', 'name')
    symbol_name.update(dict_from_df(get_all_index_list_df(), 'symbol', 'name'))
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

def symbol_market( symbol ):
    if (len(symbol) == 6) and symbol[0].isdigit(): # 600036
        return 'cn'
    elif symbol.startswith('sh') or symbol.startswith('sz'): # sh000300, index
        return 'cn'
    elif (len(symbol) == 5) and symbol[0].isdigit(): # 00700
        return 'hk'
    else:
        return 'us'

def get_index_daily( symbol ):
    market = symbol_market( symbol )
    func = _market_funcs_download_index_daily_df[ market ]
    df = get_cached_download_df('cache/market/{param}_1d.csv', download_func= func, param= symbol, check_date= True)

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace= True, drop= True)
        df = df.astype(float)

    return df

def get_daily( symbol ):
    market = symbol_market( symbol )
    func = _market_funcs_download_stock_daily_df[ market ]
    df = get_cached_download_df('cache/market/{param}_1d.csv', download_func= func, param= symbol, check_date= True)

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace= True, drop= True)
        df = df.astype(float)

    return df

def get_daily_adjust_factor( symbol ):
    market = symbol_market( symbol )
    if market in ['cn', 'hk']:
        df = get_cached_download_df('cache/market/{param}_1d_f.csv', download_func= download_stock_daily_adjust_factor, param= symbol, check_date= True)
    else:
        df = get_daily( symbol ).copy()
        df['factor'] = df['adj_close'] / df['close']
        df['factor'] = df['factor'] / df.iloc[0]['factor']
        df = df[['factor']]

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace= True, drop= True)
        df = df.astype(float)

    return df

def adjust_daily_with_factor(daily_df, factor_df, adjust: str = 'qfq'):
    if adjust == 'qfq':
        factor_df = factor_df.copy()
        max_date_factor = factor_df.iloc[-1]['factor']
        factor_df['factor'] = factor_df['factor'] / max_date_factor

    if 'factor' in daily_df.columns:
        del daily_df['factor']

    daily_df = pd.merge(
        daily_df, factor_df, left_index=True, right_index=True, how="outer"
    )
    daily_df.fillna(method="ffill", inplace=True)
    daily_df = daily_df.astype(float)
    daily_df.dropna(inplace=True)
    daily_df.drop_duplicates(subset=["open", "high", "low", "close", "volume"], inplace=True)
    daily_df["open"] = daily_df["open"] * daily_df["factor"]
    daily_df["high"] = daily_df["high"] * daily_df["factor"]
    daily_df["close"] = daily_df["close"] * daily_df["factor"]
    daily_df["low"] = daily_df["low"] * daily_df["factor"]
    daily_df["open"] = round(daily_df["open"], 2)
    daily_df["high"] = round(daily_df["high"], 2)
    daily_df["low"] = round(daily_df["low"], 2)
    daily_df["close"] = round(daily_df["close"], 2)
    daily_df.dropna(inplace=True)

    return daily_df

def adjust_daily(symbol, daily_df, adjust: str = 'hfq'):
    factor_df = get_daily_adjust_factor( symbol )
    return adjust_daily_with_factor(daily_df, factor_df, adjust)

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

def get_finance_balance_report(symbol, force_update= False):
    return get_cached_download_df('cache/finance/{param}_balance.csv', download_finance_balance_report, symbol, check_date= force_update)

def get_finance_income_report(symbol, force_update= False):
    return get_cached_download_df('cache/finance/{param}_income.csv', download_finance_income_report, symbol, check_date= force_update)

def get_finance_cashflow_report(symbol, force_update= False):
    return get_cached_download_df('cache/finance/{param}_cashflow.csv', download_finance_cashflow_report, symbol, check_date= force_update)

def create_finance_abstract_df(symbol, force_update= False):
    balance_df = get_finance_balance_report(symbol, force_update= force_update)
    income_df = get_finance_income_report(symbol, force_update= force_update)
    cashflow_df = get_finance_cashflow_report(symbol, force_update= force_update)
    return extract_abstract_from_report(symbol, balance_df, income_df, cashflow_df)

def get_finance_abstract_df(symbol, force_update= False):
    df = get_cached_download_df('cache/finance/{param}_abstract.csv', create_finance_abstract_df, symbol, check_date= force_update)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace= True, drop= True)
        df = df.astype(float)
    return df

def get_ipoinfo_df(symbol, force_update= False):
    return get_cached_download_df('cache/finance/{param}_ipo.csv', download_ipo, symbol, check_date= force_update)

def get_dividend_history(symbol, force_update= False):
    return get_cached_download_df('cache/finance/{param}_dividend.csv', download_dividend_history, symbol, check_date= force_update)

def get_finance_indicator(symbol, force_update= False):
    abstract_df = get_finance_abstract_df(symbol, force_update= force_update)
    ipoinfo_df = get_ipoinfo_df(symbol, force_update= force_update)
    dividend_df = get_dividend_history(symbol, force_update= force_update)
    return extract_finance_indicator_data(symbol, abstract_df, ipoinfo_df, dividend_df)

def get_finance_indicator_df(symbols = None, force_update= False):
    symbol_name = get_cn_stock_symbol_name()
    table = []
    cols = None
    i = 0
    n = len(symbols)
    for symbol in symbols:
        name = symbol_name[ symbol ]
        i += 1
        print('\r... {}/{} - {} {} ...'.format(i, n, symbol, name), end='', flush= True)
        row = get_finance_indicator(symbol, force_update= force_update)
        if cols is None:
            cols = list( row.keys() )
            cols.append('name')
        row = list(row.values())
        row.append(name)
        table.append( row )
    print('')
    return pd.DataFrame(table, columns= cols)

def get_finance_indicator_all(force_update= False):
    symbol_name = get_cn_stock_symbol_name()
    all_symbols = symbol_name.keys()
    print('Processing finance indicators for all stocks ...')
    df = get_cached_download_df('cache/cn_stock_indicator.csv', get_finance_indicator_df, param= all_symbols, check_date = force_update)
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
        'debt_ratio': 'float64',
        'cash_ratio': 'float64',
        'earn_ttm': 'float64',
        'assets': 'float64',
        'equity': 'float64',
        'shares': 'float64',
    })
    return df

def get_stock_pepb_history(symbol, force_update= False):
    df = get_cached_download_df('cache/pepb/{param}_pepb.csv', download_stock_pepb_history, param= symbol, check_date= force_update)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace= True, drop= True)
        df = df.astype(float)
    return df

def get_pepb_summary(symbol, force_update= False, years = 10):
    today = datetime_today()
    years_ago = today - dt.timedelta(days= 365 * years)
    df = get_stock_pepb_history(symbol, force_update= force_update)
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

    return {
        'symbol': symbol,
        'pe': pe,
        'pb': pb,
        'pe_pos': pe_pos,
        'pb_pos': pb_pos,
        'pe_ratio': pe_ratio,
        'pb_ratio': pb_ratio,
    }

def get_pepb_symmary_df(symbols, force_update= False, years = 10):
    symbol_name = get_cn_stock_symbol_name()
    table = []
    cols = None
    for symbol in symbols:
        name = symbol_name[ symbol ]
        row = get_pepb_summary(symbol, force_update= force_update, years= years)
        if cols is None:
            cols = list(row.keys())
            cols.append('name')
        row = list(row.values())
        row.append(name)
        table.append( row )
    return pd.DataFrame(table, columns=cols)

def get_pepb_symmary_all(force_update= False):
    symbol_name = get_cn_stock_symbol_name()
    all_symbols = symbol_name.keys()
    print('Processing PE/PB summary for all stocks ...')
    df = get_cached_download_df('cache/cn_stock_pepb.csv', get_pepb_symmary_df, symbols= all_symbols, check_date = force_update)
    df = df.astype({
        'pe': 'float64',
        'pb': 'float64',
        'pe_pos': 'float64',
        'pb_pos': 'float64',
        'pe_ratio': 'float64',
        'pb_ratio': 'float64',
    })
    return df

def get_macro_bank_interest_rate(country, force_update= False):
    df = get_cached_download_df('cache/bank/{paran}_macro_interest_rate.csv', download_macro_bank_interest_rate, param= country, check_date = force_update)
    df['date'] = pd.to_datetime(df.index.date)
    df.set_index('date', inplace=True, drop=True)
    return df
