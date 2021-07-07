# -*- coding: utf-8; py-indent-offset:4 -*-

import pandas as pd
import datetime as dt
import time
import matplotlib.pyplot as plt

from ..utils import datetime_today
from .data_cache import get_all_symbol_name, get_symbol_name

class Callback:
    context = None
    func = None
    called = False
    def __init__(self, func, context):
        self.context = context
        self.func = func
        self.called = False

class Trader:
    market = None
    date_start = None
    date_end = None

    timer_callbacks = {}
    bar_callbacks = []
    funds = []

    verbose = False

    def __init__(self, market):
        self.market = market
        self.date_start = market.date_start
        self.date_end = market.date_end
        self.funds = []
        self.bar_callbacks = []
        self.timer_callbacks = {}

    def set_verbose(self, verbose = True):
        self.verbose = verbose
        for fund in self.funds:
            fund.set_verbose(verbose)

    def run_daily(self, func, context, time='open'):
        # map to time
        _run_time = {
            'before_open': '7:00',
            'open': '9:30',
            'after_open': '10:00',
            'before_close': '14:30',
            'after_close': '16:00',
        }
        for k in _run_time:
            if time == k:
                time = _run_time[k]

        if time in self.timer_callbacks:
            callback_list = self.timer_callbacks[ time ]
            callback_list.append( Callback(func, context) )
        else:
            self.timer_callbacks[ time ] = [ Callback(func, context) ]

    def run_on_bar_update(self, func, context):
        self.bar_callbacks.append( Callback(func, context) )

    def add_fund(self, fund):
        self.funds.append(fund)

    def run_fund(self, date_start, date_end, tick_period = 300):
        market = self.market
        self.date_start = date_start
        self.date_end = date_end

        market.current_time = market.current_date = date = date_start
        for fund in self.funds:
            fund.init_fund( date_end >= datetime_today() )

        while date < date_end:
            # print the date at bottom of screen, but do not change line
            #if not fund.verbose:
            print('\r... {} ...'.format(date.strftime('%Y-%m-%d %H:%M:%S')), end='', flush=True)

            next_date = min(date + dt.timedelta(days=1), date_end)

            for fund in self.funds:
                fund.before_day()

            # init timer for the day, convert str to real time value
            timers = {}
            for k in self.timer_callbacks:
                time_only = dt.datetime.strptime(k, '%H:%M')
                call_time = dt.datetime(date.year, date.month, date.day, time_only.hour, time_only.minute)
                callback_list = self.timer_callbacks[ k ]
                timers[ call_time ] = callback_list
                for callback in callback_list:
                    callback.called = False

            # if the day is in the past, it's a back-trade test
            if date < datetime_today():
                timer_keys = list(timers.keys())
                timer_keys.sort()
                for k in timer_keys:
                    for fund in self.funds:
                        fund.before_tick()

                    market.current_time = k
                    callback_list = timers[k]
                    for callback in callback_list:
                        if callback.called:
                            continue
                        func = callback.func
                        func( callback.context )
                        callback.called = True

                    for fund in self.funds:
                        fund.after_tick()
            else:
                # date == today, it's realtime trade
                # wait until this day really begin
                while dt.datetime.now() < date:
                    time.sleep(1)

                # download the daily at idle time
                market.keep_daily_uptodate()

                market.current_time = dt.datetime.now()
                next_time_tick = market.current_time

                # if we run after market, we can update to get today's date
                market.update_daily_realtime( market.verbose )

                # loop until end of this day
                while market.current_time < next_date:
                    # if time to call tick
                    if market.current_time >= next_time_tick:
                        for fund in self.funds:
                            fund.before_tick()

                        if market.is_open():
                            # fetching the realtime price / volume data
                            data_updated = market.update_daily_realtime( market.verbose )
                            if data_updated:
                                # callback on bar update
                                for callback in self.bar_callbacks:
                                    func = callback.func
                                    func( callback.context )
                                pass

                        for fund in self.funds:
                            fund.after_tick()

                        next_time_tick += dt.timedelta(seconds = tick_period)

                    # callback triggered by timer
                    for k in timers:
                        if market.current_time >= k:
                            callback_list = timers[k]
                            for callback in callback_list:
                                if not callback.called:
                                    func = callback.func
                                    func( callback.context )
                                    callback.called = True

                    now_str = market.current_time.strftime('%Y-%m-%d %H:%M:%S')
                    print('\r... {} ...'.format(now_str), end = '', flush=True)
                    time.sleep(1)

                    market.current_time = dt.datetime.now()

            for fund in self.funds:
                fund.after_day()

            # move to next date
            market.current_date = date = next_date

        print('')
        pass

    def get_report(self):
        report = []
        for fund in self.funds:
            report.append({
                'name': fund.fund_name,
                'summary': fund.get_summary(),
                'stat': fund.get_stat(),
            })
        return report

    def print_report(self, report = None):
        if report is None:
            report = self.get_report()

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

        date_start = self.date_start if (self.date_start is not None) else self.market.date_start
        date_end = self.date_end if (self.date_end is not None) else self.market.date_end

        df = pd.DataFrame([], index=pd.date_range(start=date_start, end=date_end))
        for fund in report:
            fund_name = fund['name']
            stat_df = fund['stat']

            # if only one strategy, we also plot the buy/sell and drawdown
            if len(report) == 1:
                df = stat_df[['buy', 'sell', 'drawdown']]

            value = stat_df['value']
            df[ fund_name ] = (value / value.iloc[0] - 1) * 100.0
            df.index = stat_df.index

        if compare_index:
            symbol_name = get_all_symbol_name()
            compare_index_name = symbol_name[ compare_index ] if (compare_index in symbol_name) else get_symbol_name(compare_index)

            cmp_value = self.market.get_index_daily(compare_index, start=self.date_start, end=self.date_end)['close']
            cmp_value = (cmp_value / cmp_value.iloc[0] -1) * 100.0

            df[ compare_index_name ] = cmp_value

        df.dropna(inplace=True)
        df.index = df.index.strftime('%Y-%m-%d')

        plt.rcParams['font.sans-serif'] = ['SimHei'] # Chinese font
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams["axes.unicode_minus"] = False

        # now plot to visualize
        if len(report) > 1:
            # if multi strategy, we compare the performance
            df.plot(figsize = (10,6), grid = True, xlabel = 'date', ylabel = 'return (%)', title = 'performance')
            plt.show()
        else:
            # if only one strategy, we also plot the buy/sell and drawdown
            fig, axes = plt.subplots(nrows=3, gridspec_kw={'height_ratios': [3, 1, 1]})

            fund_name = report[0]['name']
            df[[fund_name, compare_index_name]].plot(ax=axes[0], figsize = (10,6), grid = True, sharex=axes[0], label = 'date', ylabel = 'return (%)', title = 'performance')

            axes[1].bar(df.index, df.buy, color='r')
            axes[1].bar(df.index, df.sell, color='g')
            axes[1].set_ylabel('trade count')

            df['drawdown'] = df['drawdown'] * 100.0
            df[['drawdown']].plot(ax=axes[2], grid = True, sharex=axes[0], ylabel = 'drawdown (%)', legend=False)

            plt.xticks(rotation=45)

            if out_file is not None:
                plt.savefig(out_file)
            else:
                plt.show()
