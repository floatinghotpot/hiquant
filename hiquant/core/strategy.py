# -*- coding: utf-8; py-indent-offset:4 -*-

import os
from ..utils import datetime_today

class Strategy:
    fund = None
    name = ''
    conf = {}

    max_stocks = 10
    max_weight = 1.2
    stop_loss = 0.0
    stop_earn = 10000.0

    def __init__(self, fund, strategy_file):
        fund.strategy = self

        self.fund = fund
        self.name = os.path.basename(strategy_file)
        self.conf = fund.conf

        self.max_stocks = 10
        self.max_weight = 1.0
        self.stop_loss = 1 + (-1.0)
        self.stop_earn = 1 + (10000.0)

        if 'max_stocks' in self.conf:
            self.max_stocks = int(self.conf['max_stocks'])
        if 'max_weight' in self.conf:
            self.max_weight = float(self.conf['max_weight'])
        if 'stop_loss' in self.conf:
            self.stop_loss = 1 + float(self.conf['stop_loss'])
        if 'stop_earn' in self.conf:
            self.stop_earn = 1 + float(self.conf['stop_earn'])

class BasicStrategy( Strategy ):
    symbol_signal = {}

    def __init__(self, fund, strategy_file):
        super().__init__(fund, strategy_file)

        agent = fund.agent
        #portfolio = agent.get_portfolio()
        #market = fund.market

        self.targets = self.select_stock()
        self.symbol_signal = {}

    def select_stock(self):
        pass

    def gen_trade_signal(self, symbol, init_data = False):
        pass

    def get_signal_comment(self, symbol, signal):
        pass

    def trade(self):
        fund = self.fund
        market = fund.market
        agent = fund.agent
        portfolio = agent.get_portfolio()

        total_value = portfolio.total_value()
        max_stocks = min(self.max_stocks, len(self.targets))
        max_pos_per_stock = total_value / max_stocks * self.max_weight

        # calc and cache the trade signal for history data
        concerned_stocks = list(set(self.targets) | set(portfolio.positions.keys()))
        concerned_stocks.sort()
        market.watch( concerned_stocks )
        for symbol in concerned_stocks:
            if not (symbol in self.symbol_signal):
                self.symbol_signal[ symbol ] = self.gen_trade_signal(symbol, init_data=True)

        # find out the stocks to sell or buy
        sell_list = {}
        buy_list = {}
        for symbol in concerned_stocks:
            if not market.allow_trading(symbol, market.current_date):
                continue

            price = market.get_price(symbol, market.current_date)
            if price < 0.01:
                continue

            if market.current_date < datetime_today():
                trade_signal = self.symbol_signal[ symbol ].loc[ market.current_date ]
            else:
                trade_signal = self.gen_trade_signal(symbol, init_data=False).iloc[-1]

            if (symbol in portfolio.positions):
                cost = portfolio.positions[ symbol ].cost
                if price <= cost * self.stop_loss:
                    diff = price / cost - 1
                    sell_list[ symbol ] = '止损: {} %'.format(round(100*diff,2))
                elif price >= cost * self.stop_earn:
                    diff = price / cost - 1
                    sell_list[ symbol ] = '止盈: {} %'.format(round(100*diff,2))
                elif (trade_signal < 0):
                    sell_list[ symbol ] = '卖出信号: ' + self.get_signal_comment(symbol, trade_signal)

            if (trade_signal > 0) and (symbol in self.targets) and (not symbol in sell_list):
                stock_value = 0.0
                if symbol in portfolio.positions:
                    stock_value = price * portfolio.positions[ symbol ].shares
                if stock_value < max_pos_per_stock:
                    buy_list[ symbol ] = '买入信号: ' + self.get_signal_comment(symbol, trade_signal)

        # now sell first, we may need the cash to buy other stocks
        for symbol, reason in sell_list.items():
            agent.order_target(symbol, 0, comment = reason)

        # now buy
        for symbol, reason in buy_list.items():
            agent.order_target_value(symbol, max_pos_per_stock, comment = reason)
