# -*- coding: utf-8; py-indent-offset:4 -*-

import datetime as dt
import pandas as pd

from ..utils import datetime_today
from .data_cache import get_all_symbol_name, \
    get_daily, get_daily_adjust_factor, adjust_daily_with_factor, \
    get_stock_spot, \
    get_index_daily

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

    force_open = False

    def __init__(self, start, end, adjust = 'hfq'):
        self.all_symbol_name = get_all_symbol_name()
        self.watching_symbols = []
        self.symbol_daily = {}
        self.symbol_adjust_factor = {}
        self.symbol_daily_adjusted = {}

        self.adjust = adjust
        self.date_start = start
        self.date_end = end
        self.current_date = self.current_time = start
        self.last_spot_time = dt.datetime.now() - dt.timedelta(minutes =10)

    def set_verbose(self, verbose = True):
        self.verbose = verbose

    # for testing purpose
    def set_force_open(self, force_open = True):
        self.force_open = force_open

    # for testing purpose
    def set_date_range(self, start, end):
        self.date_start = start
        self.date_end = end
        self.current_date = self.current_time = start

    def is_open(self):
        if self.force_open:
            return True

        now = dt.datetime.now()
        wday = now.weekday() +1
        # monday to friday, 9:00 - 15:00 treat as open time
        return (wday>=1) and (wday<=5) and (now.hour>=9 and now.hour<15)

    def load_history_price(self, symbol):
        if symbol.startswith('sh') or symbol.startswith('sz'):
            df = get_daily( symbol )
            self.symbol_daily[ symbol ] = df
            self.symbol_daily_adjusted[ symbol ] = df
        else:
            df = get_daily( symbol )
            self.symbol_daily[ symbol ] = df

            if (self.adjust == 'hfq' or self.adjust == 'qfq'):
                factor_df = get_daily_adjust_factor( symbol )
                self.symbol_adjust_factor[ symbol ] = factor_df
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
        now = dt.datetime.now()
        data_updated = False

        # if the spot out of date, update for all stocks under watch
        next_spot_time = self.last_spot_time + dt.timedelta(seconds=10)
        if now > next_spot_time:
            spot_df = get_stock_spot(self.watching_symbols, verbose)
            if verbose:
                print('')
                print(spot_df)
            self.last_spot_time = now

            today = pd.to_datetime( datetime_today() )
            for i, spot_row in spot_df.iterrows():
                symbol = spot_row['symbol']
                adjust_factor = self.symbol_adjust_factor[ symbol ]['factor'].iloc[-1]
                spot_date = spot_row['date'] if ('date' in spot_df.columns) else today

                data_updated = (spot_date >= today)

                new_row = self.symbol_daily[ symbol ].iloc[-1].copy()
                for k in ['open', 'high', 'low', 'close', 'volume']:
                    if k in spot_row:
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
        df = self.symbol_daily_adjusted[ symbol ]
        return pd.to_datetime(date) in df.index

    def get_all_trading_dates(self):
        date_set = ()
        for symbol, df in self.symbol_daily.items():
            date_set |= set(df.index)
        dates = list(date_set)
        dates.sort()
        return dates
