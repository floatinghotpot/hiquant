# -*- coding: utf-8; py-indent-offset:4 -*-

import pandas as pd
import akshare as ak

_fund_flow_common_column_mapping = {
    '主力净流入-净占比': 'main_pct',
    '超大单净流入-净占比': 'super_pct',
    '大单净流入-净占比': 'large_pct',
    '中单净流入-净占比': 'medium_pct',
    '小单净流入-净占比': 'small_pct',
    '主力净流入-净额': 'main_fund',
    #'超大单净流入-净额': 'super_fund',
    #'大单净流入-净额': 'large_fund',
    #'中单净流入-净额': 'medium_fund',
    #'小单净流入-净额': 'small_fund',
}
_fund_flow_days = {
    '1d': '今日',
    '3d': '3日',
    '5d': '5日',
    '10d': '10日',
}
_fund_flow_sectors = {
    'region': '地域资金流',
    'industry': '行业资金流',
    'concept': '概念资金流',
}

def list_fund_flow_days():
    return _fund_flow_days.keys()

def list_fund_flow_sectors():
    return _fund_flow_sectors.keys()

#
# Data source:
# http://data.eastmoney.com/zjlx/dpzjlx.html
#
def download_cn_market_fund_flow() -> pd.DataFrame:
    df = ak.stock_market_fund_flow()

    cols = {
        '日期': 'date',
        '上证-收盘价': 'sh_close',
        '深证-收盘价': 'sz_close',
        '上证-涨跌幅': 'sh_change_pct',
        '深证-涨跌幅': 'sz_change_pct',
    }
    cols.update(_fund_flow_common_column_mapping)
    df = df.rename(columns= cols)

    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date', drop= True).astype('float64')

    selected_columns = list(cols.values())
    selected_columns.remove('date')
    df = df[ selected_columns ]
    for col in df.columns:
        if '_fund' in col:
            df[col] = df[col] / 100000000.00
    return df

#
# Data source:
# http://data.eastmoney.com/bkzj/hy.html
#
def download_cn_sector_fund_flow_rank(days= '1d', sector= 'industry') -> pd.DataFrame:
    if days not in _fund_flow_days:
        raise ValueError('invalid days: ' + days + ', must be one of: ' + ','.join(_fund_flow_days))
    if sector not in _fund_flow_sectors:
        raise ValueError('invalid sector: ' + sector + ', must be one of: ' + ','.join(_fund_flow_sectors))

    zh_days = _fund_flow_days[ days ]
    zh_sector = _fund_flow_sectors[ sector ]
    df = ak.stock_sector_fund_flow_rank(indicator= zh_days, sector_type= zh_sector)

    df.columns = df.columns.str.replace(zh_days, '')
    cols = {
        #'序号': 'index',
        '名称': 'sector',
        '涨跌幅': 'change_pct',
        '主力净流入最大股': 'top_stock',
    }
    cols.update(_fund_flow_common_column_mapping)
    df = df.rename(columns= cols)

    selected_columns = list(cols.values())
    df = df[ selected_columns ]

    for col in df.columns:
        if '_fund' in col:
            df[col] = df[col] / 100000000.00

    return df

#
# Data source:
# http://data.eastmoney.com/zjlx/detail.html
#
def download_cn_stock_fund_flow_rank(days = '1d') -> pd.DataFrame:
    if days not in _fund_flow_days:
        raise ValueError('invalid days: ' + days + ', must be one of: ' + ','.join(_fund_flow_days))
    zh_days = _fund_flow_days[ days ]

    print('\rfetching fund flow data ...', end = '', flush = True)
    df = ak.stock_individual_fund_flow_rank(indicator= zh_days)
    print('\r', end = '', flush = True)

    cols = {
        #'序号': 'index',
        '代码': 'symbol',
        '名称': 'name',
        '最新价': 'price',
        '涨跌幅': 'change_pct',
    }
    cols.update(_fund_flow_common_column_mapping)
    df.columns = df.columns.str.replace(zh_days, '')
    df = df.rename(columns= cols)

    selected_columns = list(cols.values())
    df = df[ selected_columns ]

    # convert number from str to float
    float_types = {}
    for col in df.columns:
        if col.endswith('price') or col.endswith('_fund') or col.endswith('_pct'):
            float_types[col] = 'float64'
            # some cells are '-', change to '0' to avoid error of type converting
            df[col] = ['0' if ((type(v) == str) and (v == '-')) else v for v in df[col]]
    df = df.astype( float_types )

    # number of is too large, we divide to unit '亿' and easier to read
    for col in df.columns:
        if '_fund' in col:
            df[col] = df[col] / 100000000.00

    return df

#
# Data source:
# http://data.eastmoney.com/zjlx/300750.html
#
def download_cn_stock_fund_flow(symbol) -> pd.DataFrame:
    market = 'sz' if (symbol[0] in ['0','3']) else 'sh'
    df = ak.stock_individual_fund_flow(symbol, market)

    cols = {
        '日期': 'date',
    }
    cols.update(_fund_flow_common_column_mapping)
    df = df.rename(columns= cols)

    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date', drop= True).astype('float64')

    selected_columns = list(cols.values())
    selected_columns.remove('date')
    df = df[ selected_columns ]
    for col in df.columns:
        if '_fund' in col:

            df[col] = df[col] / 100000000.00
    return df

def download_cn_fund_list(param= None, verbose= False):
    df = ak.fund_em_open_fund_daily()
    return df

def download_cn_fund_info(symbol):
    df = ak.fund_em_open_fund_info(symbol, indicator='单位净值走势')
    return df

def download_cn_etf_fund_list(param= None, verbose= False):
    df = ak.fund_em_etf_fund_daily()
    return df

def download_cn_etf_fund_info(symbol):
    df = ak.fund_em_etf_fund_info(symbol)
    return df

def download_cn_fund_manager(param= None, verbose= False):
    df = ak.fund_manager(explode= True)
    return df
