# -*- coding: utf-8; py-indent-offset:4 -*-

import os

from ..utils import datetime_today
from .lang import LANG

class Strategy:
    fund = None
    name = ''
    conf = {}

    max_stocks = 10
    max_weight = 1.2
    stop_loss = 0.0
    stop_earn = 10000.0

    def __init__(self, fund, strategy_file):
        fund.add_strategy(self)

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

        self.targets = self.select_stock()
        self.symbol_signal = {}

        market = fund.market
        agent = fund.agent
        portfolio = agent.get_portfolio()

        concerned_stocks = list(set(self.targets) | set(portfolio.positions.keys()))
        concerned_stocks.sort()
        market.watch( concerned_stocks )

        trader = fund.trader
        trader.run_daily(self.before_market_open, None, time='before_open')
        trader.run_on_bar_update(self.trade, None)
        trader.run_daily(self.trade, None, time='14:30')
        trader.run_daily(self.after_market_close, None, time='after_close')

    def select_stock(self):
        pass

    def gen_trade_signal(self, symbol, init_data = False):
        pass

    def get_signal_comment(self, symbol, signal):
        pass

    def init_trade_signal(self, symbol):
        if self.fund.verbose:
            print('\tinit history trade signal:', symbol)
        return symbol, self.gen_trade_signal(symbol, True)

    def get_trade_decision(self, symbol, market, portfolio, max_pos_per_stock):
        if not market.allow_trading(symbol, market.current_date):
            return symbol, 0, ''

        price = market.get_price(symbol, market.current_date)
        if price < 0.01:
            return symbol, 0, ''

        if market.current_date < datetime_today():
            trade_signal = self.symbol_signal[ symbol ].loc[ market.current_date ]
        else:
            trade_signal = self.gen_trade_signal(symbol, init_data=False).iloc[-1]

        if (symbol in portfolio.positions):
            cost = portfolio.positions[ symbol ].cost
            if (trade_signal < 0):
                return symbol, -1, LANG('signal') + self.get_signal_comment(symbol, trade_signal)
            elif (trade_signal > 0):
                # will handle it below
                pass
            else:
                # only stop loss/earn when no signal to buy or sell
                # or else, may need buy again after sell
                if price <= cost * self.stop_loss:
                    diff = price / cost - 1
                    return symbol, -1, LANG('stop loss') + ': {} %'.format(round(100*(self.stop_loss-1),2))
                elif price >= cost * self.stop_earn:
                    diff = price / cost - 1
                    return symbol, -1, LANG('stop earn') + ' {} %'.format(round(100*(self.stop_earn-1),2))

        if (trade_signal > 0) and (symbol in self.targets):
            stock_value = 0.0
            if symbol in portfolio.positions:
                stock_value = price * portfolio.positions[ symbol ].shares
            if stock_value < max_pos_per_stock:
                return symbol, 1, LANG('signal') + self.get_signal_comment(symbol, trade_signal)

        return symbol, 0, ''

    def trade(self, param = None):
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

        symbol_list = list(set(concerned_stocks) - self.symbol_signal.keys())
        symbol_signal_list = [self.init_trade_signal(symbol) for symbol in symbol_list]
        for symbol, signal in symbol_signal_list:
            self.symbol_signal[ symbol ] = signal

        # find out the stocks to sell or buy
        decision_list = [self.get_trade_decision(symbol, market, portfolio, max_pos_per_stock) for symbol in concerned_stocks]

        # now sell first, we may need the cash to buy other stocks
        for symbol, signal, reason in decision_list:
            if signal < 0:
                agent.order_target(symbol, 0, comment = reason)

        # now buy
        for symbol, signal, reason in decision_list:
            if signal > 0:
                agent.order_target_value(symbol, max_pos_per_stock, comment = reason)

    def before_market_open(self, param = None):
        pass

    def after_market_close(self, param = None):
        pass
