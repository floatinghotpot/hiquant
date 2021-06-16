# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import importlib.util

from ..utils import *
from .agent_simulated import *
from .agent_human import *
from .agent_master import *

class Fund:
    global_config = None
    market = None
    trader = None
    fund_id = None

    conf = {}
    fund_name = 'No Name'
    strategy = None
    agent = None
    stat_df = None

    verbose = False

    def __init__(self, global_config, market, trader, fund_id):
        self.global_config = global_config
        self.market = market
        self.trader = trader
        self.fund_id = fund_id
        self.conf = {}

    def load_module(self, strategy_file):
        mod_name = os.path.basename(strategy_file).replace('.py', '')
        mod_filepath = os.path.abspath(strategy_file)
        print('dynamically loading strategy:', mod_filepath)
        spec = importlib.util.spec_from_file_location(mod_name, mod_filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def init_fund(self, realtime_trade = False):
        for k, v in self.global_config.items( self.fund_id ):
            self.conf[k] = v

        self.fund_name = self.conf['name']
        self.strategy_file = self.conf['strategy']
        self.start_cash = float(self.conf['start_cash'])

        if realtime_trade and ('agent' in self.conf):
            #self.agent = MasterAgent(self, self.conf['agent'])
            agent_conf = {}
            for k, v in self.global_config.items( self.conf['agent'] ):
                agent_conf[k] = v
            agent_type = agent_conf['agent_type']
            if agent_type == 'simulated':
                self.agent = SimulatedAgent(self, agent_conf)
            elif agent_type == 'human':
                self.agent = HumanAgent(self, agent_conf)
            elif agent_type == 'automated':
                #self.agent = AutomatedAgent(fund, agent_conf)
                pass
        else:
            self.agent = SimulatedAgent( self, None )

        self.agent.init_portfolio( self.start_cash )

        self.max_value = self.agent.get_portfolio().total_value()

        columns = ['buy', 'sell', 'value', 'cash', 'drawdown']
        self.stat_df = pd.DataFrame([], columns = columns, index = pd.to_datetime([]))
        self.update_stat(self.market.current_date - dt.timedelta(days=1))

        mod = self.load_module( self.strategy_file )
        mod.init( self )

    def update_stat(self, date = None):
        # calculate current value of today, save to dataframe
        agent = self.agent
        portfolio = agent.get_portfolio()
        value = portfolio.total_value()
        self.max_value = max(value, self.max_value)
        buy_count, sell_count = agent.get_transaction_count()
        row = [buy_count, - sell_count, value, portfolio.available_cash, (value / self.max_value -1)]

        if date is None:
            date = self.market.current_date

        self.stat_df.loc[ pd.to_datetime(date) ] = pd.Series(row, self.stat_df.columns)

    def before_day(self):
        self.agent.before_day()

    def before_tick(self):
        self.agent.before_tick()

    def after_tick(self):
        self.agent.after_tick()

    def after_day(self):
        self.agent.after_day()
        self.update_stat()

    def get_summary(self):
        df = self.stat_df

        start_value = df.value.iloc[0]
        current_value = df.value.iloc[-1]
        earn = current_value / start_value -1

        days = (df.index[-1] - df.index[0]).days
        years = days / 365
        annual_earn = earn_to_annual(earn, days)

        return {
            'fund_id': self.fund_id,
            'fund_name': self.fund_name,
            'strategy': self.strategy.name,
            'start value': '{:,}'.format(round(start_value, 2)),
            'current value': '{:,}'.format(round(current_value, 2)),
            'invest year': round(years, 1),
            'trade count': int(sum(df.buy) - sum(df.sell)),
            'total earn': str(round(100 * earn, 2)) + ' %',
            'annual earn': str(round(100 * annual_earn, 2)) + ' %',
            'max drawdown': str(round(100 * min(df.drawdown), 2)) + ' %',
        }

    def get_stat(self):
        return self.stat_df
