

# 显示 帮助
```bash
hiquant
hiquant help
hiquant help <cmd>
hiquant -v --version
```

# 初始化 数据
```bash
hiquant create <folder>
cd <folder>
```

# 股票池 财务分析
```bash
hiquant finance update all

hiquant finance view all
hiquant finance show all -ipo_years=1- -earn_ttm=1.0- -roe=0.15- -3yr_grow_rate=0.15- -sortby=roe -out=good_stock.csv
```

# 股票池 PE/PB 分析
```bash
hiquant pepb update portfolio/good_stocks.csv
hiquant pepb view portfolio/good_stocks.csv
hiquant pepb view portfolio/good_stocks.csv -sortby=pb_pos -pb_pos=0.0-0.5 -out=portfolio/good_cheap_stocks.csv

cp portfolio/good_cheap_stocks.csv portfolio/my_stocks.csv
```

# 股票池 csv 文件处理
```bash
hiquant symbol create my_stocks.csv 600036 000002 ...
hiquant symbol view my_stocks.csv
hiquant symbol merge my_stocks.csv another.csv -out=outfile.csv
hiquant symbol exclude my_stocks.csv another.csv -out=outfile.csv
hiquant symbol same my_stocks.csv another.csv -out=outfile.csv
```

# 策略
```bash
hiquant strategy create strategy/mystrategy.py
```

# 创建投资组合 以及 模拟回测
```bash
hiquant fund create etc/myfund.conf

... edit my-fund.conf ...

hiquant fund backtrade my-fund.conf 20180101 20210101
```

# 投资组合 实时盯盘 以及 邮件提醒
```bash
hiquant fund run etc/my-fund.conf
```

# 列表显示所有股票 和 指数 的代码 名称
```bash
hiquant stock list
hiquant index list
```

# 显示所有程序目前支持的 技术指标
```bash
hiquant indicator list
```

# 绘制 股票 的技术指标 以及 交易收益率
```bash
hiquant stock 600036
hiquant stock 600036 -ma -macd -kdj
hiquant stock 600036 -all
hiquant stock 600036 -macd -kdj
hiquant stock 600036 -macd -kdj -mix
```

# 绘制 K线 形态（talib）
hiquant pattern list
hiquant pattern 1
hiquant pattern CDL2CROWS

-- 全文完 --
