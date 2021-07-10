
import pandas as pd
import hiquant as hq

class StrategyStockIndicator( hq.BasicStrategy ):
    symbol_indicators = {}
    indicators = []

    def __init__(self, fund):
        super().__init__(fund, __file__)
        self.indicators = ['macd', 'kdj']

    def schedule_task(self, trader):
        trader.run_daily(self.trade, None, time='14:40')
        trader.run_on_bar_update(self.trade, None)

    def select_stock(self):
        stock_df = pd.read_csv('stockpool/t0_white_horse_20_idx.csv', dtype=str)
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
        signal = hq.gen_indicator_signal(df, indicators)

        # Notice!!! Important !!!
        # if we used the close price of the day to calc indicator,
        # to avoid "future data or function" in backtesting, it should not be used for today's trading
        # either we trade at 14:30 before market close
        # or, shift(1) and trade next morning
        return signal

    def get_signal_comment(self, symbol, signal):
        if symbol in self.symbol_indicators:
            return ' + '.join(self.symbol_indicators[ symbol ])
        else:
            return ' + '.join(self.default_indicators)

def init(fund):
    strategy = StrategyStockIndicator(fund)

if __name__ == '__main__':
    backtest_args = dict(
        #start_cash= 1000000.00,
        date_start= hq.date_from_str('6 months ago'),
        #date_end= hq.date_from_str('yesterday'),
        #out_file= 'output/demo.png',
        #parallel= True,
        compare_index= 'sh000300',
    )
    hq.backtest_strategy( StrategyStockIndicator, **backtest_args )
