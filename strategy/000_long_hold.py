import pandas as pd
import hiquant as hq

class StrategyLongHold( hq.BasicStrategy ):
    symbol_max_value = {}
    symbol_cost = {}

    def __init__(self, fund):
        super().__init__(fund, __file__)
        self.max_stocks = 10
        self.max_weight = 1.0
        fund.set_name('耐心持有策略')

    def schedule_task(self, trader):
        trader.run_daily(self.trade, None, time='09:30')
        trader.run_on_bar_update(self.trade, None)

    #def select_targets(self):
    #    return pd.read_csv('stockpool/t0_white_horse_20.csv', dtype=str)['symbol'].tolist()

    def get_trade_decision(self, symbol, market, portfolio, max_value_pos_stock):
        max_stocks = min(self.max_stocks, len(self.targets))
        init_value_per_stock = portfolio.init_value / max_stocks * self.max_weight

        if symbol in portfolio.positions:
            return symbol, 0, 0, ''
        else:
            return symbol, 1, max_value_pos_stock, ''

    def get_signal_comment(self, symbol, signal):
        return '耐心持有'

def init(fund):
    strategy = StrategyLongHold(fund)

if __name__ == '__main__':
    backtest_args = dict(
        #start_cash= 1000000.00,
        date_start= hq.date_from_str('6 months ago'),
        #date_end= hq.date_from_str('yesterday'),
        #out_file= 'output/demo.png',
        #parallel= True,
        compare_index= 'sh000300',
    )
    hq.backtest_strategy( StrategyLongHold, **backtest_args )
