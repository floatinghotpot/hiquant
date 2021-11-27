
import pandas as pd
import hiquant as hq

class StrategyMultiIndicator( hq.BasicStrategy ):
    indicators = []

    def __init__(self, fund):
        super().__init__(fund, __file__)
        self.indicators = ['boll']

    def schedule_task(self, trader):
        trader.run_daily(self.trade, None, time='09:30')
        trader.run_on_bar_update(self.trade, None)

    def select_targets(self):
        stock_df = pd.read_csv('stockpool/realtime_trade.csv', dtype=str)
        if self.fund.verbose:
            print(stock_df)
        return stock_df['symbol'].tolist()

    def gen_trade_signal(self, symbol, init_data = False):
        market = self.fund.market
        if init_data:
            df = market.get_daily(symbol)
        else:
            df = market.get_daily(symbol, end = market.current_date, count = 60)

        signal = hq.gen_indicator_signal(df, self.indicators)

        # Notice!!! Important !!!
        # if we used the close price of the day to calc indicator,
        # to avoid "future data or function" in backtesting, it should not be used for today's trading
        # either we trade at 14:30 before market close
        # or, shift(1) and trade next morning
        return signal.shift(1).fillna(0)

    def get_signal_comment(self, symbol, signal):
        return ' + '.join(self.indicators)

def init(fund):
    strategy = StrategyMultiIndicator(fund)

if __name__ == '__main__':
    backtest_args = dict(
        #start_cash= 1000000.00,
        date_start= hq.date_from_str('6 months ago'),
        #date_end= hq.date_from_str('yesterday'),
        #out_file= 'output/demo.png',
        #parallel= True,
        compare_index= 'sh000300',
    )
    hq.backtest_strategy( StrategyMultiIndicator, **backtest_args )
