
import pandas as pd
import hiquant as hq

class MyStrategy( hq.BasicStrategy ):
    def __init__(self, fund):
        super().__init__(fund, __file__)
        self.max_stocks = 10
        self.max_weight = 1.2
        self.stop_loss = 1 + (-0.10)
        self.stop_earn = 1 + (+0.20)

    def schedule_task(self, trader):
        trader.run_daily(self.trade, None, time='14:30')
        trader.run_on_bar_update(self.trade, None)

    def select_stock(self):
        stock_df = pd.read_csv('stockpool/t0_white_horse_20.csv', dtype=str)
        if self.fund.verbose:
            print(stock_df)
        return stock_df['symbol'].tolist()

    def gen_trade_signal(self, symbol, init_data = False):
        market = self.fund.market
        if init_data:
            df = market.get_daily(symbol)
        else:
            df = market.get_daily(symbol, end = market.current_date, count = 50+10)

        vhf = hq.VHF(df.close, length= 28)
        vhf = hq.SIGN(vhf.fillna(0) - 0.35)
        vhf[ vhf > 0 ] = 1
        vhf[ vhf < 0 ] = 0
        vhf_trend = vhf
        vhf_obos = 1 - vhf_trend

        # trend
        trend = [
            hq.signal_ma,
            hq.signal_macd,
            hq.signal_trix,
            hq.signal_dma,
        ]
        trend_long = pd.Series(0, df.index)
        for func in trend:
            trend_long += hq.signal_to_long( func(df) ) - 0.50

        # obos
        obos = [
            hq.signal_kdj,
            hq.signal_wr,
            hq.signal_boll,
            hq.signal_bias,
        ]
        obos_long = pd.Series(0, df.index)
        for func in obos:
            obos_long += hq.signal_to_long( func(df) ) - 0.50

        # normal
        normal = [
            hq.signal_cci,
            hq.signal_sar,
            hq.signal_rsi,
            hq.signal_mfi,
        ]
        normal_long = pd.Series(0, df.index)
        for func in normal:
            normal_long += hq.signal_to_long( func(df) ) - 0.50

        # merge all the signals
        average_long = vhf_trend * trend_long + vhf_obos * obos_long + normal_long
        average_long[ average_long > 0 ] = 1
        average_long[ average_long < 0 ] = 0
        signal = average_long.diff(1).fillna(0)

        # Notice!!! Important !!!
        # if we used the close price of the day to calc indicator,
        # to avoid "future data or function" in backtesting, it should not be used for today's trading
        # either we trade at 14:30 before market close
        # or, shift(1) and trade next morning
        return signal

    def get_signal_comment(self, symbol, signal):
        return 'trend/obos mix buy signal' if (signal > 0) else 'trend/obos mix sell signal'

def init(fund):
    strategy = MyStrategy(fund)

if __name__ == '__main__':
    backtest_args = dict(
        #start_cash= 1000000.00,
        date_start= hq.date_from_str('6 months ago'),
        #date_end= hq.date_from_str('yesterday'),
        #out_file= 'output/demo.png',
        #parallel= True,
        compare_index= 'sh000300',
    )
    hq.backtest_strategy( MyStrategy, **backtest_args )
