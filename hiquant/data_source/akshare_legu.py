# -*- coding: utf-8; py-indent-offset:4 -*-

import time
import akshare as ak

def download_stock_pepb_history(symbol):
    print('\tfetching pe/pb data ...', symbol)
    df = ak.stock_a_lg_indicator(symbol)
    time.sleep(1)
    df = df.rename(columns={"trade_date":"date"}).sort_values(by='date')
    return df

