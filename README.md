
## Hiquant

[阅读此文档的中文版本](https://github.com/floatinghotpot/hiquant/blob/master/README_zh.md)

Hiquant is an out-of-box toolset for assiting stock investment and a library for study on quantitative trading.

It can run on any OS with Python 3, suggest Python v3.7+. 

This software is developed on Mac, and the examples in this document are written with Mac environment. They are similiar for Linux, but might be a little difference on Windows.

## Features

- Data acquisition: Obtain the list of stocks and indices, and obtain financial reports, historical market quotations, real-time market data, and PE/PB data from financial websites
- Value analysis: extract key financial data from financial reports, calculate annual profit, ROE, net asset growth rate and other indicators, and screen out "value investment" stocks based on specified filter conditions
- Valuation analysis: Calculate PE/PB percentiles from PE/PB data, and select “cheap valuation” stocks based on specified filter conditions
- Stock pool: Contains a command to create a "stock pool" csv file, and provides operations such as merging, removing, and intersection
- Strategy Pool: Contains some trading strategy codes for demo purposes, and provides a command to create a new strategy from the template, which is convenient for users to write their own strategies
- Multi-portfolio: Contains some fund strategy configurations for demo purposes, and provides a command to create a new configuration from the template
- Simulated backtesting: Use historical market data to simulate backtesting of one or more portfolio strategies, output data analysis of investment returns, and draw yield curves for comparison
- Tracking reminder: Synchronize real-time market data, calculate trading decisions based on strategies, and send email notifications to remind users to trade
- TODO: Automated trading: call the quantitative trading interface to realize automated trading (not yet implemented, planned)
- TODO: Global market: currently only supports China’s A-share market, and will increase support for markets in other countries (not yet implemented, planned)

Other additional features:
- K-line chart: draw the K-line chart of stocks/indices, including drawing common technical indicators, and comparing the profit results of trading based on the indicators
- Multi-indicator combination: When drawing a K-line chart, you can also mix signals from multiple indicators for trading, and display trading actions, holding time, and yield curve
- K-line patterns: graphically display the 61 K-line patterns provided by TALib, count the number of occurrences of each pattern in the local daily data, and verify the correctness of these patterns for trend prediction
- Indicator test: Use historical data and technical indicators to test the stocks in the stock pool and find the most effective technical indicators for each stock

## Installation

```bash
pip install hiquant
```

Or, clone from GitHub:
```bash
git clone https://github.com/floatinghotpot/hiquant.git
cd hiquant
pip install -e .
```

## Quick start

```bash
hiquant create myFund
cd myFund

hiquant list stock
hiquant list index

hiquant stock 600036 -ma -macd -kdj
hiquant stock 600519 -all
hiquant stock 600036 -wr -bias -mix

hiquant stockpool create stockpool/mystocks.csv 600036 600519 600276 300357 002258
hiquant finance view stockpool/mystocks.csv
hiquant pepb view stockpool/mystocks.csv

hiquant strategy create strategy/mystrategy.py
hiquant fund create etc/myfund.conf
hiquant fund backtrade etc/myfund.conf
```

## Usage

Read following docs for more details:
- [How to use hiquant tool](https://github.com/floatinghotpot/hiquant/blob/master/docs/README.md)
- [Hiquant commands referrence](https://github.com/floatinghotpot/hiquant/blob/master/docs/CMD.md)

## Develop with Hiquant

Read this document on how to develop with Hiquant:
- [How to develop with Hiquant](https://github.com/floatinghotpot/hiquant/blob/master/docs/DEV.md)

## Screenshots

Draw stock indicators and yield curve
```bash
hiquant stock 600036 -ma -macd -kdj
```
![Draw stock](https://github.com/floatinghotpot/hiquant/raw/master/docs/draw_stock_1.png)

Draw trade signal of mixed indicators, holding time, and yield curve
```bash
hiquant stock 600036 -wr -bias -mix
```
![Draw stock](https://github.com/floatinghotpot/hiquant/raw/master/docs/draw_stock_2.png)

Backtrade with one portoflio
![Draw stock](https://github.com/floatinghotpot/hiquant/raw/master/docs/back_trade.png)

Backtrade with multiple portoflios
![Draw stock](https://github.com/floatinghotpot/hiquant/raw/master/docs/multi_funds.png)

## Credits

Great appreciate developers of following projects. This project is based on their great works: Pandas, Matplotlib, Mplfinance, Akshare, etc.

Thanks SINA financial and Legu for providing data service from their websites.

Thanks the warm-hearted knowledge sharing on Zhihu and Baidu websites.

## Disclaimer

This software and related codes are for research purposes only and do not constitute any investment advice.

If anyone invests money in actual investment based on this, please bear all risks by yourself.
