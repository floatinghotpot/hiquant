# -*- coding: utf-8; py-indent-offset:4 -*-

import os

from ..utils import datetime_today, get_file_modify_time, str_now
from .portfolio import Portfolio
from .order_cost import OrderCost
from .push_master import MasterPush
from .stock import Stock
from .lang import LANG

class SimulatedAgent:
    conf = {}
    agent_type = ''

    market = None
    order_cost = None
    push_service = None

    last_order_time = None
    order_file = ''
    portfolio_save_file = ''

    portfolio = None
    sell_count = 0
    buy_count = 0

    verbose = False

    def set_verbose(self, verbose = True):
        self.verbose = verbose

    def set_market(self, market):
        self.market = market

    def add_push_service(self, push_servcie):
        self.push_service.add_service(push_servcie)

    def set_order_cost(self, order_cost):
        self.order_cost = order_cost

    def __init__(self, market, agent_conf = {}):
        self.agent_type = 'simulated'
        self.market = market
        self.conf = agent_conf

        self.portfolio = Portfolio(market)
        self.order_cost = OrderCost(0.001, 0.0003, 0.0003, 5.0)
        self.push_service = MasterPush()

        self.sell_count = 0
        self.buy_count = 0

        if 'order' in self.conf:
            self.order_file = self.conf['order']
        if 'portfolio_save' in self.conf:
            self.portfolio_save_file = self.conf['portfolio_save']

    def before_day(self):
        self.buy_count = 0
        self.sell_count = 0
        for symbol, stock in self.portfolio.positions.items():
            stock.sellable = True

    def after_day(self):
        pass

    def before_tick(self):
        pass

    def after_tick(self):
        if self.market.current_date < datetime_today():
            self.push_service.clear()
        else:
            self.push_service.flush()

        if self.portfolio_save_file:
            if os.path.isfile(self.portfolio_save_file):
                save_modified_time = get_file_modify_time(self.portfolio_save_file)
                need_save = (self.last_order_time > save_modified_time)
            else:
                need_save = True

            if need_save:
                stock_df = self.portfolio.to_dataframe()
                stock_df.to_csv( self.portfolio_save_file, index= False)
                print('\n... {} |'.format(str_now()), 'updated:', self.portfolio_save_file)

    def get_portfolio(self):
        return self.portfolio

    def get_transaction_count(self):
        return self.buy_count, self.sell_count

    def init_portfolio(self, start_cash):
        self.portfolio = Portfolio(self.market)
        self.portfolio.available_cash = start_cash
        self.last_order_time = self.market.current_time

    def transfer_cash(self, amount, bank_to_security = True):
        if bank_to_security:
            self.portfolio.available_cash += amount
        else:
            self.portfolio.available_cash -= amount
        if self.portfolio.available_cash < 0:
            self.portfolio.available_cash = 0.0

    def exec_order(self, symbol, real_count, real_price, earn_str = '', comment = ''):
        market = self.market
        name = market.get_name(symbol)

        self.last_order_time = market.current_time

        str_now = market.current_time.strftime('%Y-%m-%d %H:%M:%S')
        trade = LANG('buy') if real_count > 0 else LANG('sell')
        msg = '{} | {} {} | {}: {} * {} | {} {}'.format(str_now, symbol, name, trade, round(real_count), round(real_price,2), earn_str, comment)
        if self.verbose:
            print('\r'+msg)

        if self.order_file:
            fp = open(self.order_file, 'a+')
            fp.write(msg + '\n')
            fp.close()

        if self.push_service is not None:
            market = self.market
            name = market.get_name(symbol)
            self.push_service.add_order(symbol, name, real_count, real_price, earn_str, comment)

    def order(self, symbol, count, price = None, comment = ''):
        market = self.market
        if not price:
            price = market.get_price(symbol)
            if price <= 0:
                return

        p = self.portfolio

        # make sure the count is within our budget
        count = min(count, p.available_cash / price)

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
                    if self.verbose:
                        print('must buy/sell no less than 1 hand', symbol, count, real_count, real_price, p.available_cash)
                    return

                count = real_count * real_price / price

                stock.cost = (stock.cost * stock.shares + price * count) / target_count
                stock.shares += count
            else:
                if stock.sellable:
                    # sell all
                    count = - stock.shares
                    real_count = price * count / real_price

                    cost = stock.cost
                    stock.cost = 0.0
                    stock.shares = 0
                    p.history[symbol] = stock
                    del p.positions[symbol]
                else:
                    if self.verbose:
                        print('stock just buy in, not sellable', symbol, stock.name)
                    return

        elif count > 0:
            name = market.get_name(symbol)
            # a hand must be times of 100
            real_count = int(real_count / 100) * 100
            if real_count == 0:
                if self.verbose:
                    print('must buy no less than 1 hand', symbol, name, count, real_count, real_price, p.available_cash)
                return

            count = real_count * real_price / price

            if symbol in p.history:
                stock = p.history[symbol]
                del p.history[symbol]
            else:
                stock = Stock(symbol, name)

            stock.cost = price
            stock.shares = count
            stock.sellable = (market.sell_rule == 'T+0')

            p.positions[symbol] = stock

        else:
            raise ValueError('attempt sell shares with no position')
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
        earn_str = '--> {} %, '.format( round(earn / cost * 100,2) ) if cost > 0 else ''
        self.exec_order(symbol, round(real_count), round(real_price,3), earn_str, comment)

    def order_target(self, symbol, target_count, price = None, comment = ''):
        if target_count < 0:
            return
        if not price:
            market = self.market
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
            market = self.market
            price = market.get_price(symbol)
        if price <= 0:
            return
        count = value / price
        if count > 0:
            self.order(symbol, count, price, comment)

    def order_target_value(self, symbol, target_value, price = None, comment = ''):
        if not price:
            market = self.market
            price = market.get_price(symbol)
        if price <= 0:
            return
        target_count = target_value / price
        self.order_target(symbol, target_count, price, comment)
