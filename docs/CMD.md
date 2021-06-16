
### show help
```bash
hiquant
hiquant help
hiquant help <cmd>
hiquant -v --version
```

### create folder and initilize data
```bash
hiquant create <folder>
cd <folder>
```

### financial analysis on stock pool
```bash
hiquant finance update all

hiquant finance view all
hiquant finance show all -ipo_years=1- -earn_ttm=1.0- -roe=0.15- -3yr_grow_rate=0.15- -sortby=roe -out=good_stock.csv
```

### PE/PB analysis on stock pool
```bash
hiquant pepb update portfolio/good_stocks.csv
hiquant pepb view portfolio/good_stocks.csv
hiquant pepb view portfolio/good_stocks.csv -sortby=pb_pos -pb_pos=0.0-0.5 -out=portfolio/good_cheap_stocks.csv

cp portfolio/good_cheap_stocks.csv portfolio/my_stocks.csv
```

### Create and edit stock pool CSV file
```bash
hiquant symbol create my_stocks.csv 600036 000002 ...
hiquant symbol view my_stocks.csv
hiquant symbol merge my_stocks.csv another.csv -out=outfile.csv
hiquant symbol exclude my_stocks.csv another.csv -out=outfile.csv
hiquant symbol same my_stocks.csv another.csv -out=outfile.csv
```

### Strategy, created from template
```bash
hiquant strategy create strategy/mystrategy.py
```

### Create fund configuration from template, and backtrading
```bash
hiquant fund create etc/myfund.conf

... edit my-fund.conf ...

hiquant fund backtrade my-fund.conf 20180101 20210101
```

### Realtime simulation and email reminder
```bash
hiquant fund run etc/my-fund.conf
```

### List all stocks and indice
```bash
hiquant stock list
hiquant index list
```

### List all technical indicators in this softeware
```bash
hiquant indicator list
```

### Plot stock with indicators and yeild curve
```bash
hiquant stock 600036
hiquant stock 600036 -ma -macd -kdj
hiquant stock 600036 -all
hiquant stock 600036 -macd -kdj
hiquant stock 600036 -macd -kdj -mix
```

### Plot candle patterns (supported with TALib）
hiquant pattern list
hiquant pattern 1
hiquant pattern CDL2CROWS
