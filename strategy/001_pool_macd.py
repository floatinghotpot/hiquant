
import pandas as pd
import talib

from hiquant import *

class StrategyMacd( BasicStrategy ):
    def __init__(self, fund, strategy_file):
        super().__init__(fund, strategy_file)

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
            df = market.get_daily(symbol, end = market.current_date, count = 26+9)

        dif, dea, macd_hist = talib.MACD(df.close, fastperiod=12, slowperiod=26, signalperiod=9)
        return pd.Series( CROSS(dif, dea), index=df.index )
        #dif, dea, macd_hist = MACD(df.close)
        #return CROSS(dif, dea)

    def get_signal_comment(self, symbol, signal):
        return 'MACD 金叉' if (signal > 0) else 'MACD 死叉'

def init(fund):
    strategy = StrategyMacd(fund, __file__)

    # set call back timer
    trader = fund.trader
    trader.run_daily(before_market_open, strategy, time='before_open')
    trader.run_on_bar_update(trade, strategy)
    trader.run_daily(trade, strategy, time='14:30')
    trader.run_daily(after_market_close, strategy, time='after_close')

def before_market_open(strategy):
    pass

def trade(strategy):
    strategy.trade()

def after_market_close(strategy):
    pass
