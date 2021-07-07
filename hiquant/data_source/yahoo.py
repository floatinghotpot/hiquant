# -*- coding: utf-8; py-indent-offset:4 -*-

import requests
import datetime
import time
import pandas as pd
import io

# headers and params used to bypass NASDAQ's anti-scraping mechanism in function __exchange2df
yahoo_headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    #'origin': 'https://finance.yahoo.com',
    #'referer': 'https://finance.yahoo.com/',
    #'accept-language': 'en-US,en;q=0.9',
}

#
# Data source:
# https://query1.finance.yahoo.com/v7/finance/download/0700.HK?period1=1594019968&period2=1625555968&interval=1d&events=history&includeAdjustedClose=true
#
def download_us_stock_daily( symbol, start= None, end= None, interval= '1d', adjust= '' ):
    if start is None:
        start = '2000-01-01'

    if isinstance(start, datetime.datetime):
        start = int(time.mktime(start.timetuple()))
    else:
        start = int(time.mktime(time.strptime(str(start), '%Y-%m-%d')))
    if end is None:
        end = int(time.time())
    elif isinstance(end, datetime.datetime):
        end = int(time.mktime(end.timetuple()))
    else:
        end = int(time.mktime(time.strptime(str(end), '%Y-%m-%d')))

    url_template = 'https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval={}&events=history&includeAdjustedClose=true'
    url = url_template.format(symbol, start, end, interval)

    print('\rfetching history data {} ...'.format(symbol), end = '', flush = True)
    r = requests.get(url, headers= yahoo_headers)
    print('')

    if 'Will be right back' in r.text:
        raise RuntimeError("*** YAHOO! FINANCE IS CURRENTLY DOWN! ***.")

    df = pd.read_csv(io.StringIO(r.text))
    df.columns = ['date', 'open', 'high', 'low', 'close', 'adj_close', 'volume']
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date', drop= True)
    return df

def download_us_index_daily( symbol ):
    return download_us_stock_daily(symbol)

#
# Data source:
# https://query1.finance.yahoo.com/v7/finance/quote?symbols=^GSPC,AAPL,0700.HK,000300.SS
#
def download_us_stock_quote(symbols, verbose = False):
    url_template = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols={}'
    url = url_template.format(','.join(symbols))

    print('\rfetching quote data ...', end = '', flush = True)
    r = requests.get(url, headers= yahoo_headers)
    print('')

    if 'Will be right back' in r.text:
        raise RuntimeError("*** YAHOO! FINANCE IS CURRENTLY DOWN! ***.")
    data = r.json()['quoteResponse']['result']
    return pd.DataFrame(data, columns=data[0].keys()) if (len(data) > 0) else pd.DataFrame()

def download_us_stock_spot(symbols, verbose = False):
    if len(symbols) > 100:
        df = pd.DataFrame()
        for i in range(0, len(symbols), 100):
            page = symbols[i:i+100]
            page_df = download_us_stock_spot(page)
            df = df.append(page_df, ignore_index=True)
        return df
    else:
        df = download_us_stock_quote(symbols, verbose= verbose)
        df['date'] = pd.to_datetime(df['regularMarketTime'], unit='s').dt.normalize()
        selected_columns = {
            'symbol': 'symbol',
            'shortName': 'name',
            'regularMarketOpen': 'open',
            'regularMarketPreviousClose': 'prevclose',
            'regularMarketPrice': 'close',
            'regularMarketDayHigh': 'high',
            'regularMarketDayLow': 'low',
            'regularMarketVolume': 'volume',
            'date': 'date',
        }
        df = df[ list(selected_columns.keys()) ].rename(columns= selected_columns)
        return df

def download_world_index_list(param= None, verbose = False):
    symbols = '''^BSESN
^NSEI
^DJI
^IXIC
^N225
^HSI
^AXJO
^TWII
^STI
000001.SS
399001.SZ
^JKSE
^KS11
^GSPC
^DJI
^AORD
^KLSE
^XAX
^RUT
^VIX
^GSPTSE
^FTSE
^GDAXI
^FCHI
^STOXX50E
^N100
^BFX
IMOEX.ME
^BVSP
^MXX
^IPSA
^MERV
^TA125.TA
^CASE30
^JN0U.JO
^NZ50'''.split('\n')
    df = download_us_stock_quote(symbols)
    df = df[['symbol','shortName','exchange','market','currency','region','language']]
    df = df.rename(columns={'shortName':'name'})
    return df

#
# Data source:
# https://query1.finance.yahoo.com/v7/finance/spark?symbols=%5EAORD&range=1d&interval=5m&indicators=close&includeTimestamps=false&includePrePost=false&corsDomain=in.finance.yahoo.com&.tsrc=finance
#
def download_us_stock_spark(symbol, verbose= False):
    pass
