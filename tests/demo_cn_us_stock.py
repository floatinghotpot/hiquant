# -*- coding: utf-8; py-indent-offset:4 -*-
import pandas as pd
import talib
import hiquant as hq

class StrategyMacd( hq.BasicStrategy ):
    def __init__(self, fund):
        super().__init__(fund, __file__)

    def gen_trade_signal(self, symbol, init_data = False):
        market = self.fund.market
        if init_data:
            df = market.get_daily(symbol)
        else:
            df = market.get_daily(symbol, end = market.current_date, count = 26+9)

        dif, dea, macd_hist = talib.MACD(df.close, fastperiod=12, slowperiod=26, signalperiod=9)
        return pd.Series( hq.CROSS(dif, dea), index=df.index )

    def get_signal_comment(self, symbol, signal):
        return 'MACD golden cross' if (signal > 0) else 'MACD dead cross'

class StrategyCN( StrategyMacd ):
    def select_stock(self):
        return ['600519','002714','603882','300122','601888','hk3690','hk9988', 'hk0700']

class StrategyUS( StrategyMacd ):
    def select_stock(self):
        return ['AAPL','GOOG','AMZN','TSLA','MSFT','NFLX','FB']

if __name__ == '__main__':
    backtest_args = dict(
        #start_cash= 1000000.00,
        #date_start= hq.date_from_str('3 years ago'),
        #date_end= hq.date_from_str('yesterday'),
        #out_file= 'output/demo.png',
        #parallel= True,
        compare_index= '^GSPC',
    )
    hq.backtest_strategy( [StrategyCN, StrategyUS], **backtest_args )
