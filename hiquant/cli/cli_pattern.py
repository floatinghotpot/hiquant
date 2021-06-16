# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import talib as tl
from talib import abstract
from tabulate import tabulate

from ..utils import dict_from_df
from ..core import get_all_index_list_df, get_all_stock_list_df
from ..indicator import SIGN

_talib_pattern_length = {
'CDL2CROWS': 3,
'CDL3BLACKCROWS': 3,
'CDL3INSIDE': 3,
'CDL3LINESTRIKE': 4,
'CDL3OUTSIDE': 3,
'CDL3STARSINSOUTH': 3,
'CDL3WHITESOLDIERS': 3,
'CDLABANDONEDBABY': 3,
'CDLADVANCEBLOCK': 3,
'CDLBELTHOLD': 2,
'CDLBREAKAWAY': 5,
'CDLCLOSINGMARUBOZU': 1,
'CDLCONCEALBABYSWALL': 4,
'CDLCOUNTERATTACK': 2,
'CDLDARKCLOUDCOVER': 2,
'CDLDOJI': 1,
'CDLDOJISTAR': 1,
'CDLDRAGONFLYDOJI': 1,
'CDLENGULFING': 2,
'CDLEVENINGDOJISTAR': 3,
'CDLEVENINGSTAR': 3,
'CDLGAPSIDESIDEWHITE': 2,
'CDLGRAVESTONEDOJI': 1,
'CDLHAMMER': 1,
'CDLHANGINGMAN': 1,
'CDLHARAMI': 2,
'CDLHARAMICROSS': 2,
'CDLHIGHWAVE': 3,
'CDLHIKKAKE': 3,
'CDLHIKKAKEMOD': 3,
'CDLHOMINGPIGEON': 2,
'CDLIDENTICAL3CROWS': 3,
'CDLINNECK': 2,
'CDLINVERTEDHAMMER': 1,
'CDLKICKING': 2,
'CDLKICKINGBYLENGTH': 2,
'CDLLADDERBOTTOM': 5,
'CDLLONGLEGGEDDOJI': 1,
'CDLLONGLINE': 1,
'CDLMARUBOZU': 1,
'CDLMATCHINGLOW': 2,
'CDLMATHOLD': 5,
'CDLMORNINGDOJISTAR': 3,
'CDLMORNINGSTAR': 3,
'CDLONNECK': 2,
'CDLPIERCING': 2,
'CDLRICKSHAWMAN': 1,
'CDLRISEFALL3METHODS': 5,
'CDLSEPARATINGLINES': 2,
'CDLSHOOTINGSTAR': 1,
'CDLSHORTLINE': 1,
'CDLSPINNINGTOP': 1,
'CDLSTALLEDPATTERN': 3,
'CDLSTICKSANDWICH': 3,
'CDLTAKURI': 1,
'CDLTASUKIGAP': 3,
'CDLTHRUSTING': 2,
'CDLTRISTAR': 3,
'CDLUNIQUE3RIVER': 3,
'CDLUPSIDEGAP2CROWS': 3,
'CDLXSIDEGAP3METHODS': 5,
}

def list_existing_daily_files():
    file_list = []
    files = os.listdir('cache/market')
    for file in files:
        if file.endswith('_daily.csv'):
            file_list.append('cache/market/'+file)
    return file_list

def cli_pattern_list():
    all_patterns = tl.get_function_groups()['Pattern Recognition']
    table = []
    for pattern in all_patterns:
        info = _talib_pattern_length[ pattern ]
        func = abstract.Function(pattern)
        table.append([pattern, func.info['display_name'], info])
    df = pd.DataFrame(table, columns=['pattern', 'name', 'length'])
    print( tabulate(df, headers='keys', tablefmt='psql') )

def cli_pattern_stat():
    all_patterns = tl.get_function_groups()['Pattern Recognition']

    # init the counters
    pattern_counters = {}
    for pattern in all_patterns:
        pattern_counters[ pattern ] = [0, 0]

    # find all daily files
    files = list_existing_daily_files()
    n = len(files)
    i = 0
    for file in files:
        i += 1
        print('\r ... {}/{} ... searching patterns in {} ...'.format(i, n, file), end= '', flush= True)
        df = pd.read_csv(file, parse_dates=['date']).set_index('date', drop=True)
        df = df.astype(float)

        # prepare for validity exam
        diff = df['close'].diff().shift(-1).fillna(0)

        for pattern in all_patterns:
            # find the pattern signals
            func = abstract.Function(pattern)
            signal = func(df)

            # examine
            verify = SIGN( signal * diff )
            valid_signals = verify[ verify > 0 ].sum()
            invalid_signals = verify[ verify < 0 ].abs().sum()

            pattern_counters[ pattern ][0] += valid_signals
            pattern_counters[ pattern ][1] += invalid_signals
    print('\n')

    # stat result as dataframe
    table = []
    for pattern, counters in pattern_counters.items():
        sum_counter = counters[0] + counters[1]
        valid_rate = ' - ' if (sum_counter == 0) else (str(round(counters[0] / sum_counter * 100.0)).rjust(3) + " %")
        row = [pattern, counters[0], counters[1], valid_rate]
        table.append(row)
    stat_df = pd.DataFrame(table, columns=['pattern', 'valid', 'invalid', 'valid_rate'])

    stat_df.sort_values('valid_rate', ascending=False, inplace=True)

    print( tabulate(stat_df, headers='keys', tablefmt='psql') )

def find_pattern(func):
    files = list_existing_daily_files()
    for file in files:
        df = pd.read_csv(file, parse_dates=['date']).set_index('date', drop=True)
        df = df.astype(float)

        signal = func(df)
        signal = signal[ signal != 0 ]
        if len(signal) > 0:
            symbol = os.path.basename(file).replace('_daily.csv','')
            return symbol, signal, df

    return None, [], None

