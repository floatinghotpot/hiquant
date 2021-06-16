
import pandas as pd

from .stock import *

class Portfolio:
    fund = None
    available_cash = 0.0
    positions = {}
    history = {}

    def __init__(self, fund):
        self.fund = fund
        self.available_cash = 0.0
        self.positions = {}
        self.history = {}

    def total_value(self):
        market = self.fund.market
        value = self.available_cash
        for symbol, stock in self.positions.items():
            value += stock.shares * market.get_price(symbol)
        return value

    def to_dataframe(self, use_real_price = True):
        market = self.fund.market

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

        return pd.DataFrame(table,columns=['symbol','name','amount','cost'])

    def from_dataframe(self, df, use_real_price = True):
        market = self.fund.market

        self.available_cash = 0
        self.positions = {}
        self.history = {}
        for i, row in df.iterrows():
            symbol = row['symbol']
            if symbol == 'cash':
                self.available_cash = float(row['amount'])
            else:
                name = row['name']
                cost = float(row['cost'])
                shares = float(row['amount'])

                if use_real_price:
                    adjust_factor = market.get_adjust_factor(symbol)
                    cost *= adjust_factor
                    shares /= adjust_factor

                stock = Stock(symbol, name)
                stock.shares = shares
                stock.cost = cost
                self.positions[ symbol ] = stock

    def to_csv(self, csvfile, use_real_price = True):
        df = self.to_dataframe(use_real_price)
        df.to_csv(csvfile, index=False)

    def from_csv(self, csvfile, use_real_price = True):
        df = pd.read_csv(csvfile, dtype=str)
        self.from_dataframe(df, use_real_price)
