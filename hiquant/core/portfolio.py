# -*- coding: utf-8; py-indent-offset:4 -*-

import pandas as pd
import tabulate as tb

from .stock import Stock

class Portfolio:
    market = None
    init_value = 0.0
    available_cash = 0.0
    positions = {}
    history = {}

    def __init__(self, market, init_cash = 0.0):
        self.market = market
        self.available_cash = init_cash
        self.positions = {}
        self.history = {}
        self.init_value = init_cash

    def count(self):
        return len(list(self.positions.keys()))

    def total_value(self):
        market = self.market
        value = self.available_cash
        for symbol, stock in self.positions.items():
            value += stock.shares * market.get_price(symbol)
        return value

    def to_dataframe(self, use_real_price = True):
        market = self.market

        table = [['cash', '-', self.available_cash, 1.0, 1.0]]
        for symbol, stock in self.positions.items():
            shares = stock.shares
            cost = stock.cost
            price = market.get_price(symbol)
            if use_real_price:
                adjust_factor = 1.0 / market.get_adjust_factor(symbol)
                cost = round(cost * adjust_factor, 3)
                shares = int(shares / adjust_factor)
            row = [symbol, stock.name, shares, cost, price]
            table.append(row)

        df = pd.DataFrame(table,columns=['symbol','name','shares','cost', 'price'])
        df['value'] = (df['price'] * df['shares']).round(2)
        total_value = sum( df['value'] )
        df['position'] = (df['value'] / total_value * 100.0).round(2)
        return df

    def from_dataframe(self, df, use_real_price = True):
        market = self.market

        self.available_cash = 0
        self.positions = {}
        self.history = {}
        for i, row in df.iterrows():
            symbol = row['symbol']
            if symbol == 'cash':
                self.available_cash = float(row['shares'])
            else:
                name = row['name']
                cost = float(row['cost'])
                shares = float(row['shares'])

                if use_real_price:
                    adjust_factor = market.get_adjust_factor(symbol)
                    cost *= adjust_factor
                    shares /= adjust_factor

                stock = Stock(symbol, name)
                stock.shares = shares
                stock.cost = cost
                self.positions[ symbol ] = stock
        self.init_value = self.total_value()

    def print(self):
        df = self.to_dataframe()
        print( tb.tabulate(df, headers='keys') )
