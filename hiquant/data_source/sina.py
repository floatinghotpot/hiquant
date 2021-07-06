
import requests
import pandas as pd

def download_cn_stock_spot( symbols, verbose= False ):
    if len(symbols) > 100:
        df = pd.DataFrame()
        for i in range(0, len(symbols), 100):
            page = symbols[i:i+100]
            page_df = download_cn_stock_spot(page)
            df = df.append(page_df, ignore_index=True)
        return df
    else:
        sina_symbols = []
        for symbol in symbols:
            if symbol.startswith('6'):
                sina_symbols.append( 'sh' + symbol )
            elif symbol.startswith('0') or symbol.startswith('3'):
                sina_symbols.append( 'sz' + symbol )
            elif symbol.startswith('hk') or symbol.startswith('HK'):
                sina_symbols.append( 'hk0' + symbol[-4:] )

        print('\rfetching sina data ...', end = '', flush = True)
        url = 'http://hq.sinajs.cn/list={0}'.format(','.join(sina_symbols))
        r = requests.get(url)
        print('\r', end = '', flush = True)

        table = []
        if(r.status_code == 200):
            lines = r.text.split('\n')
            for line in lines:
                strs = line.split('=')
                if(len(strs) <2):
                    break
                row = []
                str0 = strs[0].replace('var hq_str_','')
                str1 = strs[1].replace('\"','').replace(';','')
                v = str1.split(',')
                if str0.startswith('sh') or str0.startswith('sz'):
                    # return data format:
                    # symbol = name, open, prevclose, lasttrade, high, low, buy, sell, volume, amount
                    # buy1-count, buy1-price, ...
                    # sell1-count, sell1-price, ...
                    # date, time
                    str0 = str0[-6:]
                    # symbol, name, open, prevclose, lasttrade, high, low, volume, amount, date, time
                    row = [str0, v[0], v[1], v[2], v[3], v[4], v[5], v[8], v[9], v[30], v[31]]
                elif str0.startswith('hk'):
                    # return data format:
                    # symbol = en_name, zh_name, open, prevclose, high, low, lasttrade,
                    # pricechange, changepercent, buy1-price, sell1-price, amount, volume, 0, 0, ?, ?,
                    # date, time
                    str0 = 'hk' + str0[-4:]
                    # symbol, name, open, prevclose, lasttrade, high, low, volume, amount, date, time
                    row = [str0, v[1], v[2], v[3], v[4], v[4], v[6], v[12], v[11], v[17], v[18]]
                table.append(row)
                #print(row)
        df = pd.DataFrame(table)
        df.columns = [
            'symbol',
            'name',
            'open',
            'prevclose',
            'close',
            'high',
            'low',
            'volume',
            'amount',
            'date',
            'time'
        ]
        df = df.astype({
            'open':'float64',
            'prevclose':'float64',
            'close':'float64',
            'high':'float64',
            'low':'float64',
            'volume':'int64',
            'date':'datetime64'
        })
        #print(df)
        return df[ [
            'symbol', 'name',
            'open', 'prevclose',
            'close', 'high', 'low',
            'volume', 
            'date',
        ] ]
