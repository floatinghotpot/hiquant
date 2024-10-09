# -*- coding: utf-8; py-indent-offset:4 -*-

import time
import datetime as dt
import pandas as pd
import akshare as ak

def download_cn_index_daily( symbol ):
    daily_df = ak.stock_zh_index_daily_tx(symbol = symbol)
    #print(daily_df.index)
    #daily_df['date'] = pd.to_datetime(daily_df.index.date)
    daily_df['volume'] = daily_df['amount']
    daily_df.set_index('date', inplace=True, drop=True)
    return daily_df
