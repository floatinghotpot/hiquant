# -*- coding: utf-8; py-indent-offset:4 -*-

import datetime as dt
import time

from ..utils import datetime_today
from .fund import Fund

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

    def run_daily(self, func, context, time='09:30'):
        time_only = dt.datetime.strptime(time, '%H:%M')
        time = time_only.strftime('%H:%M')

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
        return [fund.get_report() for fund in self.funds]

    def print_report(self, report = None):
        if report is None:
            report = self.get_report()

        fund = self.funds[0] if (len(self.funds) > 0) else Fund(self.market, self)
        fund.print_report(report= report)

    def plot(self, report = None, compare_index = None, out_file= None):
        if report is None:
            report = self.get_report()

        fund = self.funds[0] if (len(self.funds) > 0) else Fund(self.market, self)
        fund.plot(report= report, compare_index= compare_index, out_file= out_file)
