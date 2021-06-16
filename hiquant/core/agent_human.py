# -*- coding: utf-8; py-indent-offset:4 -*-

import os

from ..utils import *
from .agent_simulated import *

class HumanAgent(SimulatedAgent):
    fund = None
    conf = None

    last_load_modified_time = None
    last_order_time = None
    push_notify = False
    order_file = ''
    transaction_file = ''
    human_position_file = ''
    bot_position_file = ''
    def __init__(self, fund, agent_conf = None):
        super().__init__(fund, agent_conf)

        self.account = self.conf['account']
        self.order_file = self.conf['order'].replace('{name}', self.account)
        self.portfolio_load_file = self.conf['portfolio_load'].replace('{name}', self.account)
        self.portfolio_save_file = self.conf['portfolio_save'].replace('{name}', self.account)

    def init_portfolio(self, start_cash):
        print('[human agent] init portfolio')
        fund = self.fund
        market = fund.market
        self.portfolio = Portfolio(fund)
        self.last_order_time = market.current_time
        if os.path.isfile(self.portfolio_load_file):
            load_modified_time = self.get_file_modify_time(self.portfolio_load_file)
            self.portfolio.from_csv( self.portfolio_load_file )
            self.last_load_modified_time = load_modified_time
            print('\n... {} |'.format(str_now()), 'loaded:', self.portfolio_load_file, load_modified_time)
        else:
            self.portfolio.available_cash = start_cash

    def before_day(self):
        super().before_day()

    def after_day(self):
        super().after_day()

    def before_tick(self):
        super().before_tick()

    def after_tick(self):
        super().after_tick()

        if os.path.isfile(self.portfolio_save_file):
            save_modified_time = get_file_modify_time(self.portfolio_save_file)
            need_save = (self.last_order_time > save_modified_time)
        else:
            need_save = True

        if need_save:
            self.portfolio.to_csv( self.portfolio_save_file )
            print('\n... {} |'.format(str_now()), 'updated:', self.portfolio_save_file)

        if os.path.isfile(self.portfolio_load_file):
            load_modified_time = get_file_modify_time(self.portfolio_load_file)
            need_load = (load_modified_time > self.last_load_modified_time)
            if need_load:
                self.portfolio = Portfolio(self.fund)
                self.portfolio.from_csv( self.portfolio_load_file )
                self.last_load_modified_time = load_modified_time
                print('\n... {} |'.format(str_now()), 'reloaded:', self.portfolio_load_file, load_modified_time)

    def exec_order(self, symbol, real_count, real_price, earn_str = '', comment = ''):
        market = self.fund.market
        name = market.get_name(symbol)

        self.last_order_time = market.current_time

        str_now = market.current_time.strftime('%Y-%m-%d %H:%M:%S')
        trade = '买入' if real_count > 0 else '卖出'
        msg = '{} | {} {} | {}: {} * {} | {} {}'.format(str_now, symbol, name, trade, round(real_count), round(real_price,2), earn_str, comment)

        print('\r'+msg)

        if self.order_file:
            fp = open(self.order_file, 'a+')
            fp.write(msg + '\n')
            fp.close()

        if self.push_service is not None:
            self.push_service.add_order(symbol, name, real_count, real_price, earn_str, comment)
