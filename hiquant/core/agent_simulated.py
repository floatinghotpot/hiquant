# -*- coding: utf-8; py-indent-offset:4 -*-

import configparser

from ..utils import *
from .stock import *
from .order_cost import *
from .portfolio import *
from .push_master import *

class SimulatedAgent:
    conf = {}

    fund = None
    push_service = None
    order_cost = None

    portfolio = None
    sell_count = 0
    buy_count = 0

    def __init__(self, fund, agent_conf = None):
        self.fund = fund

        self.conf = {}
        if agent_conf is not None:
            for k, v in agent_conf.items():
                self.conf[ k ] = v

            if 'push_service' in self.conf:
                self.push_service = MasterPush(fund.global_config, self.conf['push_service'])

        hiquant_conf_file = 'hiquant.conf'
        if os.path.isfile(hiquant_conf_file):
            config = configparser.ConfigParser()
            config.read(hiquant_conf_file, encoding='utf-8')
            order_cost_conf = {}
            for k, v in config.items('order_cost'):
                order_cost_conf[k] = v
            self.order_cost = OrderCost(
                float(order_cost_conf['close_tax']),
                float(order_cost_conf['open_commission']),
                float(order_cost_conf['close_commission']),
                float(order_cost_conf['min_commission']),
            )
        else:
            self.order_cost = OrderCost(0.001, 0.0003, 0.0003, 5.0)

        self.portfolio = Portfolio(fund)
        self.sell_count = 0
        self.buy_count = 0

    def before_day(self):
        self.buy_count = 0
        self.sell_count = 0
        pass

    def after_day(self):
        pass

    def before_tick(self):
        pass

    def after_tick(self):
        if self.push_service is not None:
            if self.fund.market.current_date < datetime_today():
                self.push_service.clear()
            else:
                self.push_service.flush()

    def get_portfolio(self):
        return self.portfolio

    def get_transaction_count(self):
        return self.buy_count, self.sell_count

    def init_portfolio(self, start_cash):
        self.portfolio = Portfolio(self.fund)
        self.portfolio.available_cash = start_cash

    def transfer_cash(self, amount, bank_to_security = True):
        if bank_to_security:
            self.portfolio.available_cash += amount
        else:
            self.portfolio.available_cash -= amount
        if self.portfolio.available_cash < 0:
            self.portfolio.available_cash = 0.0

    def exec_order(self, symbol, real_count, real_price, earn_str = '', comment = ''):
        fund = self.fund
        market = fund.market
        msg = '{} | {} | order: {} * {} | {} {}'.format(market.current_time, symbol, round(real_count), round(real_price,2), earn_str, comment)
        if fund.verbose:
            print(msg)

    def order(self, symbol, count, price = None, comment = ''):
        market = self.fund.market
        if not price:
            price = market.get_price(symbol)
            if price <= 0:
                return

        p = self.portfolio
        if count > 0 and p.available_cash < price * count:
            # no enough cash to buy stock, ignore order
            return

        real_price = market.get_real_price(symbol)
        real_count = price * count / real_price

        cost = 0
        if symbol in p.positions:
            stock = p.positions[symbol]
            target_count = stock.shares + count
            if target_count > 0:
                # buy, or not sell all, a hand must be times of 100
                real_count = int(real_count / 100) * 100
                if real_count == 0:
                    return

                count = real_count * real_price / price

                stock.cost = (stock.cost * stock.shares + price * count) / target_count
                stock.shares += count
            else:
                # sell all
                count = - stock.shares
                real_count = price * count / real_price

                cost = stock.cost
                stock.cost = 0.0
                stock.shares = 0
                p.history[symbol] = stock
                del p.positions[symbol]
        elif count > 0:
            xcount = count
            # a hand must be times of 100
            real_count = int(real_count / 100) * 100
            if real_count == 0:
                return

            count = real_count * real_price / price

            if symbol in p.history:
                stock = p.history[symbol]
                del p.history[symbol]
            else:
                stock = Stock(symbol, market.get_name(symbol))
            stock.cost = price
            stock.shares = count
            p.positions[symbol] = stock

        else:
            return

        # calculate trade cost
        trade_cost = 0.0
        trade_value = price * max(count, -count)
        if count > 0:
            trade_cost = trade_value * (self.order_cost.open_commission)
        else:
            trade_cost = trade_value * (self.order_cost.close_commission + self.order_cost.close_tax)
        if cost < self.order_cost.min_commission:
            trade_cost = self.order_cost.min_commission

        p.available_cash = round(p.available_cash  - price * count - trade_cost, 2)

        if real_count > 0:
            self.buy_count += 1
        elif real_count < 0:
            self.sell_count += 1

        earn = round(price - cost, 2)
        earn_str = ' --> {} %'.format( round(earn / cost * 100,2) ) if cost > 0 else ''
        self.exec_order(symbol, round(real_count), round(real_price,3), earn_str, comment)

    def order_target(self, symbol, target_count, price = None, comment = ''):
        if target_count < 0:
            return
        if not price:
            market = self.fund.market
            price = market.get_price(symbol)
        if price <= 0:
            return
        p = self.portfolio
        if symbol in p.positions:
            stock = p.positions[symbol]
            count = target_count - stock.shares
        else:
            if target_count == 0:
                return
            count = target_count
        self.order(symbol, count, price, comment)

    def order_value(self, symbol, value, price = None, comment = ''):
        if not price:
            market = self.fund.market
            price = market.get_price(symbol)
        if price <= 0:
            return
        count = value / price
        if count > 0:
            self.order(symbol, count, price, comment)

    def order_target_value(self, symbol, target_value, price = None, comment = ''):
        if not price:
            market = self.fund.market
            price = market.get_price(symbol)
        if price <= 0:
            return
        target_count = target_value / price
        self.order_target(symbol, target_count, price, comment)
