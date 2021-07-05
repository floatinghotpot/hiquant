
from hiquant import *

class StrategyStockIndicator( BasicStrategy ):
    symbol_indicators = {}
    indicators = []

    def __init__(self, fund):
        super().__init__(fund, __file__)
        self.default_indicators = self.conf['indicators'].replace(' ','').split('+')

    def select_stock(self):
        # read stock from stock pool
        stock_df = get_stockpool_df(self.conf['stock_pool'])
        if self.fund.verbose:
            print(stock_df)

        for i, row in stock_df.iterrows():
            self.symbol_indicators[row['symbol']] = row['indicators'].replace(' ','').split('+')

        return stock_df['symbol'].tolist()

    def gen_trade_signal(self, symbol, init_data = False):
        market = self.fund.market
        if init_data:
            df = market.get_daily(symbol)
        else:
            df = market.get_daily(symbol, end = market.current_date, count = 60)

        indicators = self.symbol_indicators[symbol] if (symbol in self.symbol_indicators) else self.indicators
        return gen_indicator_signal(df, indicators)

    def get_signal_comment(self, symbol, signal):
        if symbol in self.symbol_indicators:
            return ' + '.join(self.symbol_indicators[ symbol ])
        else:
            return ' + '.join(self.default_indicators)

    def before_market_open(self, param = None):
        pass

    def after_market_close(self, param = None):
        pass

def init(fund):
    strategy = StrategyStockIndicator(fund)
