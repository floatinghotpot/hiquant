
## HiQuant

[Read English version of this document](https://github.com/floatinghotpot/hiquant/blob/master/README.md)

Hiquant 是一个使用 Python 开发的量化交易框架 和 开箱即用的工具集，主要用于辅助股票/基金投资。有了它的帮助，炒股、买基金不再盲目，可以有效提高盈利概率。

可以运行于任何支持 Python 的操作系统。建议 Python 3.7 以上。

## 功能

- **数据获取**：从金融网站获取数据，包括指数、股票、基金、财务报告、历史数据、实时数据等。
- **估值分析**：从 ROE 等财务报告中提取关键抽象信息，计算 PE/PB 百分位数，找到“估值便宜”的股票，导出到股票池
- **用指标绘制股票**：用指标绘制股票的k线图，比较多个指数甚至多个股票的收益曲线
- **策略框架**：实现了用于回测的策略框架，附示例代码用于演示，并提供从模板创建新策略的命令，方便用户编写自己的策略
- **模拟回测**：利用历史市场数据，模拟一种或多种投资组合策略的回测，输出投资收益数据分析，绘制收益率曲线进行比较
- **模拟实时交易**：同步实时行情数据，根据策略计算交易决策，发送邮件通知提醒用户交易
- **多市场**：目前支持中国、香港和美国市场，如果有要求和数据可用，将增加对其他国家市场的支持
- **TODO：自动交易**：调用量化交易接口实现自动交易（暂未实施，计划中）

其他特性：
- **评估基金**：搜索和筛选基金，计算夏普比率和最大回撤，评估基金，比较多个基金的收益曲线，比较基金经理的投资业绩 

![Hiquant system architecture](https://github.com/floatinghotpot/hiquant/raw/master/docs/hiquant.png)

## 如何安装

请确认您的 Python 是 3.7 以上版本，因为 Matplotlib 3.4 绘图需要。

```bash
python3 --version
python3 -m pip install hiquant
```

或者 从 GitHub 复制：
```bash
git clone https://github.com/floatinghotpot/hiquant.git
cd hiquant
python3 -m pip install -e .
```

## 快速体验

```bash
hiquant create myProj
cd myProj

hiquant index list cn
hiquant stock list cn

hiquant stock plot 600036 -ma -macd -kdj
hiquant stock plot 600519 -all
hiquant stock plot 600036 -wr -bias -mix

hiquant stock pool 600036 600519 600276 300357 002258 -out=stockpool/mystocks.csv

hiquant stock eval stockpool/mystocks.csv
hiquant stock pepb stockpool/mystocks.csv

hiquant strategy create strategy/mystrategy.py
hiquant backtest strategy/mystrategy.py

hiquant trade create etc/myfund.conf
hiquant backtrade etc/myfund.conf
hiquant run etc/myfund.conf

hiquant fund list
hiquant fund list -include=新能源 -exclude=C
hiquant fund eval 005669 000209 002190 -years=3 -plot
```

## 快速开发

```python
# -*- coding: utf-8; py-indent-offset:4 -*-
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
        return ['600519','002714','603882','300122','601888','hk3690','hk9988', 'hk0700']

    def gen_trade_signal(self, symbol, init_data = False):
        market = self.fund.market
        if init_data:
            df = market.get_daily(symbol)
        else:
            df = market.get_daily(symbol, end = market.current_date, count = 26+9)

        dif, dea, macd_hist = hq.MACD(df.close, fast=12, slow=26, signal=9)
        return pd.Series( hq.CROSS(dif, dea), index=df.index )

    def get_signal_comment(self, symbol, signal):
        return 'MACD金叉' if (signal > 0) else 'MACD死叉'

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

## 功能示范

- 绘制股票 技术指标 和 收益率：
![Draw stock](https://github.com/floatinghotpot/hiquant/raw/master/docs/draw_stock_1.png)

- 绘制 多个技术指标的交易信号、持仓情况 以及收益率：
![Draw stock](https://github.com/floatinghotpot/hiquant/raw/master/docs/draw_stock_2.png)

- 比较多只股票的投资回报率
![Compore stocks](https://github.com/floatinghotpot/hiquant/raw/master/docs/cmp_cn_stocks.png)

- 模拟回测：
![Draw stock](https://github.com/floatinghotpot/hiquant/raw/master/docs/back_trade.png)

- 运行多个投资组合：
![Draw stock](https://github.com/floatinghotpot/hiquant/raw/master/docs/multi_funds.png)

- 比较多只基金的投资回报率
![Compore funds](https://github.com/floatinghotpot/hiquant/raw/master/docs/cmp_cn_funds.png)

## 如何使用

如何使用请参见 文档:
- [《如何使用 hiquant 工具》](https://github.com/floatinghotpot/hiquant/blob/master/docs/README_zh.md)

## 如何开发

如何使用请参见 
- [《如何基于 hiquant 开发》](https://github.com/floatinghotpot/hiquant/blob/master/docs/DEV.md)

## 致谢

感谢如下开源项目的开发者：pandas, matplotlib, mplfinance, akshare，没有他们的优秀工作作为基础，我恐怕无法完成这个项目。

感谢 以下网站提供的数据服务：新浪财经、乐股、雅虎、交易所网站等。

感谢 知乎、百度 上提供各种指标介绍的 热心分享者。

## 免责声明

本软件及相关代码，仅供研究用途，不构成任何投资建议。

若投入资金做实盘用途，风险自负。

本项目开发于 Mac 环境，因此本文的一些示范说明用于 Mac 环境，Linux 也差不多，Windows 可能有少量差异。

