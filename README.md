
## HiQuant

[hiquant](https://github.com/floatinghotpot/hiquant.git) 是一组用 Python 开发的 辅助股票投资的工具。

理论上，可以运行于任何支持 Python 的操作系统。本文的一些示范说明写于 Mac 环境。

建议 Python 3.7 以上。

## 功能

[x] 数据获取：免费获取 股票、指数 列表，获取 财报、历史行情、实时行情数据、PE/PB数据
[x] 价值分析：从 财报 提取关键财务数据，计算 年利润、ROE、净资产增长率 等指标，根据指定标准，筛选出 “价值投资” 的股票
[x] 估值分析：从 PE/PB 数据计算 PE/PB 百分位等，根据指定标准，筛选出 “估值便宜” 的股票
[x] 股票池：包含一个创建 “股票池” csv 文件的命令，并提供 合并、去除、交集 等操作
[x] 策略池：包含一些 demo 用途的交易策略代码，并提供一个从模版创建 新策略 的命令，便于用户编写自己的策略
[x] 多投资组合：包含一些 demo 用途的基金策略配置，并提供一个从模版创建 新配置 的命令
[x] 模拟回测：用历史行情数据，对 1个或者多个 投资组合的策略进行 模拟回测，输出投资回报的数据分析，并绘制收益率曲线 进行对比
[x] 盯盘提醒：同步实时行情，根据策略计算交易决策，发送 邮件通知 提醒交易
[ ] 自动化交易：对接 量化交易 买卖接口，实现 自动化交易（尚未实现，计划中）
[ ] 目前仅支持 中国 A股市场，将增加 对其他国家市场的 支持

其他附带的功能：
[x] K线图：绘制 股票 / 指数 的 K线图，并可绘制常见的 技术指标，以及 根据指标交易的 获利结果 对比
[x] 多指标组合：绘制 K线图时，也可混合多个指标 的信号 进行交易，并显示 交易动作、持仓时间、回报率 轨迹
[x] K线形态图：绘制图形展示 talib 提供的 61个 K线形态，并统计在本地日线数据中 每个形态出现的次数，以及 统计预测走势的 有效性
[x] 指标测试：用根据历史数据和技术指标 测试股票池，测试出每只股票 表现最有效的 技术指标

## 如何安装

```bash
pip install hiquant
```

或者 从 GitHub 复制：
```bash
git clone https://github.com/floatinghotpot/hiquant.git
cd hiquant
pip install -e .
```

## 快速体验

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
hiquant fund create myfund.conf
hiquant fund backtrade myfund.conf
```

## 如何使用

如何使用请参见 文档:
1, [《如何使用 hiquant 工具》](docs/README.md)
2, [《 hiquant 命令集 参考》](docs/CMD.md)

## 如何开发

如何使用请参见 文档[《如何基于 hiquant 开发》](docs/DEV.md)

## 功能截图

绘制股票 技术指标 和 收益率：
![Draw stock](draw_stock_1.png)

绘制 多个技术指标的交易信号、持仓情况 以及收益率：
![Draw stock](draw_stock_2.png)

模拟回测：
![Draw stock](back_trade.png)

运行多个投资组合：
![Draw stock](multi_funds.png)

## 致谢

感谢如下开源项目的开发者：pandas, matplotlib, mplfinance, akshare，没有他们的工作作为基础，不会有这个项目。

感谢 新浪财经 和 乐股 网站提供的数据服务。

感谢 知乎、百度 上提供各种指标介绍的 热心分享者。

## 声明

本软件及相关代码，仅供研究用途，不构成任何投资建议。

若投入资金做实盘用途，风险自负。

-- 全文完 --
