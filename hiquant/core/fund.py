# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import importlib.util
import pandas as pd
import datetime as dt

from ..utils import earn_to_annual
from .order_cost import get_order_cost, OrderCost
from .agent_simulated import SimulatedAgent

class Fund:
    market = None
    trader = None
    conf = None
    fund_name = 'No Name'
    strategy_list = None
    agent = None
    stat_df = None

    verbose = False

    def __init__(self, market, trader, fund_conf = None):
        self.market = market
        self.trader = trader
        self.conf = fund_conf if (fund_conf is not None) else {}
        self.strategy_list = []
        self.agent = None
        self.stat_df = None
        self.fund_name = ''
        self.start_cash = 0.0
        self.set_agent(SimulatedAgent(market))

    def set_verbose(self, verbose = True):
        self.verbose = verbose
        if self.agent is not None:
            self.agent.set_verbose(verbose)

    def add_strategy(self, strategy):
        if strategy not in self.strategy_list:
            self.strategy_list.append( strategy )
        pass

    def set_agent(self, agent, order_cost = None):
        self.agent = agent
        self.agent.order_cost = order_cost if (order_cost is not None) else get_order_cost()

    def load_module(self, strategy_file):
        mod_name = os.path.basename(strategy_file).replace('.py', '')
        mod_filepath = os.path.abspath(strategy_file)
        if self.verbose:
            print('dynamically loading strategy:', mod_filepath)
        spec = importlib.util.spec_from_file_location(mod_name, mod_filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def load_strategy(self, strategy_file):
        mod = self.load_module( strategy_file )
        mod.init( self )

    def set_name(self, name):
        self.fund_name = name

    def set_start_cash(self, cash):
        self.start_cash = cash

    def init_fund(self, realtime_trade = False):
        if 'name' in self.conf:
            self.fund_name = self.conf['name']
        if 'start_cash' in self.conf:
            self.start_cash = float(self.conf['start_cash'])

        if self.agent is None:
            self.set_agent(SimulatedAgent(self.market, None), OrderCost())

        # for backtrade, we force to use simulated agent
        if (not realtime_trade) and (self.agent.agent_type != 'simulated'):
            self.set_agent(SimulatedAgent(self.market, None), self.agent.order_cost)

        self.agent.init_portfolio( self.start_cash )

        self.max_value = self.agent.get_portfolio().total_value()

        columns = ['buy', 'sell', 'value', 'cash', 'drawdown']
        self.stat_df = pd.DataFrame([], columns = columns, index = pd.to_datetime([]))
        self.update_stat(self.market.current_date - dt.timedelta(days=1))

        if 'strategy' in self.conf:
            self.load_strategy( self.conf['strategy'] )

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
        if self.verbose:
            print(df)

        start_value = df.value.iloc[0]
        current_value = df.value.iloc[-1]
        earn = current_value / start_value -1

        days = (df.index[-1] - df.index[0]).days
        years = days / 365
        annual_earn = earn_to_annual(earn, days)

        return {
            'fund_name': self.fund_name,
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
