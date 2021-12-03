
## Hiquant

[阅读此文档的中文版本](https://github.com/floatinghotpot/hiquant/blob/master/README_zh.md)

Hiquant is an out-of-box tool and framework for quantitative trading and study.

It can run on any OS with Python 3, suggest Python v3.7+. 

This software is developed on Mac, and the examples in this document are written with Mac environment. They are similiar for Linux, but might be a little difference on Windows.

## Features

![Hiquant system architecture](https://github.com/floatinghotpot/hiquant/raw/master/docs/hiquant.png)

- **Data acquisition**: fetch data from financial websites, including indices, stocks, funds, financial reports, history data, realtime data, etc.
- **Valuation analysis**: extract key abstract info from financial reports like ROE, calculate PE/PB percentiles, find “cheap valuation” stocks, export to stock pool
- **Plot stock with indicators**: plot k-line diagram of stocks with indicators, comparing earning curve of multiple indices or even multiple stocks
- **Strategy framework**: with some trading strategy codes for demo purposes, and provides a command to create a new strategy from the template, which is convenient for users to write their own strategies
- **Simulated backtrade**: Use historical market data to simulate backtesting of one or more portfolio strategies, output data analysis of investment returns, and draw yield curves for comparison
- **Simulated realtime trading**: Synchronize real-time market data, calculate trading decisions based on strategies, and send email notifications to remind users to trade
- **Multi markets**: currently supports China, Hong Kong and United States market, will add support for markets in other countries
- **TODO: Automated trading**: call the quantitative trading interface to realize automated trading (not yet implemented, planned)

Other features:
- **Evalute funds**: evaluate funds, plot diagram of funds, comparing earning curve of multiple funds

## Installation

Please make sure your Python is v3.7 or above, as it's required by Matplotlib 3.4 for plottting.

```bash
python3 --version
python3 -m pip install hiquant
```

Or, clone from GitHub:
```bash
git clone https://github.com/floatinghotpot/hiquant.git
cd hiquant
python3 -m pip install -e .
```

## Command quick start

```bash
hiquant create myProj
cd myProj

hiquant index list us
hiquant stock list us

hiquant stock plot AAPL -ma -macd -kdj
hiquant stock plot AAPL -all
hiquant stock plot AAPL -wr -bias -mix

hiquant stock pool AAPL GOOG AMZN TSLA MSFT -out=stockpool/mystocks.csv

hiquant strategy create strategy/mystrategy.py
hiquant backtest strategy/mystrategy.py

hiquant trade create etc/myfund.conf
hiquant backtrade etc/myfund.conf
hiquant run etc/myfund.conf
```

## Code quick start

```python
import pandas as pd
import hiquant as hq

class MyStrategy( hq.BasicStrategy ):
    def __init__(self, fund):
        super().__init__(fund, __file__)
        self.max_stocks = 10
        self.max_weight = 1.2
        self.stop_loss = 1 + (-0.10)
        self.stop_earn = 1 + (+0.20)

    def select_targets(self):
        return ['AAPL', 'MSFT', 'AMZN', 'TSLA', '0700.HK']

    def gen_trade_signal(self, symbol, init_data = False):
        market = self.fund.market
        if init_data:
            df = market.get_daily(symbol)
        else:
            df = market.get_daily(symbol, end = market.current_date, count = 26+9)

        dif, dea, macd_hist = hq.MACD(df.close, fast=12, slow=26, signal=9)
        return pd.Series( hq.CROSS(dif, dea), index=df.index )

    def get_signal_comment(self, symbol, signal):
        return 'MACD golden cross' if (signal > 0) else 'MACD dead cross'

def init(fund):
    strategy = MyStrategy(fund)

if __name__ == '__main__':
    backtest_args = dict(
        #start_cash= 1000000.00,
        #date_start= hq.date_from_str('3 years ago'),
        #date_end= hq.date_from_str('yesterday'),
        #out_file= 'output/demo.png',
        #parallel= True,
        compare_index= '^GSPC',
    )
    hq.backtest_strategy( MyStrategy, **backtest_args )
```

## Usage

Read following docs for more details:
- [How to use hiquant tool](https://github.com/floatinghotpot/hiquant/blob/master/docs/README.md)

## Develop with Hiquant

Read this document on how to develop with Hiquant:
- [How to develop with Hiquant](https://github.com/floatinghotpot/hiquant/blob/master/docs/DEV.md)

## Screenshots

- Draw stock indicators and yield curve
```bash
hiquant stock AAPL -ma -macd
```
![Draw stock](https://github.com/floatinghotpot/hiquant/raw/master/docs/draw_stock_1.png)

- Draw trade signal of mixed indicators, holding time, and yield curve
```bash
hiquant stock AAPL -ma -macd -mix
```
![Draw stock](https://github.com/floatinghotpot/hiquant/raw/master/docs/draw_stock_2.png)

- Backtrade with one portoflio
![Draw stock](https://github.com/floatinghotpot/hiquant/raw/master/docs/back_trade.png)

- Backtrade with multiple portoflios
![Draw stock](https://github.com/floatinghotpot/hiquant/raw/master/docs/multi_funds.png)

- Compare ROI of multiple stocks
```bash
hiquant stock plot AAPL GOOG AMZN -years=5 "-base=^IXIC,^GSPC"
```
![Compore stocks](https://github.com/floatinghotpot/hiquant/raw/master/docs/cmp_us_stocks.png)

## Credits

Great appreciate developers of following projects. This project is based on their great works: Pandas, Matplotlib, Mplfinance, Akshare, etc.

Thanks folloowing websites for providing data service: Sina, Legu, Yahoo, Nasdaq, etc.

Thanks the warm-hearted knowledge sharing on Zhihu and Baidu websites.

## Disclaimer

This software and related codes are for research purposes only and do not constitute any investment advice.

If anyone invests money in actual investment based on this, please bear all risks by yourself.
