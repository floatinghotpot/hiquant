# -*- coding: utf-8; py-indent-offset:4 -*-

import pandas as pd

from .stock import Stock

class Portfolio:
    market = None
    available_cash = 0.0
    positions = {}
    history = {}

    def __init__(self, market):
        self.market = market
        self.available_cash = 0.0
        self.positions = {}
        self.history = {}

    def total_value(self):
        market = self.market
        value = self.available_cash
        for symbol, stock in self.positions.items():
            value += stock.shares * market.get_price(symbol)
        return value

    def to_dataframe(self, use_real_price = True):
        market = self.market

        table = [['cash', '-', self.available_cash, 1.0]]
        for symbol, stock in self.positions.items():
            shares = stock.shares
            cost = stock.cost
            if use_real_price:
                adjust_factor = 1.0 / market.get_adjust_factor(symbol)
                cost = round(cost * adjust_factor, 3)
                shares = int(shares / adjust_factor)
            row = [symbol, stock.name, shares, cost]
            table.append(row)

        return pd.DataFrame(table,columns=['symbol','name','shares','cost'])

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
