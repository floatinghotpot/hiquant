# -*- coding: utf-8; py-indent-offset:4 -*-

import os

from ..utils import get_file_modify_time, str_now
from .portfolio import Portfolio
from .agent_simulated import SimulatedAgent
from .lang import LANG

class HumanAgent(SimulatedAgent):
    market = None
    conf = None

    last_load_modified_time = None
    last_order_time = None

    order_file = ''
    transaction_file = ''
    human_position_file = ''
    bot_position_file = ''

    push_service = None

    def set_verbose(self, verbose = True):
        super().set_verbose(verbose)
        if self.push_service is not None:
            self.push_service.set_verbose(verbose)

    def __init__(self, market, agent_conf = None):
        super().__init__(market, agent_conf)

        self.agent_type = 'simulated'

        self.account = self.conf['account']
        self.order_file = self.conf['order'].replace('{account}', self.account)
        self.portfolio_load_file = self.conf['portfolio_load'].replace('{account}', self.account)
        self.portfolio_save_file = self.conf['portfolio_save'].replace('{account}', self.account)

    def load_portoflio_from_file(self):
        if os.path.isfile(self.portfolio_load_file):
            load_modified_time = get_file_modify_time(self.portfolio_load_file)
            self.portfolio.from_csv( self.portfolio_load_file )
            self.last_load_modified_time = load_modified_time
            print('\n... {} |'.format(str_now()), 'loaded:', self.portfolio_load_file, load_modified_time)

    def init_portfolio(self, start_cash):
        self.portfolio = Portfolio(self.market)
        self.last_order_time = self.market.current_time
        self.portfolio.available_cash = start_cash

    def before_day(self):
        super().before_day()
        self.load_portoflio_from_file()

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
                self.load_portoflio_from_file()

    def exec_order(self, symbol, real_count, real_price, earn_str = '', comment = ''):
        market = self.market
        name = market.get_name(symbol)

        self.last_order_time = market.current_time

        str_now = market.current_time.strftime('%Y-%m-%d %H:%M:%S')
        trade = LANG('buy') if real_count > 0 else LANG('sell')
        msg = '{} | {} {} | {}: {} * {} | {} {}'.format(str_now, symbol, name, trade, round(real_count), round(real_price,2), earn_str, comment)
        print('\r'+msg)

        if self.order_file:
            fp = open(self.order_file, 'a+')
            fp.write(msg + '\n')
            fp.close()

        if self.push_service is not None:
            self.push_service.add_order(symbol, name, real_count, real_price, earn_str, comment)
