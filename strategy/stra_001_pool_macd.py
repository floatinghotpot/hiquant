
import pandas as pd
import talib
import hiquant as hq

class StrategyMacd( hq.BasicStrategy ):
    def __init__(self, fund):
        super().__init__(fund, __file__)

    def select_stock(self):
        stock_df = pd.read_csv('stockpool/t0_white_horse_20_idx.csv', dtype=str)
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
        return pd.Series( hq.CROSS(dif, dea), index=df.index )
        #dif, dea, macd_hist = MACD(df.close)
        #return CROSS(dif, dea)

    def get_signal_comment(self, symbol, signal):
        return 'MACD 金叉' if (signal > 0) else 'MACD 死叉'

    def before_market_open(self, param = None):
        pass

    def after_market_close(self, param = None):
        pass

def init(fund):
    strategy = StrategyMacd(fund)
