# -*- coding: utf-8; py-indent-offset:4 -*-

import requests
import datetime
import time
import io
import pandas as pd
import yfinance as yf

from ..utils import symbol_yahoo_style

def download_us_stock_spot( symbols, verbose= False):

    pass

def download_us_stock_daily( symbol, start= None, end= None, interval= '1d' ):
    stock = yf.Ticker(symbol)
    df = stock.history(period='3mo')
    return df
    pass
