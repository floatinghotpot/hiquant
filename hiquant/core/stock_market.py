# -*- coding: utf-8; py-indent-offset:4 -*-

import datetime as dt
import pandas as pd

from ..utils import datetime_today, dict_from_df
from .data_cache import *
from .order_cost import *

class Market:
    adjust = 'hfq'

    all_symbol_name = {}
    watching_symbols = []

    symbol_daily = {}
    symbol_adjust_factor = {}
    symbol_daily_adjusted = {}

    verbose = False

    date_start = None
    date_end = None
    current_date = None
    current_time = None

    def is_open(self):
        #return True
        now = dt.datetime.now()
        wday = now.weekday() +1
        # monday to friday, 9:00 - 15:00 treat as open time
        return (wday>=1) and (wday<=5) and (now.hour>=9 and now.hour<15)

    def __init__(self, start, end, adjust = 'hfq'):
        self.date_start = start
        self.date_end = end

        self.all_symbol_name = dict_from_df(get_all_stock_list_df(), 'symbol', 'name')

        self.adjust = adjust
        self.last_spot_time = dt.datetime.now() - dt.timedelta(minutes =10)

        self.default_order_cost = OrderCost(0.001, 0.0003, 0.0003, 5.0)
        self.symbol_order_cost = {}

    def load_history_price(self, symbol):
        if symbol.startswith('sh') or symbol.startswith('sz'):
            df = get_daily( symbol )
            self.symbol_daily[ symbol ] = df
            self.symbol_daily_adjusted[ symbol ] = df
        else:
            df = get_daily( symbol )
            factor_df = get_daily_adjust_factor( symbol )

            self.symbol_daily[ symbol ] = df
            self.symbol_adjust_factor[ symbol ] = factor_df

            if (self.adjust == 'hfq' or self.adjust == 'qfq'):
                self.symbol_daily_adjusted[ symbol ] = adjust_daily_with_factor(df, factor_df, self.adjust)
            else:
                self.symbol_daily_adjusted[ symbol ] = df

    def watch(self, symbols):
        for symbol in symbols:
            if not (symbol in self.watching_symbols):
                self.watching_symbols.append(symbol)
                self.load_history_price(symbol)

    def keep_daily_uptodate(self):
        for symbol in self.watching_symbols:
            self.load_history_price( symbol )

    def update_daily_realtime(self, verbose = False):
        if not self.is_open():
            return

        now = dt.datetime.now()
        data_updated = False

        # if the spot out of date, update for all stocks under watch
        next_spot_time = self.last_spot_time + dt.timedelta(seconds=10)
        if now > next_spot_time:
            spot_df = get_stock_spot(self.watching_symbols, verbose)
            if verbose:
                print(spot_df)
            self.last_spot_time = now

            today = datetime_today()
            for i, spot_row in spot_df.iterrows():
                symbol = spot_row['symbol']
                adjust_factor = self.symbol_adjust_factor[ symbol ]['factor'].iloc[-1]
                spot_date = spot_row['date']

                data_updated = (spot_date >= today)

                new_row = self.symbol_daily[ symbol ].iloc[-1].copy()
                for k in ['open', 'high', 'low', 'close', 'volume']:
                    new_row[ k ] = spot_row[ k ]
                self.symbol_daily[ symbol ].loc[spot_date] = new_row

                new_row_adjusted = new_row.copy()
                if (self.adjust == 'hfq' or self.adjust == 'qfq'):
                    for k in ['open', 'high', 'low', 'close']:
                        new_row_adjusted[ k ] *= adjust_factor
                self.symbol_daily_adjusted[ symbol ].loc[spot_date] = new_row_adjusted

        return data_updated

    def get_index_daily(self, symbol, start = None, end = None, count = None):
        if end is None:
            end = self.date_end
        if start is None:
            start = self.date_start - dt.timedelta(days=90)
        df = get_index_daily( symbol )

        if start:
            df = df[ pd.to_datetime(start) : ]
        if end:
            df = df[ : pd.to_datetime(end) ]
        if count:
            df = df.iloc[ -count : ]

        return df

    def get_daily(self, symbol, start = None, end = None, count = None):
        if end is None:
            end = self.date_end
        if start is None:
            start = self.date_start - dt.timedelta(days=90)

        if not symbol in self.watching_symbols:
            self.watch([ symbol ])
            if end and (end >= datetime_today()):
                self.update_daily_realtime()

        df = self.symbol_daily_adjusted[ symbol ]

        if start:
            df = df[ pd.to_datetime(start) : ]
        if end:
            df = df[ : pd.to_datetime(end) ]
        if count:
            df = df.iloc[ -count : ]

        return df

    def get_spot(self, symbol, date = None):
        if date is None:
            date = self.current_date
        df = self.get_daily(symbol, end = date, count = 1)
        if df.shape[0] > 0:
            return df.iloc[-1]
        else:
            return False

    def get_price(self, symbol, date = None):
        if date is None:
            date = self.current_date
        df = self.get_daily(symbol, end = date, count = 1)
        if df.shape[0] > 0:
            return df.iloc[-1]['close']
        else:
            print(date, 'not trading day')
            return 0

    def get_real_price(self, symbol, date = None):
        if date is None:
            date = self.current_date
        if not symbol in self.watching_symbols:
            self.watch([ symbol ])
            today = datetime_today()
            if date and (date >= today):
                self.update_daily_realtime()
        df = self.symbol_daily[ symbol ]
        df = df[:date]
        if df.shape[0] > 0:
            return df['close'].iloc[-1]
        else:
            print(date, 'not trading day')
            return 0

    def get_adjust_factor(self, symbol, date = None):
        if date is None:
            date = self.current_date
        if not symbol in self.watching_symbols:
            self.watch([ symbol ])
            today = datetime_today()
            if date and (date >= today):
                self.update_daily_realtime()
        factor_df = self.symbol_adjust_factor[ symbol ]
        df = factor_df[:date]
        factor =  df['factor'].iloc[-1] if (df.shape[0] > 0) else False
        if not factor:
            print(factor_df)
        return factor

    def get_name(self, symbol):
        if symbol in self.all_symbol_name:
            return self.all_symbol_name[ symbol ]
        else:
            return ''

    def allow_trading(self, symbol, date = None):
        if date is None:
            date = self.current_date
        if not symbol in self.watching_symbols:
            self.watch([ symbol ])
            today = datetime_today()
            if date >= today:
                self.update_daily_realtime()

        df = self.symbol_daily_adjusted[ symbol ]
        return date in df.index

    def get_all_trading_dates(self):
        date_set = ()
        for symbol, df in self.symbol_daily.items():
            date_set |= set(df.index)
        dates = list(date_set)
        dates.sort()
        return dates
