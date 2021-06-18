# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant import *

def test_stock():
    date_start = date_from_str('3 years ago')
    date_end = date_from_str('yesterday')
    market = Market(date_start, date_end)

    df = market.get_daily('600036')

    stock = Stock('600036', '招商银行', df)
    stock.add_indicator(['macd', 'kdj', 'ma'], inplace= True)
    stock.plot(out_file = 'output/test_stock.png')
