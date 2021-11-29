
import pandas as pd
import hiquant as hq

class StrategyMacd( hq.BasicStrategy ):
    def __init__(self, fund):
        super().__init__(fund, __file__)
        fund.set_name('MACD策略')

    def schedule_task(self, trader):
        trader.run_daily(self.trade, None, time='09:30')
        trader.run_on_bar_update(self.trade, None)

    #def select_targets(self):
    #    return pd.read_csv('stockpool/t0_white_horse_20.csv', dtype=str)['symbol'].tolist()

    def gen_trade_signal(self, symbol, init_data = False):
        market = self.fund.market
        if init_data:
            df = market.get_daily(symbol)
        else:
            df = market.get_daily(symbol, end = market.current_date, count = 26+9)

        dif, dea, macd_hist = hq.MACD(df.close, fast=12, slow=26, signal=9)
        signal = pd.Series( hq.CROSS(dif, dea), index=df.index )

        # Notice!!! Important !!!
        # if we used the close price of the day to calc indicator,
        # to avoid "future data or function" in backtesting, it should not be used for today's trading
        # either we trade at 14:30 before market close
        # or, shift(1) and trade next morning
        return signal.shift(1).fillna(0)

    def get_signal_comment(self, symbol, signal):
        return 'MACD 金叉' if (signal > 0) else 'MACD 死叉'

def init(fund):
    strategy = StrategyMacd(fund)

if __name__ == '__main__':
    backtest_args = dict(
        #start_cash= 1000000.00,
        date_start= hq.date_from_str('6 months ago'),
        #date_end= hq.date_from_str('yesterday'),
        #out_file= 'output/demo.png',
        #parallel= True,
        compare_index= 'sh000300',
    )
    hq.backtest_strategy( StrategyMacd, **backtest_args )
