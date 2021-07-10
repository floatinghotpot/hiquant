
# -*- coding: utf-8; py-indent-offset:4 -*-
import datetime
import pandas as pd
import hiquant as hq

class MyStrategy( hq.BasicStrategy ):
    def __init__(self, fund):
        super().__init__(fund, __file__)
        self.max_stocks = 10
        self.max_weight = 1.0
        self.stop_loss = 1 + (-0.10)
        self.stop_earn = 1 + (+0.50)

    def schedule_task(self, trader):
        # trade at 10:00 after observing the main fund flow,
        # may get a changed price between open and close with time factor 0.5
        #trader.run_daily(self.trade, None, time='10:00')
        trader.run_daily(self.trade, None, time='13:00')
        trader.run_on_bar_update(self.trade, None)

    def select_stock(self):
        # read stock from stock pool
        stock_df = hq.get_stockpool_df('stockpool/realtime_trade.csv')
        if self.fund.verbose:
            print(stock_df)

        return stock_df['symbol'].tolist()

    def gen_trade_signal(self, symbol, init_data = False):
        market = self.fund.market
        if init_data:
            df = market.get_daily(symbol)
        else:
            df = market.get_daily(symbol, end = market.current_date, count = 1)

        signal = hq.signal_mffi(df)

        # Notice!!! Important !!!
        # if we used the close price of the day to calc indicator,
        # to avoid "future data or function" in backtesting, it should not be used for today's trading
        # either we trade at 14:30 before market close
        # or, shift(1) and trade next morning
        return signal

    def get_signal_comment(self, symbol, signal):
        return '主力买入' if (signal > 0) else '主力卖出'

def init(fund):
    strategy = MyStrategy(fund)

if __name__ == '__main__':
    backtest_args = dict(
        #start_cash= 1000000.00,
        date_start= datetime.datetime(2021,2,1), #hq.date_from_str('6 months ago'),
        #date_end= hq.date_from_str('yesterday'),
        #out_file= 'output/demo.png',
        #parallel= True,
        compare_index= '000651',
    )
    hq.backtest_strategy( MyStrategy, **backtest_args )

