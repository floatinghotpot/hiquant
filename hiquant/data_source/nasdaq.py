# -*- coding: utf-8; py-indent-offset:4 -*-

import requests
import pandas as pd

_EXCHANGE_LIST = ['nyse', 'nasdaq', 'amex']

_REGIION_LIST = ['AFRICA','EUROPE','ASIA','AUSTRALIA+AND+SOUTH+PACIFIC','CARIBBEAN','SOUTH+AMERICA','MIDDLE+EAST','NORTH+AMERICA']

_SECTORS_LIST = ['Consumer Non-Durables', 'Capital Goods', 'Health Care',
       'Energy', 'Technology', 'Basic Industries', 'Finance',
       'Consumer Services', 'Public Utilities', 'Miscellaneous',
       'Consumer Durables', 'Transportation']

# headers and params used to bypass NASDAQ's anti-scraping mechanism in function __exchange2df
nasdaq_headers = {
    'authority': 'api.nasdaq.com',
    'accept': 'application/json, text/plain, */*',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'origin': 'https://www.nasdaq.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.nasdaq.com/',
    'accept-language': 'en-US,en;q=0.9',
}

def stocks_params(exchange):
    return (
        ('letter', '0'),
        ('exchange', exchange),
        ('download', 'true'),
    )

#
# Data source: exchange = nyse, nasdaq, amex
# https://api.nasdaq.com/api/screener/stocks?exchange=nasdaq&download=true
#
def download_us_stock_list(param = None, verbose = False):
    if param is not None:
        print('\rfetching data from nasdaq ...', end = '', flush = True)
        r = requests.get('https://api.nasdaq.com/api/screener/stocks', headers=nasdaq_headers, params=stocks_params(param))
        print('\r', end = '', flush = True)
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

def index_params(offset):
    return (
        ('letter', '0'),
        ('offset', offset),
        ('download', 'true'),
    )

#
# Data source:
# https://api.nasdaq.com/api/screener/index?offset=0&limit=50
#
def download_us_index_list(param = None, verbose = False):
    df = None
    offset = 0
    for i in range(10):
        print('\rfetching data from nasdaq ...', end = '', flush = True)
        r = requests.get('https://api.nasdaq.com/api/screener/index', headers=nasdaq_headers, params=index_params(offset))
        print('\r', end = '', flush = True)
        records = r.json()['data']['records']
        totalRecords = int(records['totalrecords'])
        data = records['data']
        if df is None:
            df = pd.DataFrame(data['rows'], columns=data['headers'])
        else:
            df = df.append( pd.DataFrame(data['rows'], columns=data['headers']) , ignore_index= True)
        offset = int(records['offset']) + int(records['limit'])
        if offset > totalRecords:
            break
    df.columns = ['symbol', 'name', 'price', 'netchange', 'pctchange']
    df = df.sort_values(by='symbol').reset_index(drop=True)
    if verbose:
        print(df)
    return df

