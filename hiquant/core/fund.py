# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import importlib.util
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

from ..utils import earn_to_annual
from .order_cost import get_order_cost, OrderCost
from .agent_simulated import SimulatedAgent
from .lang import LANG
from .data_cache import get_all_symbol_name, get_symbol_name

class Fund:
    market = None
    trader = None
    conf = None
    fund_name = 'No Name'
    strategy_list = None
    agent = None
    stat_df = None

    verbose = False

    stat_file = None
    plot_file = None
    compare_index = None

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

    def set_stat_file(self, stat_file):
        self.stat_file = stat_file

    def set_plot_file(self, plot_file):
        self.plot_file = plot_file

    def set_compare_index(self, compare_index):
        self.compare_index = compare_index

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
            self.set_agent(SimulatedAgent(self.market), OrderCost())

        # for backtrade, we force to use simulated agent
        if (not realtime_trade) and (self.agent.agent_type != 'simulated'):
            self.set_agent(SimulatedAgent(self.market), self.agent.order_cost)

        self.agent.init_portfolio( self.start_cash )

        self.max_value = self.agent.get_portfolio().total_value()

        columns = ['buy', 'sell', 'value', 'cash', 'position', 'drawdown']
        self.stat_df = pd.DataFrame([], columns = columns, index = pd.to_datetime([]))
        self.stat_df.index.name = 'date'
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
        row = [
            buy_count,
            - sell_count,
            value,
            portfolio.available_cash,
            (value - portfolio.available_cash) / value,
            (value / self.max_value -1),
        ]

        if date is None:
            date = self.market.current_date

        self.stat_df.loc[ pd.to_datetime(date) ] = pd.Series(row, self.stat_df.columns)

        if self.stat_file is not None:
            df = self.stat_df
            df.to_csv(self.stat_file, index= True)

        if (self.stat_df.shape[0] > 1) and (self.plot_file is not None):
            self.plot(out_file= self.plot_file)

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

    def get_report(self):
        return {
            'name': self.fund_name,
            'summary': self.get_summary(),
            'stat': self.stat_df,
        }

    def print_report(self, report = None):
        if report is None:
            report = self.get_report()

        if type(report) != list:
            report = [ report ]

        summary_df = pd.DataFrame()
        for fund in report:
            symmary = fund['summary']
            if summary_df.shape[0] == 0:
                summary_df = pd.DataFrame([], columns = list(symmary.keys()))
            summary_df = summary_df.append(symmary, ignore_index = True)

        summary_df = summary_df.T
        summary_df.index.name = ''
        summary_df.columns.name = ''
        summary_df.index = summary_df.index.str.pad(15, side='left')

        print('-' * 80)
        print(summary_df)
        print('-' * 80)

    def plot(self, report = None, compare_index = None, out_file= None):
        if report is None:
            report = self.get_report()

        if type(report) != list:
            report = [ report ]

        dates = report[0]['stat'].index
        date_start = min(dates)
        date_end = max(dates)

        df = pd.DataFrame([], index=pd.date_range(start=date_start, end=date_end))
        for fund in report:
            fund_name = fund['name']
            stat_df = fund['stat']

            value = stat_df['value']
            df[ fund_name + '.' ] = (value / value.iloc[0] - 1) * 100.0
            df[ fund_name + ':'] = stat_df['drawdown'] * 100
            df[ fund_name + ','] = stat_df['position'] * 100
            df.index = stat_df.index

            # if only one strategy, we also plot the buy/sell
            if len(report) == 1:
                df['buy'] = stat_df['buy']
                df['sell'] = stat_df['sell']

        if compare_index is None:
            compare_index = self.compare_index

        if compare_index:
            symbol_name = get_all_symbol_name()
            compare_index_name = symbol_name[ compare_index ] if (compare_index in symbol_name) else get_symbol_name(compare_index)

            cmp_value = self.market.get_index_daily(compare_index, start=date_start, end=date_end)['close']
            cmp_value = (cmp_value / cmp_value.iloc[0] -1) * 100.0

            df[ compare_index_name ] = cmp_value

        df.dropna(inplace=True)
        df.index = df.index.strftime('%Y-%m-%d')

        plt.rcParams['font.sans-serif'] = ['SimHei'] # Chinese font
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams["axes.unicode_minus"] = False

        if len(report) > 1:
            plot_rows = 3
            grid_ratios = [3, 1, 1]
        else:
            plot_rows = 4
            grid_ratios = [3, 1, 1, 1]

        fig, axes = plt.subplots(nrows = plot_rows, gridspec_kw = {'height_ratios': grid_ratios})

        fund_list = []
        pos_list = []
        drawdown_list = []
        for k in df.columns:
            if k.endswith('.'):
                fund_list.append(k)
            elif k.endswith(':'):
                drawdown_list.append(k)
            elif k.endswith(','):
                pos_list.append(k)

        fund_list.append( compare_index_name )
        df[ fund_list ].plot(ax=axes[0], figsize = (10,6), grid = True, sharex=axes[0], label = 'date', ylabel = LANG('return(%)'), title = LANG('quantitative backtesting'))

        if len(report) == 1:
            ax_id = plot_rows -3
            axes[ax_id].set_ylabel(LANG('trade'))
            axes[ax_id].bar(df.index, df.buy, color='r')
            axes[ax_id].bar(df.index, df.sell, color='g')

        df[ pos_list ].plot(ax=axes[plot_rows -2], grid = True, sharex=axes[0], ylabel = LANG('position(%)'), legend=False)
        df[ drawdown_list ].plot(ax=axes[plot_rows -1], grid = True, sharex=axes[0], ylabel = LANG('drawdown(%)'), legend=False)

        #plt.xticks(rotation=30)

        if out_file is not None:
            plt.savefig(out_file)
        else:
            plt.show()
