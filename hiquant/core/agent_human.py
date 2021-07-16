# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import pandas as pd

from ..utils import get_file_modify_time, str_now
from .agent_simulated import SimulatedAgent

class HumanAgent(SimulatedAgent):
    market = None
    conf = None

    human_position_file = ''
    last_load_modified_time = None
    push_service = None

    def set_verbose(self, verbose = True):
        super().set_verbose(verbose)
        if self.push_service is not None:
            self.push_service.set_verbose(verbose)

    def __init__(self, market, agent_conf = None):
        super().__init__(market, agent_conf)

        self.agent_type = 'human'
        if 'portfolio_load' in self.conf:
            self.portfolio_load_file = self.conf['portfolio_load']

    def load_portoflio_from_file(self):
        if os.path.isfile(self.portfolio_load_file):
            load_modified_time = get_file_modify_time(self.portfolio_load_file)
            stock_df = pd.read_csv(self.portfolio_load_file, dtype= str)
            stock_df = stock_df.astype({
                'shares': 'float64',
                'cost': 'float64',
            })
            self.portfolio.from_dataframe( stock_df )
            self.last_load_modified_time = load_modified_time
            print('\n... {} |'.format(str_now()), 'loaded:', self.portfolio_load_file, load_modified_time)
            if self.verbose:
                stock_df['price'] = self.market.get_real_price(stock_df['symbol'].tolist())
                stock_df['value'] = stock_df['price'] * stock_df['shares']
                print(stock_df)

    def before_day(self):
        super().before_day()
        self.load_portoflio_from_file()

    def after_day(self):
        super().after_day()

    def before_tick(self):
        super().before_tick()

    def after_tick(self):
        super().after_tick()

        if os.path.isfile(self.portfolio_load_file):
            load_modified_time = get_file_modify_time(self.portfolio_load_file)
            need_load = (load_modified_time > self.last_load_modified_time)
            if need_load:
                self.load_portoflio_from_file()

