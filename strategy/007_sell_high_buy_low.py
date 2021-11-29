import pandas as pd
import hiquant as hq

class StrategyValueAveraging( hq.BasicStrategy ):
    symbol_max_value = {}
    symbol_cost = {}

    def __init__(self, fund):
        super().__init__(fund, __file__)
        self.max_stocks = 10
        self.max_weight = 1.0
        fund.set_name('高抛低吸策略')

    def schedule_task(self, trader):
        trader.run_daily(self.trade, None, time='09:30')
        trader.run_on_bar_update(self.trade, None)

    #def select_targets(self):
    #    return pd.read_csv('stockpool/t0_white_horse_20.csv', dtype=str)['symbol'].tolist()

    def get_trade_decision(self, symbol, market, portfolio, max_value_pos_stock):
        max_stocks = min(self.max_stocks, len(self.targets))
        init_value_per_stock = portfolio.init_value / max_stocks * self.max_weight * 0.80

        value = 0.0
        max_value = init_value_per_stock
        if symbol in portfolio.positions:
            price = market.get_price(symbol, market.current_date)
            value = price * portfolio.positions[ symbol ].shares
            max_value = max(value, self.symbol_max_value[ symbol ] if (symbol in self.symbol_max_value) else init_value_per_stock)
            self.symbol_max_value[ symbol ] = max_value

        if value < max_value * (1 - 0.10):
            new_value = max_value * (1 + 0.10)
            self.symbol_cost[ symbol ] = new_value
            return symbol, 1, new_value, ''
        else:
            cost = self.symbol_cost[ symbol ]
            if value > cost * (1 + 0.20):
                new_value = cost * (1 - 0.05)
                self.symbol_max_value[ symbol ] = new_value
                self.symbol_cost[ symbol ] = new_value
                return symbol, 1, new_value, ''
        
        return symbol, 0, 0, ''

    def get_signal_comment(self, symbol, signal):
        return '耐心持有'

def init(fund):
    strategy = StrategyValueAveraging(fund)

if __name__ == '__main__':
    backtest_args = dict(
        #start_cash= 1000000.00,
        date_start= hq.date_from_str('6 months ago'),
        #date_end= hq.date_from_str('yesterday'),
        #out_file= 'output/demo.png',
        #parallel= True,
        compare_index= 'sh000300',
    )
    hq.backtest_strategy( StrategyValueAveraging, **backtest_args )
