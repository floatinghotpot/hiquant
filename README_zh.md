
## HiQuant

[Read English version of this document](https://github.com/floatinghotpot/hiquant/blob/master/README.md)

Hiquant 是一个用 Python 开发的 辅助股票投资的技术框架，以及一个开箱即用的命令行工具。

可以运行于任何支持 Python 的操作系统。建议 Python 3.7 以上。

本项目开发于 Mac 环境，因此本文的一些示范说明用于 Mac 环境，Linux 也差不多，Windows 可能有少量差异。

## 功能

![Hiquant system architecture](https://github.com/floatinghotpot/hiquant/raw/master/docs/hiquant.png)

- **数据获取**：从 交易所和财经网站 获取 财报、历史行情、实时行情数据、PE/PB数据
- **价值分析**：从 财报 提取关键财务数据，计算 年利润、ROE、净资产增长率 等指标，根据指定过滤条件，筛选出 “价值投资” 的股票
- **估值分析**：从 PE/PB 数据计算 PE/PB 百分位等，根据指定过滤条件，筛选出 “估值便宜” 的股票
- **股票池**：包含一个创建 “股票池” csv 文件的命令，并提供 合并、去除、交集 等操作
- **策略池**：包含一些 demo 用途的交易策略代码，并提供一个从模版创建 新策略 的命令，便于用户编写自己的策略
- **多投资组合**：包含一些 demo 用途的基金策略配置，并提供一个从模版创建 新配置 的命令
- **模拟回测**：用历史行情数据，对 1个或者多个 投资组合的策略进行 模拟回测，输出投资回报的数据分析，并绘制收益率曲线 进行对比
- **盯盘提醒**：同步实时行情，根据策略计算交易决策，发送 邮件通知 提醒用户交易
- **全球市场**：现已支持 中国市场（A股 和 港股）和 美国市场，将增加 对其他国家市场的 支持
- **自动化交易（计划中）**：调用量化交易接口，实现 自动化交易（尚未实现）

其他附加的功能：
- **基金收益分析**：获取基金的每日数据，绘制 单个或者多个基金的 收益曲线 对比
- **K线走势图**：绘制 股票 / 指数 的 K线图，包括绘制常见的 技术指标，以及 根据指标交易的 获利结果 对比
- **多指标组合**：绘制 K线图时，也可混合多个指标 的信号 进行交易，并显示 交易动作、持仓时间、以及收益率曲线
- **指标测试**：使用历史数据和技术指标，测试股票池中的股票，寻找出每只股票 表现最有效的技术指标

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

hiquant fund list -include=新能源 -exclude=C
hiquant fund eval 005669 000209 -years=3 -plot
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

## 如何使用

如何使用请参见 文档:
- [《如何使用 hiquant 工具》](https://github.com/floatinghotpot/hiquant/blob/master/docs/README_zh.md)

## 如何开发

如何使用请参见 
- [《如何基于 hiquant 开发》](https://github.com/floatinghotpot/hiquant/blob/master/docs/DEV.md)

## 功能截图

- 绘制股票 技术指标 和 收益率：
![Draw stock](https://github.com/floatinghotpot/hiquant/raw/master/docs/draw_stock_1.png)

- 绘制 多个技术指标的交易信号、持仓情况 以及收益率：
![Draw stock](https://github.com/floatinghotpot/hiquant/raw/master/docs/draw_stock_2.png)

- 模拟回测：
![Draw stock](https://github.com/floatinghotpot/hiquant/raw/master/docs/back_trade.png)

- 运行多个投资组合：
![Draw stock](https://github.com/floatinghotpot/hiquant/raw/master/docs/multi_funds.png)

- 比较多只股票的投资回报率
![Compore stocks](https://github.com/floatinghotpot/hiquant/raw/master/docs/cmp_cn_stocks.png)

- 比较多只基金的投资回报率
![Compore funds](https://github.com/floatinghotpot/hiquant/raw/master/docs/cmp_cn_funds.png)

## 致谢

感谢如下开源项目的开发者：pandas, matplotlib, mplfinance, akshare，没有他们的优秀工作作为基础，我恐怕无法完成这个项目。

感谢 以下网站提供的数据服务：新浪财经、乐股、雅虎、交易所网站等。

感谢 知乎、百度 上提供各种指标介绍的 热心分享者。

## 免责声明

本软件及相关代码，仅供研究用途，不构成任何投资建议。

若投入资金做实盘用途，风险自负。
