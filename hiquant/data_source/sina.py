
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
            if (len(symbol) == 6) and symbol[0].isdigit():
                if symbol[0] == '6':
                    sina_symbols.append( 'sh' + symbol )
                elif symbol[0] in ['0','3']:
                    sina_symbols.append( 'sz' + symbol )
            elif (len(symbol) == 5) and symbol[0].isdigit():
                sina_symbols.append( 'hk' + symbol )
            elif symbol[:2].capitalize() == 'HK':
                sina_symbols.append( 'hk0' + symbol[-4:] )
            else:
                sina_symbols.append( symbol )
        print('\rfetching quote data ...', end = '', flush = True)
        url = 'http://hq.sinajs.cn/list={0}'.format(','.join(sina_symbols))
        r = requests.get(url)
        print('')

        table = []
        if(r.status_code == 200):
            lines = r.text.replace('var hq_str_','').replace('="',',').replace('";','').split('\n')
            for line in lines:
                v = line.split(',')
                symbol = v[0]
                symbol_prefix = symbol[:2]
                if symbol_prefix in ['sh', 'sz']:
                    # return data format:
                    # symbol = name, open, prevclose, lasttrade, high, low, buy, sell, volume, amount
                    # buy1-count, buy1-price, ...
                    # sell1-count, sell1-price, ...
                    # date, time
                    symbol = symbol[-6:]
                    # symbol, name, open, prevclose, lasttrade, high, low, volume, date
                    row = [symbol, v[1], v[2], v[3], v[4], v[5], v[6], v[9], v[31]]
                    table.append(row)
                elif symbol_prefix == 'hk':
                    # return data format:
                    # symbol = en_name, zh_name, open, prevclose, high, low, lasttrade,
                    # pricechange, changepercent, buy1-price, sell1-price, amount, volume, 0, 0, ?, ?,
                    # date, time
                    symbol = 'hk' + symbol[-4:]
                    # symbol, name, open, prevclose, lasttrade, high, low, volume, date
                    row = [symbol, v[2], v[3], v[4], v[5], v[6], v[7], v[13], v[18]]
                    table.append(row)
        df = pd.DataFrame(table, columns = ['symbol','name','open','prevclose','close','high','low','volume','date'])
        df = df.astype({
            'open':'float64',
            'prevclose':'float64',
            'close':'float64',
            'high':'float64',
            'low':'float64',
            'volume':'int64',
            'date':'datetime64'
        })
        return df
