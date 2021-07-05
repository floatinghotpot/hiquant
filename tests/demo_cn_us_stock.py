import pandas as pd
import talib
from hiquant import *

class StrategyMacd( BasicStrategy ):
    def __init__(self, fund):
        super().__init__(fund, __file__)

    def gen_trade_signal(self, symbol, init_data = False):
        market = self.fund.market
        if init_data:
            df = market.get_daily(symbol)
        else:
            df = market.get_daily(symbol, end = market.current_date, count = 26+9)

        dif, dea, macd_hist = talib.MACD(df.close, fastperiod=12, slowperiod=26, signalperiod=9)
        return pd.Series( CROSS(dif, dea), index=df.index )

    def get_signal_comment(self, symbol, signal):
        return 'MACD golden cross' if (signal > 0) else 'MACD dead cross'

class StrategyCN( StrategyMacd ):
    def __init__(self, fund):
        super().__init__(fund)
    def select_stock(self):
        return ['600519','002714','603882','300122','601888','hk3690','hk9988', 'hk0700']

class StrategyUS( StrategyMacd ):
    def __init__(self, fund):
        super().__init__(fund)
    def select_stock(self):
        return ['AAPL','GOOG','AMZN','TSLA','FB','MSFT','NFLX', 'SONY'] 

date_start = date_from_str('3 years ago')
date_end = date_from_str('yesterday')
market = Market(date_start, date_end)
trader = Trader(market)

fund_args = {
    'Fund #1': StrategyCN,
    'Fund #2': StrategyUS,
}
for name, stra in fund_args.items():
    fund = Fund(market, trader)
    fund.set_name(name)
    fund.set_start_cash( 1000000.00 )
    fund.add_strategy( stra(fund) )
    trader.add_fund(fund)

trader.run_fund(date_start, date_end)
trader.print_report()
trader.plot(compare_index= 'sh000300')
