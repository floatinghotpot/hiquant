
from hiquant import *

class StrategyStockIndicator( BasicStrategy ):
    symbol_indicators = {}
    default_indicators = []

    def __init__(self, fund, strategy_file):
        super().__init__(fund, strategy_file)
        self.default_indicators = self.conf['default_indicators'].replace(' ','').split('+')

    def select_stock(self):
        # read stock from stock pool
        stock_df = get_stockpool_df(self.conf['stock_pool'])

        for i, row in stock_df.iterrows():
            self.symbol_indicators[row['symbol']] = row['indicators'].replace(' ','').split('+')

        return stock_df['symbol'].tolist()

    def gen_trade_signal(self, symbol, init_data = False):
        market = self.fund.market
        if init_data:
            df = market.get_daily(symbol)
        else:
            df = market.get_daily(symbol, end = market.current_date, count = 60)

        indicators = self.symbol_indicators[symbol] if (symbol in self.symbol_indicators) else self.default_indicators
        return gen_indicator_signal(df, indicators)

    def get_signal_comment(self, symbol, signal):
        if symbol in self.symbol_indicators:
            return ' + '.join(self.symbol_indicators[ symbol ])
        else:
            return ' + '.join(self.default_indicators)

def init(fund):
    strategy = StrategyStockIndicator(fund, __file__)

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
