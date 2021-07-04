# -*- coding: utf-8; py-indent-offset:4 -*-

import time
import requests
import datetime as dt
import pandas as pd
import yfinance as yf

from ..utils import *

_EXCHANGE_LIST = ['nyse', 'nasdaq', 'amex']

_REGIION_LIST = ['AFRICA','EUROPE','ASIA','AUSTRALIA+AND+SOUTH+PACIFIC','CARIBBEAN','SOUTH+AMERICA','MIDDLE+EAST','NORTH+AMERICA']

_SECTORS_LIST = ['Consumer Non-Durables', 'Capital Goods', 'Health Care',
       'Energy', 'Technology', 'Basic Industries', 'Finance',
       'Consumer Services', 'Public Utilities', 'Miscellaneous',
       'Consumer Durables', 'Transportation']

# headers and params used to bypass NASDAQ's anti-scraping mechanism in function __exchange2df
headers = {
    'authority': 'api.nasdaq.com',
    'accept': 'application/json, text/plain, */*',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'origin': 'https://www.nasdaq.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.nasdaq.com/',
    'accept-language': 'en-US,en;q=0.9',
}

def params(exchange):
    return (
        ('letter', '0'),
        ('exchange', exchange),
        ('download', 'true'),
    )

def params_region(region):
    return (
        ('letter', '0'),
        ('region', region),
        ('download', 'true'),
    )

def download_us_stock_list(param = None, verbose = False):
    if param is not None:
        r = requests.get('https://api.nasdaq.com/api/screener/stocks', headers=headers, params=params(param))
        data = r.json()['data']
        df = pd.DataFrame(data['rows'], columns=data['headers'])
    else:
        df = pd.DataFrame()
        for exchange in _EXCHANGE_LIST:
            ex_df = download_us_stock_list(exchange, verbose)
            df = df.append(ex_df, ignore_index=True)
    # removes weird tickers
    df = df[~df['symbol'].str.contains(r'\.|\^', regex=True)]
    df = df.sort_values(by='symbol').reset_index(drop=True)
    if verbose:
        print(df)
    return df

def download_us_stock_daily( symbol, adjust = '' ):
    df = yf.download(symbol, start='2000-01-01', period='1d')
    df.columns = ['open', 'high', 'low', 'close', 'adj_close', 'volume']
    df.index.name = 'date'
    return df

# TODO: donwload us index list
def download_us_index_list(param = None, verbose = False):
    df = pd.DataFrame([], columns=['symbol', 'name'])

    # TODO:

    return df

# TODO: donwload us index daily
def download_us_index_daily( symbol ):
    df = pd.DataFrame([], columns=['open', 'high', 'low', 'close', 'adj_close', 'volume'])

    # TODO:

    return df
