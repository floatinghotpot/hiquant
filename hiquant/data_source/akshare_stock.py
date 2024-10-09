import datetime
import time
import pandas as pd
import akshare as ak

def download_cn_stock_spot( symbols, verbose= False):
    # sina_symbols = []
    # for symbol in symbols:
    #     if (len(symbol) == 6) and symbol[0].isdigit():
    #         if symbol[0] == '6':
    #             sina_symbols.append( 'sh' + symbol )
    #         elif symbol[0] in ['0','3']:
    #             sina_symbols.append( 'sz' + symbol )
    #         elif symbol[0] in ['8']:
    #             sina_symbols.append( 'bj' + symbol )
    #     elif (len(symbol) == 5) and symbol[0].isdigit():
    #         sina_symbols.append( 'hk' + symbol )
    #     elif symbol[:2].capitalize() == 'HK':
    #         sina_symbols.append( 'hk0' + symbol[-4:] )

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
    
