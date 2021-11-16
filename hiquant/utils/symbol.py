# -*- coding: utf-8; py-indent-offset:4 -*-

import pandas as pd

'''
symbol rule:

for China user (name in Chinese):
    China mainland market:
        stock: 6 digits, like 600036, 000002, 300357
        index: sh/sz + 6 digits, like sh000300
    Hongkong market:
        stock: 5 digits, like 00700, 09988
        any symbol like 'hk0700' or 'hk00700' will be converted to 00700

for US user (name in English):
    China mainland market:
        stock & index: 6 digits + exchange, like 600036.SS, 000002.SZ
    Hongkong market:
        stock: 4 digits + exchange, like 0700.HK
    US market:
        stock: like AAPL, AMZN, MSFT
        index: like ^GSPC

'''

def symbol_market( symbol ):
    if (len(symbol) == 6) and symbol[0].isdigit(): # 600036, 000002, 300357
        return 'cn'
    elif symbol.startswith('sh') or symbol.startswith('sz'): # sh000300, sz399001, index
        return 'cn'
    elif (len(symbol) == 5) and symbol[0].isdigit(): # 00700
        return 'hk'
    else:
        return 'us'

def symbol_normalize(symbol):
    if type(symbol) == str:
        if symbol[:2] in ['hk','HK','Hk','hK']:
            return '0' + symbol[-4:]
        else:
            return symbol
    elif type(symbol) == list:
        return [symbol_normalize(sym) for sym in symbol]
    else:
        raise ValueError('invalid symbol type: ' + type(symbol))

def symbol_yahoo_style(symbol):
    if (len(symbol) == 6) and symbol[0].isdigit():
        if symbol[0] in ['0','3']: # 000002, 300357
            return symbol + '.SZ'
        elif symbol[0] in ['6']: # 600036
            return symbol + '.SS'
        else:
            raise ValueError('invalid symbol: ' + symbol)
    elif symbol.startswith('sh'): # sh000300, shanghai index
        return symbol[-6:] + '.SS'
    elif symbol.startswith('sz'): # sz399001, shenzhen index
        return symbol[-6:] + '.SZ'
    elif (len(symbol) == 5) and symbol[0].isdigit(): # 00700
        return symbol[-4:] + '.HK'
    else:
        return symbol

def symbols_from_params(params):
    symbols = []
    for param in params:
        if param.endswith('.csv'):
            symbols += pd.read_csv(param, dtype=str)['symbol'].tolist()
        elif param.endswith('.xlsx'):
            symbols += pd.read_excel(param, dtype=str)['symbol'].tolist()
        elif ',' in param:
            symbols += param.split(',')
        else:
            symbols.append(param)
    return list(set(symbols))
