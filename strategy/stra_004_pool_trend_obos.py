
import pandas as pd
import talib

from hiquant import *

class MyStrategy( BasicStrategy ):
    def __init__(self, fund):
        super().__init__(fund, __file__)
        self.max_stocks = 10
        self.max_weight = 1.2
        self.stop_loss = 1 + (-0.10)
        self.stop_earn = 1 + (+0.20)

    def select_stock(self):
        # read stock from stock pool
        stock_df = get_stockpool_df(self.conf['stock_pool'])
        if self.fund.verbose:
            print(stock_df)

        return stock_df['symbol'].tolist()

    def gen_trade_signal(self, symbol, init_data = False):
        market = self.fund.market
        if init_data:
            df = market.get_daily(symbol)
        else:
            df = market.get_daily(symbol, end = market.current_date, count = 50+10)

        vhf = VHF(df.close, length= 28)
        vhf = SIGN(vhf.fillna(0) - 0.35)
        vhf[ vhf > 0 ] = 1
        vhf[ vhf < 0 ] = 0
        vhf_trend = vhf
        vhf_obos = 1 - vhf_trend

        # trend
        trend = [
            signal_ma,
            signal_macd,
            signal_trix,
            signal_dma,
        ]
        trend_long = pd.Series(0, df.index)
        for func in trend:
            trend_long += signal_to_long( func(df), long_value= 1, short_value= -1 )

        # obos
        obos = [
            signal_kdj,
            signal_wr,
            signal_boll,
            signal_bias,
        ]
        obos_long = pd.Series(0, df.index)
        for func in obos:
            obos_long += signal_to_long( func(df), long_value= 1, short_value= -1 )

        # normal
        normal = [
            signal_cci,
            signal_sar,
            signal_rsi,
            signal_mfi,
        ]
        normal_long = pd.Series(0, df.index)
        for func in normal:
            normal_long += signal_to_long( func(df), long_value= 1, short_value= -1 )

        average_long = vhf_trend * trend_long + vhf_obos * obos_long + normal_long
        average_long[ average_long > 0 ] = 1
        average_long[ average_long < 0 ] = 0

        return long_to_signal( average_long )

    def get_signal_comment(self, symbol, signal):
        return 'trend/obos mix buy signal' if (signal > 0) else 'trend/obos mix sell signal'

    def before_market_open(self, param = None):
        pass

    def after_market_close(self, param = None):
        pass

def init(fund):
    strategy = MyStrategy(fund)
