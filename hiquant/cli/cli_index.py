# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
import pandas as pd
import tabulate as tb
import matplotlib.pyplot as plt

from ..utils import symbol_normalize, date_range_from_options, range_from_options, dict_from_df, csv_xlsx_from_options, sort_with_options, filter_with_options
from ..data_source import download_cn_index_stocks_list
from ..core import symbol_to_name
from ..core import get_order_cost
from ..core import list_signal_indicators
from ..core import get_cn_index_list_df, get_hk_index_list_df, get_us_index_list_df, get_world_index_list_df, get_index_daily, get_all_index_list_df
from ..core import Stock

def cli_index_help():
    syntax_tips = '''Syntax:
    __argv0__ index list <region>
    __argv0__ index plot <symbol> [<from_date>] [<to_date>] [<options>]
    __argv0__ index stocks <symbol> [-out=<out.csv>]

<action>
    list ....................... list index, following param: world, cn, us, hk, etc.
    plot ....................... plot the index
    stocks ..................... list stocks of this index

<symbol> ....................... stock symbol, like 600036
<from_date> .................... default from 3 year ago
<to_date> ...................... default to yesterday

<options> ...................... options to plot the stock
    -ma, -macd, -kdj, etc. ..... add some indicators
    -all ....................... add all indicators
    -mix ....................... show trade result if mix trade signal of the indicators
    -top5 ...................... show only top 5 indicators according to result

Example:
    __argv0__ index list world
    __argv0__ index list cn
    __argv0__ index list us

    __argv0__ index plot sh000300 -ma
    __argv0__ index plot sh000300 20180101 -ma -macd -kdj
    __argv0__ index plot sh000300 20180101 20210101 -ma -macd -kdj

    __argv0__ index stocks sh000300 -out=stockpool/sh000300_stocks.csv

'''.replace('__argv0__',os.path.basename(sys.argv[0]))
    print(syntax_tips)

def cli_index_list(params, options):
    list_funcs = {
        'world': get_world_index_list_df,
        'cn': get_cn_index_list_df,
        'us': get_us_index_list_df,
        'hk': get_hk_index_list_df,
    }
    if (len(params) == 0) or (not (params[0] in list_funcs)):
        print('Error: index list expected param:', ', '.join(list(list_funcs.keys())))
        cli_index_help()
        return
    func = list_funcs[ params[0] ]
    df = func()
    print( tb.tabulate(df, headers='keys', showindex=True, tablefmt='psql') )
    print( 'Totally', df.shape[0], 'records.\n')

def cmp_index_earn(params, options):
    date_from, date_to = date_range_from_options(options)
    range_from, range_to = range_from_options(options)
    limit = range_to - range_from

    df_stocks = None
    i = 0
    for symbol in params:
        try:
            df = get_index_daily(symbol)
        except (KeyError, ValueError) as e:
            continue

        df = df[ df.index >= date_from ]
        df = df[ df.index < date_to ]

        df['pct_change'] = df['close'].pct_change(1) * 100.0
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

    df_stock_list = get_all_index_list_df()
    stock_symbol_names = dict_from_df(df_stock_list, 'symbol', 'name')
    df_cmp.insert(1, 'name', [stock_symbol_names[symbol] if (symbol in stock_symbol_names) else '' for symbol in symbols])

    return df_stocks, df_cmp

def cli_index_cmp(params, options):
    if params[0].endswith('.csv'):
        df = pd.read_csv(params[0], dtype=str)
        params = df['symbol'].tolist()
    elif ',' in params[0]:
        params = params[0].split(',')

    df_stocks, df = cmp_index_earn(params, options)

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

def cli_index_plot_one(params, options):
    symbol = params[0]
    symbol_name = dict_from_df(get_all_index_list_df(), 'symbol', 'name')
    name = (symbol_name[symbol] if (symbol in symbol_name) else '')

    date_from, date_to = date_range_from_options(options)
    df = get_index_daily(symbol)
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

def cli_index_plot_multi(params, options):
    df_stocks, df_cmp = cmp_index_earn(params, options)

    print(df_cmp)
    df_stocks = df_stocks[ df_cmp['symbol'].tolist() ]

    symbol_names = dict_from_df(df_cmp, 'symbol', 'name')
    df_stocks.columns = [(symbol + ' - ' + symbol_names[symbol]) for symbol in df_stocks.columns]

    if '-mix' in options:
        df_stocks = df_stocks.mean(axis=1).to_frame()
        df_stocks.columns = ['平均收益']
    else:
        pass

    df_stocks.index = df_stocks.index.strftime('%Y-%m-%d')
    title = '持仓收益 (' + df_stocks.index[0] + ' ~ ' + df_stocks.index[-1] + ')'
    df_stocks.plot(kind='line', ylabel='return (%)', figsize=(10,6), title= title)
    plt.xticks(rotation=15)
    plt.show()

def cli_index_plot(params, options):
    if len(params) == 0:
        cli_index_help()
        return

    if params[0].endswith('.csv'):
        df = pd.read_csv(params[0], dtype=str)
        params = df['symbol'].tolist()
    elif ',' in params[0]:
        params = params[0].split(',')

    if len(params) == 1:
        cli_index_plot_one(params[0], options)
    else:
        cli_index_plot_multi(params, options)

def cli_index_stocks(params, options):
    if len(params) > 0:
        symbol = params[0]
        if symbol.startswith('sh') or symbol.startswith('sz'):
            df = download_cn_index_stocks_list(symbol)
            print( tb.tabulate(df, headers='keys', showindex=True, tablefmt='psql') )
            print( 'Totally', df.shape[0], 'records.\n')

            for option in options:
                if ('-out=' in option) and option.endswith('.csv'):
                    out_csv_file = option.replace('-out=','')
                    df.to_csv(out_csv_file, index=False)
                    print('Saved to:', os.path.abspath(out_csv_file))
                    return
            return

    print('Expect param: China index symbol, with prefix sh or sz, like sh000300, sz399991, etc.\n')

def cli_index(params, options):

    if (len(params) == 0) or (params[0] == 'help'):
        cli_index_help()
        return

    action = params[0]
    params = params[1:]

    if action == 'list':
        cli_index_list(params, options)

    elif action in ['plot', 'view', 'show']:
        cli_index_plot(params, options)

    elif action == 'stocks':
        cli_index_stocks(params, options)

    else:
        print('invalid action:', action)
        cli_index_help()
