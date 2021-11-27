# -*- coding: utf-8; py-indent-offset:4 -*-

import os

from ..utils import datetime_today
from .lang import LANG

class Strategy:
    fund = None
    name = ''
    conf = {}

    max_stocks = 10
    max_weight = 1.0
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

        self.targets = self.select_targets()
        self.symbol_signal = {}

        market = fund.market
        agent = fund.agent
        portfolio = agent.get_portfolio()

        concerned_stocks = list(set(self.targets) | set(portfolio.positions.keys()))
        concerned_stocks.sort()
        market.watch( concerned_stocks )

        self.schedule_task(fund.trader)

    def schedule_task(self, trader):
        trader.run_daily(self.trade, None, time='14:30')
        trader.run_on_bar_update(self.trade, None)

    def select_targets(self):
        pass

    def gen_trade_signal(self, symbol, init_data = False):
        pass

    def get_signal_comment(self, symbol, signal):
        pass

    def init_trade_signal(self, symbol):
        return symbol, self.gen_trade_signal(symbol, True)

    # symbol, signal, value, reason
    def get_trade_decision(self, symbol, market, portfolio, max_value_pos_stock):
        if not market.allow_trading(symbol, market.current_date):
            return symbol, 0, 0, ''

        price = market.get_price(symbol, market.current_date)
        if price < 0.01:
            return symbol, 0, 0, ''

        if market.current_date < datetime_today():
            date_signal = self.symbol_signal[ symbol ]
            if market.current_date in date_signal:
                trade_signal = date_signal.loc[ market.current_date ]
            else:
                trade_signal = self.gen_trade_signal(symbol, init_data=False).iloc[-1]
        else:
            trade_signal = self.gen_trade_signal(symbol, init_data=False).iloc[-1]

        if (symbol in portfolio.positions):
            cost = portfolio.positions[ symbol ].cost
            if (trade_signal < 0):
                return symbol, -1, 0, LANG('signal') + ': ' + self.get_signal_comment(symbol, trade_signal)
            elif (trade_signal > 0):
                # will handle it below
                pass
            else:
                # only stop loss/earn when no signal to buy or sell
                # or else, may need buy again after sell
                if price <= cost * self.stop_loss:
                    stop_percent = round(100*(self.stop_loss-1),2)
                    return symbol, -1, 0, LANG('stop loss') + ': {} %'.format(stop_percent)
                elif price >= cost * self.stop_earn:
                    stop_percent = round(100*(self.stop_earn-1),2)
                    return symbol, -1, 0, LANG('stop earn') + ' {} %'.format(stop_percent)

        if (trade_signal > 0) and (symbol in self.targets):
            reason = LANG('signal') + ': ' + self.get_signal_comment(symbol, trade_signal)
            value = 0.0
            if symbol in portfolio.positions:
                value = price * portfolio.positions[ symbol ].shares
            if value < max_value_pos_stock:
                return symbol, 1, max_value_pos_stock, reason

        return symbol, 0, 0, ''

    def trade(self, param = None):
        fund = self.fund
        market = fund.market
        agent = fund.agent
        portfolio = agent.get_portfolio()

        max_stocks = min(self.max_stocks, len(self.targets))
        max_value_pos_stock = portfolio.total_value() / max_stocks * self.max_weight

        # we merge the targets and in stock shares, but keep tarets ahead of others with higher priority to buy
        concerned_stocks = self.targets + list(set(portfolio.positions.keys()) - set(self.targets))

        # make sure the daily data in cache of market object
        market.watch( concerned_stocks )

        # for those symbol witout signal, we need init the data
        symbol_list = list(set(concerned_stocks) - self.symbol_signal.keys())
        symbol_signal_list = [self.init_trade_signal(symbol) for symbol in symbol_list]
        for symbol, signal in symbol_signal_list:
            self.symbol_signal[ symbol ] = signal

        # find out the stocks to sell or buy
        decision_list = [self.get_trade_decision(symbol, market, portfolio, max_value_pos_stock) for symbol in concerned_stocks]

        # now sell first, we may need the cash to buy other stocks
        for symbol, signal, value, reason in decision_list:
            if signal < 0:
                agent.order_target(symbol, 0, comment = reason)

        # now buy
        for symbol, signal, value, reason in decision_list:
            if signal > 0:
                if (symbol in portfolio.positions) or (portfolio.count() < max_stocks):
                    agent.order_target_value(symbol, value, comment = reason)

        #portfolio.print()