def get_k_value(price, pattern_date, length):
    '''将开、高、低、收价格数据进行处理，以支持K线图展示
    Args:
        pattern: 形态函数返回的标的与时间元组
        count: 形态数量
    Return:
        返回处理后的价格数据，类型为df
    '''

    start = pattern_date - dt.timedelta(days=20)
    end = pattern_date + dt.timedelta(days=20)
    price = price[start:end]

    dates = price.index.tolist()
    i = dates.index(pattern_date)
    pattern_dates = dates[i+1-length:i+1]

    y_list = {'y1': [], 'y2': [], 'y3': [], 'y4': [], 'c': [], 'al': []}
    
    # 数据处理
    for i in range(price.shape[0]):
        # 计算各bar的透明度
        #print(price.index[i].date(), type(price.index[i].date()))
        if price.index[i] in pattern_dates:
            y_list['al'].append(1)
        else:
            y_list['al'].append(0.3)
        
        # 计算各实体的长度
        if price.open[i] > price.close[i]:
            y_list['y1'].append(price.close[i])
            y_list['y2'].append(price.open[i] - price.close[i])
            y_list['c'].append('g')
        else:
            y_list['y1'].append(price.open[i])
            y_list['y2'].append(price.close[i] - price.open[i])
            y_list['c'].append('r')
        
        # 计算各影线的长度
        if price.high[i] > price.low[i]:
            y_list['y3'].append(price.low[i])
            y_list['y4'].append(price.high[i] - price.low[i])
        else:
            y_list['y3'].append(price.high[i])
            y_list['y4'].append(price.low[i] - price.high[i])
            
    for name, value in y_list.items():
        price.loc[:, name] = value

    return price

def show_bar(data, title='None'):
    '''将价格数据按实体与影线进行组合
    Args:
        data: 处理好的价格数据，df类型
        title: 图片标题，可选
    Return:
        None
    '''

    # 整合 x 轴与 y 轴数据
    x = [str(date.date()) for date in data.index]
    y1 = data['y1']
    y2 = data['y2']

    y3 = data['y3']
    y4 = data['y4']
    
    fig = plt.figure(figsize=(10, 5))

    # 画影线，要求对应不同的颜色与透明度
    for i in range(len(data)):
        plt.bar(x[i], y3[i], align='center', alpha=0)
        plt.bar(x[i], y4[i], align='center', color=data['c'][i], 
                alpha=data['al'][i], bottom=y3[i], width=0.1)

    # 画实体，要求对应不同的颜色与透明度
    for j in range(len(data)):
        plt.bar(x[j], y1[j], align='center', alpha=0)
        plt.bar(x[j], y2[j], align='center', color=data['c'][j], 
                alpha=data['al'][j], bottom=y1[j])
    
    _min = data[['open', 'high', 'low', 'close']].min().min() - 1.0
    _max = data[['open', 'high', 'low', 'close']].max().max() + 1.0

    plt.ylim(_min, _max)
    plt.margins(x=0.0, y=0.05)
    plt.title(title)
    plt.xticks(rotation=45)
    plt.show()

# 检查某标的在某日形成的形态，返回形态描述
def discern_pattern(daily_df, date):
    price = daily_df[ daily_df.index <= date ]
    pattern_function = tl.get_function_groups()['Pattern Recognition']
    for name in pattern_function:
        func = abstract.Function(name)
        signal_series = func(price)
        if signal_series[-1] != 0:
            yield func.info['display_name']

def cli_pattern_demo(pattern):
    all_patterns = tl.get_function_groups()['Pattern Recognition']
    pattern = all_patterns[int(pattern) % len(all_patterns)] if pattern.isdigit() else pattern
    if pattern not in all_patterns:
        print('\nError: pattern "{}" not exists'.format(pattern))
        return

    func = abstract.Function(pattern)
    symbol, signal, df = find_pattern(func)

    if len(signal) > 0:
        # symbol -> name mapping of all stocks and index
        stock_df = get_all_stock_list_df()
        index_df = get_all_index_list_df()
        stock_df = stock_df.append(index_df, ignore_index= True)
        symbol_name = dict_from_df(stock_df, 'symbol', 'name')

        name = symbol_name[symbol] if (symbol in symbol_name) else ''

        # plot the pattern
        length = _talib_pattern_length[pattern]
        k_value = get_k_value(df, signal.index[0], length)
        title = '{} - {} : {}'.format(symbol, name, func.info['display_name'])
        show_bar(k_value, title)

    else:
        print('\nPattern "{}" not found after searching all daily data in cache/market .'.format(pattern))
        print('You can try again after download more daily data.\n')

def cli_pattern(params, options):
    syntax_tips = '''Syntax:
    __argv0__ pattern list
    __argv0__ pattern stat
    __argv0__ pattern demo <pattern>

Actions:
    list ........................... list pattern supported in this tool
    stat ........................... count all the patterns and effectiveness
    demo ........................... plot pattern as demo

Pattern:
    i .............................. index of patterns, range 0 - 60
    name ........................... name of pattern, like CDL2CROWS

Example:
    __argv0__ pattern list
    __argv0__ pattern demo 1
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    if (len(params) == 0) or (params[0] == 'help'):
        print( syntax_tips )
        return

    action = params[0]
    params = params[1:]

    if action == 'list':
        cli_pattern_list()

    elif action == 'stat':
        cli_pattern_stat()

    elif action == 'demo':
        if len(params) > 0:
            cli_pattern_demo(params[0])
        else:
            print('\nError: pattern index or name exptected.')

    else:
        print('\nError: invalid action:', action)
