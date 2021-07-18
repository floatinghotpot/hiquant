# -*- coding: utf-8; py-indent-offset:4 -*-

import datetime as dt
import pandas as pd

from ..utils import datetime_today
from .data_cache import get_all_symbol_name, get_cn_stock_fund_flow_rank, \
    get_daily, get_stock_fund_flow_daily, \
    get_stock_spot, \
    get_index_daily

class Market:
    all_symbol_name = {}
    watching_symbols = []

    symbol_daily = {}
    symbol_daily_adjusted = {}

    verbose = False

    date_start = None
    date_end = None
    current_date = None
    current_time = None

    biz_time = None
    biz_hour = (11.5 - 9.5) + (15.0 - 13.0)
    sell_rule = 'T+1'

    is_testing = False

    def __init__(self, start, end):
        self.all_symbol_name = get_all_symbol_name()
        self.watching_symbols = []
        self.symbol_daily = {}
        self.symbol_daily_adjusted = {}

        self.date_start = start
        self.date_end = end
        self.current_date = self.current_time = start
        self.last_spot_time = dt.datetime.now() - dt.timedelta(minutes =10)

        self.set_business_time(morning= ['9:30', '11:30'], afternoon= ['13:00', '15:00'])
        self.set_sell_rule(sell_rule= 'T+1')

    def set_sell_rule(self, sell_rule = 'T+1'):
        self.sell_rule = sell_rule

    def set_business_time(self, morning= ['9:30', '11:30'], afternoon= ['13:00', '15:00']):
        business_time = morning + afternoon

        biz_time = []
        for k in business_time:
            time_only = dt.datetime.strptime(k, '%H:%M')
            biz_time.append(time_only.hour + time_only.minute / 60.0)
        self.biz_time = biz_time

        morning_start, morning_end, afternoon_start, afternoon_end = self.biz_time
        self.biz_hour = (morning_end - morning_start) + (afternoon_end - afternoon_start)

    def set_verbose(self, verbose = True):
        self.verbose = verbose

    # for testing purpose
    def set_date_range(self, start, end):
        self.date_start = start
        self.date_end = end
        self.current_date = self.current_time = start

    def is_open(self) -> bool:
        if self.is_testing:
            return True

        # business hour:
        # monday to friday, 9:30 ~ 11:30, 13:00 ~ 15:00
        now = dt.datetime.now()
        wday = now.weekday() +1
        if (wday >= 1) and (wday <= 5):
            hour = now.hour + now.minute / 60.0
            morning_start, morning_end, afternoon_start, afternoon_end = self.biz_time
            if (hour >= morning_start) and (hour < morning_end):
                return True
            if (hour >= afternoon_start) and (hour < afternoon_end):
                return True

        return False

    def load_history_price(self, symbol):
        if symbol.startswith('sh') or symbol.startswith('sz'):
            df = get_index_daily( symbol )
            self.symbol_daily[ symbol ] = df
            self.symbol_daily_adjusted[ symbol ] = df
        else:
            # OHCLV
            df = get_daily( symbol )

            # fund flow
            fund_df = get_stock_fund_flow_daily( symbol )
            if fund_df is not None:
                df['main_fund'] = fund_df['main_fund']
                df['main_pct'] = fund_df['main_pct']
                df = df.fillna(0)
            self.symbol_daily[ symbol ] = df

            if 'factor' in df.columns:
                df = df.copy()
                for k in ['open', 'close', 'high', 'low']:
                    df[k] = df[k] * df['factor']
            self.symbol_daily_adjusted[ symbol ] = df

    def watch(self, symbols):
        for symbol in symbols:
            if not (symbol in self.watching_symbols):
                self.watching_symbols.append(symbol)
                self.load_history_price(symbol)

    def keep_daily_uptodate(self):
        for symbol in self.watching_symbols:
            self.load_history_price( symbol )

    def update_fundflow_realtime(self, verbose = False) -> pd.DataFrame:
        today = pd.to_datetime( datetime_today() )

        # merge fund flow data into df
        fund_df = get_cn_stock_fund_flow_rank()
        fund_df = fund_df[ fund_df.symbol.isin(self.watching_symbols) ]
        fund_df = fund_df.sort_values(by='main_pct', ascending=False).reset_index(drop= True)
        if verbose:
            print('')
            print(fund_df)

        for i, fund_row in fund_df.iterrows():
            symbol = fund_row['symbol']
            if symbol not in self.watching_symbols:
                continue
            df = self.symbol_daily_adjusted[ symbol ]
            if today in df.index:
                if 'main_pct' in df.columns:
                    df.loc[ today ]['main_pct'] = fund_row['main_pct']
                if 'main_fund' in df.columns:
                    df.loc[ today ]['main_fund'] = fund_row['main_fund']

        return fund_df

    def update_daily_realtime(self, verbose = False) -> bool:
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
                spot_date = spot_row['date'] if ('date' in spot_row) else today
                if spot_date >= today:
                    data_updated = True

                    symbol = spot_row['symbol']

                    new_row = self.symbol_daily[ symbol ].iloc[-1].copy()
                    for k in ['open', 'high', 'low', 'close', 'volume']:
                        if k in spot_row:
                            new_row[ k ] = spot_row[ k ]
                    self.symbol_daily[ symbol ].loc[spot_date] = new_row

                    if 'factor' in new_row:
                        new_row = new_row.copy()
                        adjust_factor = new_row['factor']
                        for k in ['open', 'high', 'low', 'close']:
                            new_row[ k ] = new_row[ k ] * adjust_factor
                    self.symbol_daily_adjusted[ symbol ].loc[spot_date] = new_row

        self.update_fundflow_realtime(verbose= verbose)

        return data_updated

    def get_index_daily(self, symbol, start = None, end = None, count = None) -> pd.DataFrame:
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
            df = df.tail(count)

        return df

    def get_daily(self, symbol, start = None, end = None, count = None) -> pd.DataFrame:
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
            df = df.tail(count)

        return df

    def get_spot(self, symbol, date = None) -> pd.Series:
        if date is None:
            date = self.current_date

        df = self.get_daily(symbol, end = date, count = 1)

        if df.shape[0] > 0:
            return df.iloc[-1]
        else:
            return None

    def get_time_factor(self) -> float:
        cur_hour = self.current_time.hour + self.current_time.minute / 60.0

        # convert to valid biz time
        morning_start, morning_end, afternoon_start, afternoon_end = self.biz_time
        cur_hour = min(max(cur_hour, morning_start), afternoon_end)
        if (cur_hour > morning_end) and (cur_hour < afternoon_start):
            cur_hour = afternoon_start

        hour = (cur_hour - morning_start) if (cur_hour <= morning_end) else (cur_hour - afternoon_start + (morning_end - morning_start))
        return hour / self.biz_hour

    def get_price(self, symbol, date = None) -> float:
        if date is None:
            date = self.current_date

        if type(symbol) == list:
            return [self.get_price(sym) for sym in symbol]

        if symbol == 'cash':
            return 1.0

        # adjusted daily
        df = self.get_daily(symbol, end = date, count = 1)

        if df.shape[0] > 0:
            row = df.iloc[-1]
            close_price = row['close']
            if self.current_time > datetime_today():
                return close_price
            else:
                open_price = row['open']
                # assume the price change is function of time, either linear, quadratic, or cubic
                f = 1 - self.get_time_factor()
                price = close_price - (close_price - open_price) * (f * f * f)
                return price
        else:
            print(date, 'not trading day')
            return 0

    def get_real_price(self, symbol, date = None) -> float:
        if date is None:
            date = self.current_date

        if type(symbol) == list:
            return [self.get_real_price(sym) for sym in symbol]

        if symbol == 'cash':
            return 1.0

        if not symbol in self.watching_symbols:
            self.watch([ symbol ])
            today = datetime_today()
            if date and (date >= today):
                self.update_daily_realtime()

        df = self.symbol_daily[ symbol ]
        df = df[:date]

        if df.shape[0] > 0:
            row = df.iloc[-1]
            close_price = row['close']
            if self.current_time > datetime_today():
                return close_price
            else:
                open_price = row['open']
                # assume the price change is function of time, either linear, quadratic, or cubic
                f = 1 - self.get_time_factor()
                price = close_price - (close_price - open_price) * f * f * f
                return price
        else:
            print(date, 'not trading day')
            return 0

    def get_adjust_factor(self, symbol, date = None) -> pd.Series:
        df = self.get_daily(symbol, end = date, count = 1)
        factor =  df['factor'].iloc[-1] if (df.shape[0] > 0) else False
        if not factor:
            print(df)
        return factor

    def get_name(self, symbol) -> str:
        if symbol in self.all_symbol_name:
            return self.all_symbol_name[ symbol ]
        else:
            return ''

    def allow_trading(self, symbol, date = None) -> bool:
        if date is None:
            date = self.current_date
        df = self.symbol_daily_adjusted[ symbol ]
        return pd.to_datetime(date) in df.index

    def get_all_trading_dates(self) -> list:
        date_set = ()
        for symbol, df in self.symbol_daily.items():
            date_set |= set(df.index)
        dates = list(date_set)
        dates.sort()
        return dates

    def get_main_fundflow_rank(self, symbols) -> pd.DataFrame:
        if self.current_date >= datetime_today():
            # get the fund flow ranking from web for today
            df = self.update_fundflow_realtime()
            df = df[ df['symbol'].isin(symbols) ]
            df = df[['symbol','main_pct', 'main_fund']]
        else:
            # or, merge them from history data
            table = []
            for symbol in symbols:
                if not symbol in self.watching_symbols:
                    self.watch([ symbol ])
                main_pct, main_fund = 0.0, 0.0
                if symbol in self.symbol_daily_adjusted:
                    daily_df = self.symbol_daily_adjusted[ symbol ]
                    the_date = pd.to_datetime(self.current_date)
                    if the_date in daily_df.index:
                        row = daily_df.loc[ the_date ]
                        main_pct, main_fund = row['main_pct'], row['main_fund']
                else:
                    print('symbol not in symbol_daily_adjusted:', symbol)
                row = [symbol, main_pct, main_fund]
                table.append(row)

            df = pd.DataFrame(table, columns=['symbol', 'main_pct', 'main_fund'])

        # now sort by main fundflow percentage
        df = df.sort_values(by='main_pct', ascending= False).reset_index(drop= True)
        return df

    def get_main_fundflow(self, symbol) -> set:
        if symbol in self.symbol_daily_adjusted:
            daily_df = self.symbol_daily_adjusted[ symbol ]
            the_date = pd.to_datetime( self.current_date )
            if the_date in daily_df.index:
                row = daily_df.loc[ the_date ]
                if ('main_pct' in row) and ('main_fund' in row):
                    return (row['main_pct'], row['main_fund'])
        return (0.0, 0.0)
