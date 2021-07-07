# -*- coding: utf-8; py-indent-offset:4 -*-

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
