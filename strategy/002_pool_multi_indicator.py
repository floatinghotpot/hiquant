
from hiquant import *

class StrategyMultiIndicator( BasicStrategy ):
    indicators = []

    def __init__(self, fund, strategy_file):
        super().__init__(fund, strategy_file)
        self.indicators = self.conf['indicators'].replace(' ','').split('+')

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
            df = market.get_daily(symbol, end = market.current_date, count = 60)

        return gen_indicator_signal(df, self.indicators)

    def get_signal_comment(self, symbol, signal):
        return ' + '.join(self.indicators)

def init(fund):
    strategy = StrategyMultiIndicator(fund, __file__)

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
