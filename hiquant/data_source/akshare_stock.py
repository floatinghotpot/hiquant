import datetime
import time
import pandas as pd
import akshare as ak

def download_cn_stock_list(param= None, verbose= False):
    df = ak.stock_info_a_code_name()
    df.columns = ['symbol', 'name']
    if verbose:
        print(df)
    return df

def download_cn_index_list(param, verbose = False):
    df = ak.index_stock_info()
    df.columns = ['symbol','name','publish_date']
    df['symbol'] = df['symbol'].apply(lambda x: 'sh'+x if (x[0]=='0') else 'sz'+x)
    df = df[['symbol', 'name']]

    if verbose:
        print(df)
    return df

def download_cn_index_stocks_list(symbol, verbose = False):
    if symbol.startswith('sh') or symbol.startswith('sz'):
        symbol = symbol[2:]
        df = ak.index_stock_cons(index= symbol)
        df.columns = ['symbol','name','publish_date']
        df = df[['symbol', 'name']]
        if verbose:
            print(df)
        return df
    else:
        raise ValueError('unknown index: ' + symbol)

def download_cn_index_spot( symbols= None, verbose= False):
    # use eastmoney instead of sina, much faster
    #df = ak.stock_zh_index_spot_sina()
    df = ak.stock_zh_index_spot_em(symbol='指数成份')
    df = df.sort_values(by='代码', ascending=True).reset_index(drop= True)
    df = df[['代码','名称','今开','昨收','最新价','最高','最低','成交量']]
    df = df.rename(columns={
        '代码':'symbol',
        '名称':'name',
        '今开':'open',
        '昨收':'prevclose',
        '最新价':'close',
        '最高':'high',
        '最低':'low',
        '成交量':'volume'
        })
    #print( tb.tabulate(df, headers='keys') )
    return df

def download_cn_index_daily( symbol ):
    daily_df = ak.stock_zh_index_daily_tx(symbol = symbol)
    #print(daily_df.index)
    #daily_df['date'] = pd.to_datetime(daily_df.index.date)
    daily_df['volume'] = daily_df['amount']
    daily_df.set_index('date', inplace=True, drop=True)
    return daily_df

def download_cn_stock_spot( symbols, verbose= False):
    # use eastmoney instead of sina, much faster
    #df = ak.stock_zh_a_spot()
    df = ak.stock_zh_a_spot_em()
    df = df[['代码','名称','今开','昨收','最新价','最高','最低','成交量']]
    df = df.rename(columns={
        '代码':'symbol',
        '名称':'name',
        '今开':'open',
        '昨收':'prevclose',
        '最新价':'close',
        '最高':'high',
        '最低':'low',
        '成交量':'volume'
        })
    return df

def download_cn_stock_daily( symbol, start= None, end= None, interval= '1d'):
    if start is None:
        start = '2000-01-01'
    if isinstance(start, str):
        start = datetime.date.fromisoformat(start)
    if isinstance(start, datetime.date):
        start = start.strftime('%Y%m%d')

    if end is None:
        end = datetime.date.today()
    if isinstance(end, str):
        end = datetime.date.fromisoformat(end)
    if isinstance(end, datetime.date):
        end = end.strftime('%Y%m%d')

    period = 'daily'

    print('\rfetching history data {} ...'.format(symbol))
    daily_df = ak.stock_zh_a_hist( symbol=symbol, period=period, start_date=start, end_date=end )
    daily_df = daily_df[['日期','股票代码','开盘','收盘','最高','最低','成交量']]
    #print(daily_df)

    hfq_df = ak.stock_zh_a_hist( symbol=symbol, period=period, start_date=start, end_date=end, adjust='hfq' )
    hfq_df = hfq_df[['日期','股票代码','开盘','收盘','最高','最低','成交量']]
    #print(hfq_df)

    df = pd.concat([daily_df, hfq_df['收盘'].rename('adj_close')], axis=1)
    #print(df)
    df = df.rename(columns={
        '日期':'date',
        '股票代码':'symbol',
        '开盘':'open',
        '收盘':'close',
        '最高':'high',
        '最低':'low',
        '成交量':'volume'
    })
    #print(df)
    df['factor'] = df['adj_close'] / df['close']
    return df
    
def download_hk_stock_list(param= None, verbose= False):
    df = ak.stock_hk_spot()
    # columns: symbol, name, engname, tradetype, lasttrade, prevclose, open, high, low, volume, amount, ticktime, buy, sell, pricechange, changepercent
    df = df[['symbol', 'name']]
    if verbose:
        print(df)
    return df

# TODO:
def download_hk_index_list(param, verbose = False):
    df = pd.DataFrame([], columns=['symbol','name'])
    # TODO:
    return df

'''
def download_cn_index_daily( symbol ):
    daily_df = ak.stock_zh_index_daily(symbol = symbol)
    daily_df['date'] = pd.to_datetime(daily_df.index.date)
    daily_df.set_index('date', inplace=True, drop=True)
    return daily_df
'''
'''
def _download_cn_stock_daily( symbol, adjust = '' ):
    start = '20000101'
    end = dt.datetime.now().strftime('%Y%m%d')

    if len(symbol) == 5:
        df = ak.stock_hk_daily(symbol=symbol, adjust = adjust)
        time.sleep( _SINA_DOWNLOAD_DELAY )
        df.index = df.index.set_names('date')
    elif len(symbol) == 6:
        if symbol[0] == '6':
            symbol = 'sh' + symbol
        elif symbol[0] in ['0','3']:
            symbol = 'sz' + symbol
        df = ak.stock_zh_a_daily(symbol=symbol, start_date=start, end_date=end, adjust = adjust)
        time.sleep( _SINA_DOWNLOAD_DELAY )
    else:
        raise ValueError('unknown symbol: ' + symbol)

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace= True, drop= True)
        df = df.astype(float)

    df.sort_index(ascending=True, inplace=True)

    # drop invalid data
    if 'close' in df.columns:
        df = df[df['close'] > 0.01]

    return df

def _download_stock_daily_adjust_factor( symbol, adjust ):
    df = _download_cn_stock_daily( symbol, adjust )
    if len(symbol) == 6:
        df.columns = ['factor']
    elif len(symbol) == 5:
        df.columns = ['factor', 'cash']
    else:
        raise ValueError('unknown symbol: ' + symbol)
    return df[['factor']]

#
# download cn stock daily from yahoo is more efficient
# (1) yahoo will not block IP
# (2) yahoo provide adj_close with close, easier to calc adjust factor
#
def download_cn_stock_daily( symbol ):
    print('\rfetching history data {} ...'.format(symbol))
    daily_df = _download_cn_stock_daily( symbol )
    factor_df = _download_stock_daily_adjust_factor( symbol, 'hfq-factor' )
    df = pd.merge(
        daily_df, factor_df, left_index=True, right_index=True, how='outer'
    )
    df = df.fillna(method='ffill').astype(float).dropna().drop_duplicates(subset=['open', 'high', 'low', 'close', 'volume'])
    df['factor'] = df['factor'] / df['factor'].iloc[-1]
    df['adj_close'] = df['close'] * df['factor']
    return df
'''
