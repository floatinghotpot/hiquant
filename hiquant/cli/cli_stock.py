# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
import pandas as pd
import tabulate as tb
import matplotlib.pyplot as plt

from ..utils import symbol_normalize, date_range_from_options, range_from_options, dict_from_df, csv_xlsx_from_options, sort_with_options, filter_with_options
from ..core import symbol_to_name, get_cn_stock_list_df, get_hk_stock_list_df, get_us_stock_list_df, get_all_stock_list_df, get_all_index_list_df
from ..core import get_index_daily, get_daily
from ..core import list_signal_indicators, get_order_cost
from ..core import Stock

def cli_stock_help():
    syntax_tips = '''Syntax:
    __argv0__ stock list <market>
    __argv0__ stock plot <symbol> [<from_date>] [<to_date>] [<options>]

<market>
    cn ......................... China market
    hk ......................... Hong Kong market
    us ......................... USA market

<symbol> ....................... stock symbol, like 600036
<from_date> .................... default from 3 year ago
<to_date> ...................... default to yesterday

<options> ...................... options to plot the stock
    -ma, -macd, -kdj, etc. ..... add some indicators
    -all ....................... add all indicators
    -mix ....................... show trade result if mix trade signal of the indicators
    -top5 ...................... show only top 5 indicators according to result

Example:
    __argv0__ stock list cn
    __argv0__ stock cmp 601012,300347
    __argv0__ stock cmp stockpool/stocks.csv -days=3650 -sortby=earn -desc -out=output/output.csv
    __argv0__ stock plot 600036 -ma
    __argv0__ stock plot 600036 -days=365 -ma -macd -kdj
    __argv0__ stock plot 600036 -date=20200101-20210831 -ma -macd -kdj
    __argv0__ stock plot 600036 -ma -macd -mix
    __argv0__ stock plot 601012,300347 -days=365
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    print( syntax_tips )

def cli_stock_list(params, options):
    list_funcs = {
        'cn': get_cn_stock_list_df,
        'us': get_us_stock_list_df,
        'hk': get_hk_stock_list_df,
    }
    if (len(params) == 0) or (not (params[0] in list_funcs)):
        print('Error: stock list expected param:', ', '.join(list(list_funcs.keys())))
        cli_stock_help()
        return
    func = list_funcs[ params[0] ]
    df = func()
    df['name'] = df['name'].str.slice(stop=60)
    print( tb.tabulate(df, headers='keys', showindex=False, tablefmt='psql') )
    print( 'Totally', df.shape[0], 'rows.\n')

def cmp_stock_earn(params, options):
    date_from, date_to = date_range_from_options(options)
    range_from, range_to = range_from_options(options)
    limit = range_to - range_from

    df_stocks = None
    i = 0
    for symbol in params:
        try:
            df = get_daily(symbol)
        except (KeyError, ValueError) as e:
            continue

        df = df[ df.index >= date_from ]
        df = df[ df.index < date_to ]

        df['pct_change'] = df['adj_close'].pct_change(1) * 100.0
        df['pct_cum'] = round(((df['pct_change'] * 0.01 +1).cumprod() - 1.0) * 100.0, 1)
        if df_stocks is None:
            df_stocks = df[['pct_cum']]
            df_stocks.columns = [ symbol ]
        else:
            df_stocks[ symbol ] = df['pct_cum']
        #print(df)

    #pd.options.display.float_format = '{:.0f} %'.format
    col = df_stocks.iloc[-1].copy()
    col.name = 'earn'
    df_cmp = col.to_frame()
    df_cmp.insert(0, 'symbol', df_cmp.index)
    df_cmp = df_cmp.sort_values(by='earn', ascending= False)
    df_cmp.reset_index(drop= True, inplace= True)

    if limit > 0:
        df_cmp = df_cmp.head(limit)
        symbols = df_cmp['symbol'].tolist()
        df_stocks = df_stocks[ symbols ]
    else:
        symbols = df_cmp['symbol'].tolist()

    df_stock_list = get_all_stock_list_df()
    stock_symbol_names = dict_from_df(df_stock_list, 'symbol', 'name')
    df_cmp.insert(1, 'name', [stock_symbol_names[symbol] if (symbol in stock_symbol_names) else '' for symbol in symbols])

    return df_stocks, df_cmp

def cli_stock_cmp(params, options):
    if params[0].endswith('.csv'):
        df = pd.read_csv(params[0], dtype=str)
        params = df['symbol'].tolist()
    elif ',' in params[0]:
        params = params[0].split(',')

    df_stocks, df = cmp_stock_earn(params, options)

    date_from, date_to = date_range_from_options(options)
    range_from, range_to = range_from_options(options)
    limit = range_to - range_from
    if limit > 0:
        df = df.head(limit)
        df_stocks = df_stocks[ df['stock'].tolist() ]

    df = filter_with_options(df, options)
    df = sort_with_options(df, options, by_default='earn')

    print( tb.tabulate(df, headers='keys') )

    out_csv_file, out_xls_file = csv_xlsx_from_options(options)

    if out_csv_file:
        df = df[['symbol', 'name']]
        df.to_csv(out_csv_file, index= False)
        print('Exported to:', out_csv_file)
        print(df)

    pass

def cli_stock_plot_one(symbol, options):
    date_from, date_to = date_range_from_options(options)

    symbol = symbol_normalize(symbol)
    name = symbol_to_name(symbol)

    try:
        df = get_daily(symbol)
    except (KeyError, ValueError) as e:
        pass

    df = df[ df.index >= date_from ]
    df = df[ df.index < date_to ]

    stock = Stock(symbol, name, df)

    all_indicators = list_signal_indicators()

    indicators = []
    topN = 5
    inplace = True
    out_file = None
    for option in options:
        if option.startswith('-top'):
            topN = int(option.replace('-top',''))
        elif option.startswith('-out=') and (option.endswith('.png') or option.endswith('.jpg')):
            out_file = option.replace('-out=', '')
        else:
            k = option.replace('-','')
            if (k in all_indicators) and (not k in indicators):
                indicators.append(k)
    if '-all' in options:
        indicators = all_indicators
        inplace = False

    mix = '-mix' in options

    # add indicators and calculate performance
    stock.add_indicator(indicators, mix=mix, inplace= inplace, order_cost = get_order_cost())

    rank_df = stock.rank_indicator(by = 'final')
    if rank_df.shape[0] > 0:
        print(rank_df)

    # find top indicators
    ranked_indicators = rank_df['indicator'].tolist()
    other_indicators = ranked_indicators[topN:]
    df.drop(columns = other_indicators, inplace=True)

    stock.plot(out_file= out_file)

def cli_stock_plot_multi(params, options):
    df_stocks, df_cmp = cmp_stock_earn(params, options)

    print(df_cmp)
    df_stocks = df_stocks[ df_cmp['symbol'].tolist() ]
    symbol_names = dict_from_df(df_cmp, 'symbol', 'name')
    df_stocks.columns = [(symbol + ' - ' + symbol_names[symbol]) for symbol in df_stocks.columns]

    if '-mix' in options:
        df_stocks = df_stocks.mean(axis=1).to_frame()
        df_stocks.columns = ['平均收益']
    else:
        pass

    base = 'sh000300'
    for k in options:
        if k.startswith('-base='):
            base = k.replace('-base=', '')
    df_base = get_index_daily( base )

    date_from, date_to = date_range_from_options(options)
    df_base = df_base[ df_base.index >= date_from ]
    df_base = df_base[ df_base.index < date_to ]
    df_base['pct_cum'] = (df_base['close'] / df_base['close'].iloc[0] - 1.0) * 100.0

    index_symbol_names = dict_from_df( get_all_index_list_df() )
    base_name = index_symbol_names[ base ] if base in index_symbol_names else base
    df_stocks[ base_name ] = df_base['pct_cum']

    df_stocks.index = df_stocks.index.strftime('%Y-%m-%d')
    title = '持仓收益 (' + df_stocks.index[0] + ' ~ ' + df_stocks.index[-1] + ')'
    df_stocks.plot(kind='line', ylabel='return (%)', figsize=(10,6), title= title)
    plt.xticks(rotation=15)
    plt.show()

def cli_stock_plot(params, options):
    if len(params) == 0:
        cli_stock_help()
        return

    if params[0].endswith('.csv'):
        df = pd.read_csv(params[0], dtype=str)
        params = df['symbol'].tolist()
    elif ',' in params[0]:
        params = params[0].split(',')

    if len(params) == 1:
        cli_stock_plot_one(params[0], options)
    else:
        cli_stock_plot_multi(params, options)

def cli_stock(params, options):
    if (len(params) == 0) or (params[0] == 'help'):
        cli_stock_help()
        return

    action = params[0]
    params = params[1:]

    if action == 'list':
        cli_stock_list(params, options)

    elif action in ['cmp']:
        cli_stock_cmp(params, options)

    elif action in ['plot', 'show']:
        cli_stock_plot(params, options)

    else:
        print('invalid action:', action)
        cli_stock_help()
