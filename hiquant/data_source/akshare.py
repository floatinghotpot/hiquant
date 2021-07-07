# -*- coding: utf-8; py-indent-offset:4 -*-

import time
import datetime as dt
import pandas as pd
import akshare as ak

from ..utils import earn_to_annual, dict_from_df

def download_cn_stock_list(param= None, verbose= False):
    df = ak.stock_info_a_code_name()
    df.columns = ['symbol', 'name']
    if verbose:
        print(df)
    return df

def download_cn_index_list(param, verbose = False):
    df = ak.stock_zh_index_spot()
    time.sleep(2)
    df.columns = ['symbol', 'name', 'close', 'amount_diff', 'volume_diff', 'last_close', 'open', 'high', 'low', 'volume', 'amount']
    df = df[['symbol', 'name']]
    if verbose:
        print(df)
    return df

def download_hk_stock_list(param= None, verbose= False):
    df = ak.stock_hk_spot()
    time.sleep(2)
    # columns: symbol, name, engname, tradetype, lasttrade, prevclose, open, high, low, volume, amount, ticktime, buy, sell, pricechange, changepercent
    df = df[['symbol', 'name']]
    if verbose:
        print(df)
    return df

# TODO:
def download_hk_index_list(param, verbose = False):
    df = pd.DataFrame([], columns=['symbol','name'])
    # TODO:
    return df

def download_cn_index_daily( symbol ):
    daily_df = ak.stock_zh_index_daily(symbol = symbol)
    time.sleep(2)
    daily_df['date'] = pd.to_datetime(daily_df.index.date)
    daily_df.set_index('date', inplace=True, drop=True)
    return daily_df

def download_cn_stock_daily( symbol, adjust = '' ):
    start = '20000101'
    end = dt.datetime.now().strftime('%Y%m%d')

    print('\rfetching history data {} {} ...'.format(symbol, adjust))
    if len(symbol) == 5:
        df = ak.stock_hk_daily(symbol=symbol, adjust = adjust)
        time.sleep(2)
        df.index = df.index.set_names('date')
    elif len(symbol) == 6:
        if symbol[0] == '6':
            symbol = 'sh' + symbol
        elif symbol[0] in ['0','3']:
            symbol = 'sz' + symbol
        df = ak.stock_zh_a_daily(symbol=symbol, start_date=start, end_date=end, adjust = adjust)
        time.sleep(2)
    else:
        raise ValueError('unknown symbol: ' + symbol)

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace= True, drop= True)
        df = df.astype(float)

    df.sort_index(ascending=True, inplace=True)

    # drop invalid data
    if 'close' in df.columns:
        df = df[df['close'] > 0.01]

    return df

def download_stock_daily_adjust_factor( symbol ):
    df = download_cn_stock_daily( symbol, adjust = 'hfq-factor')
    if len(symbol) == 6:
        df.columns = ['factor']
    elif len(symbol) == 5:
        df.columns = ['factor', 'cash']
    else:
        raise ValueError('unknown symbol: ' + symbol)
    return df

def download_finance_report(symbol, report_type = 'balance'):
    en_zh = {'balance':'资产负债表', 'income':'利润表', 'cashflow':'现金流量表'}
    if report_type in en_zh:
        pass
    else:
        raise ValueError('Unknown finance report type: ' + report_type)

    print('\rfetching ' + report_type + ' report ...')
    df = ak.stock_financial_report_sina(symbol, en_zh[ report_type ])
    time.sleep(1)

    df.rename(columns={'报表日期':'date'}, inplace= True)
    val = df.iloc[0]['date']
    if type(val) == str:
        if '-' in val:
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        else:
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

    return df

def download_finance_balance_report(symbol):
    return download_finance_report(symbol, 'balance')

def download_finance_income_report(symbol):
    return download_finance_report(symbol, 'income')

def download_finance_cashflow_report(symbol):
    return download_finance_report(symbol, 'cashflow')

def extract_data_from_report(report_df, data_mapping):
    df = pd.DataFrame()

    cols = report_df.columns
    for key, fields in data_mapping.items():
        found = False
        for field in fields:
            if field in cols:
                df[key] = report_df[field]
                found = True
        if not found:
            raise ValueError('Column not found in report: ' + key)

    df = df.astype(float)
    df.index = pd.to_datetime( report_df['date'] )

    return df

def extract_abstract_from_report(symbol, balance_df, income_df, cashflow_df):
    df1 = extract_data_from_report(balance_df, {
        'assets': ['资产总计'],
        'debt': ['负债合计'],
        'equity': ['股东权益合计','所有者权益合计','所有者权益(或股东权益)合计'],
        'shares': ['股本','实收资本(或股本)']
    })
    df1 = df1[~df1.index.duplicated(keep='first')]
    df1 = df1[df1['shares'] > 0]

    df2 = extract_data_from_report(income_df, {
        # income sheet
        'revenue': ['一、营业收入', '一、营业总收入'],
        'cost': ['二、营业支出','二、营业总成本'],
        'earning': ['五、净利润'],
    })
    df2 = df2[~df2.index.duplicated(keep='first')]

    df3 = extract_data_from_report(cashflow_df, {
        # cashflow sheet
        'operate': ['经营活动产生的现金流量净额'],
        'invest': ['投资活动产生的现金流量净额'],
        'financing': ['筹资活动产生的现金流量净额'],
        'cash': ['六、期末现金及现金等价物余额']
    })
    df3 = df3[~df3.index.duplicated(keep='first')]

    df = pd.DataFrame()
    x1 = set(df1.index.tolist())
    x2 = set(df2.index.tolist())
    x3 = set(df3.index.tolist())
    if len(x1 ^ x2) > 0 or len(x1 ^ x3) > 0:
        xu = x1.union(x2, x3)
        info = symbol + ': some quarter report missing\n'
        diff = {
            'balance': (xu-x1),
            'income': (xu-x2),
            'cashflow': (xu-x3),
        }
        for k, v in diff.items():
            dates = []
            for date in v:
                dates.append(date.strftime('%Y-%m-%d'))
            dates.sort()
            info = info + '\t' + k + ': ' + ', '.join(dates) + '\n'
        print(info)

    df = pd.concat([df1, df2, df3], axis=1, join='inner')

    df = df.astype({
        'assets':'float',
        'debt':'float',
        'equity':'float',
        'shares':'float',
        'revenue':'float',
        'cost':'float',
        'earning':'float',
        'operate':'float',
        'invest':'float',
        'financing':'float',
        'cash':'float',
    })

    df.sort_index(ascending= True)

    return df

def download_ipo(symbol):
    df = ak.stock_ipo_info(stock= symbol)
    time.sleep(2)
    return df

def download_dividend_history(symbol):
    df = ak.stock_history_dividend_detail(indicator="分红", stock=symbol, date='')
    time.sleep(2)
    df = df[df['进度'] == '实施']
    df.index = pd.to_datetime(df['公告日期'])
    df = df.astype({
        '公告日期':'datetime64',
        #'除权除息日':'datetime64',
        #'股权登记日':'datetime64',
    })
    df.sort_index(ascending= True, inplace= True)
    return df

def download_rightissue_history(symbol):
    df = ak.stock_history_dividend_detail(indicator="配股", stock=symbol, date='')
    time.sleep(2)
    df = df[df['查看详细'] == '查看']
    df.index = pd.to_datetime(df['公告日期'])
    df = df.astype({
        '公告日期':'datetime64',
        #'除权日':'datetime64',
        #'股权登记日':'datetime64',
        #'缴款起始日':'datetime64',
        #'缴款终止日':'datetime64',
        #'配股上市日':'datetime64',
    })
    df.sort_index(ascending= True, inplace= True)
    return df

def get_share_grow(dividend_df, date_from, date_to):
    df = dividend_df.astype({
        '公告日期':'datetime64',
        '送股(股)':'float64',
        '转增(股)':'float64',
        #'派息(税前)(元)':'float64',
    })
    df = df[df['公告日期'] > date_from]
    df = df[df['公告日期'] < date_to]
    x = 1.0
    n = 0
    for i, row in df.iterrows():
        give = row['送股(股)']
        convert = row['转增(股)']
        #bonus = row['派息(税前)(元)']
        # split every 10 shares, we ignore bonus temprarily
        if give>0 or convert>0:
            n = n +1
            x = x * (1 + 0.1 * give) * (1 + 0.1 * convert)
    return x, n

def extract_finance_indicator_data(symbol, abstract_df, ipoinfo_df, dividend_df):
    df = abstract_df

    df = df[df['assets'] > 0]
    df = df[df['equity'] > 0]
    df = df[df['shares'] > 0]

    # debt ratio
    df['debt_ratio'] = round(df['debt'] / df['assets'], 3)
    # leverage
    df['leverage'] = round(df['assets'] / df['equity'], 3)
    # cash ratio
    df['cash_ratio'] = round(df['cash'] / df['assets'], 3)

    # convert earning to earn_ttm according to report month
    df['earn_ttm'] = df['earning'] / df.index.month * 12.0

    # rate of return on owner equity
    df['roe'] = round(df['earn_ttm'] / df['equity'], 3)

    # book value (owner equity) per share
    df['bvps'] = round(df['equity'] / df['shares'], 3)

    # earning per share
    df['eps'] = round(df['earn_ttm'] / df['shares'], 3)

    data = {}
    ipo_dict = dict_from_df(ipoinfo_df, 'item', 'value')
    data['symbol'] = symbol
    data['ipo_date'] = ipo_date = ipo_dict['上市日期']

    if type(ipo_date) == str and ipo_date != '--':
        ipo_date = dt.datetime.strptime(ipo_date, '%Y-%m-%d')
        data['ipo_years'] = round((dt.datetime.now() - ipo_date).days / 365, 2)

        # we only need finance report no early than 3 years before IPO
        ipo_3yr_ago = pd.to_datetime( ipo_date - dt.timedelta(days=365*3) )
        df = df[ df.index >= ipo_3yr_ago ]
    else:
        data['ipo_years'] = 0

    dates = list(df.index)
    min_date = min(dates)
    max_date = max(dates)
    data['last_report'] = max_date.strftime('%Y-%m-%d')

    ago3yr = dt.datetime(max_date.year -4, 12, 31)
    if (not ago3yr in dates) or (ago3yr < min_date):
        ago3yr = min_date
    bvps_grow_3yr = df.loc[max_date]['bvps'] / df.loc[ago3yr]['bvps']
    share_grow_3yr, share_split = get_share_grow(dividend_df, ago3yr, max_date)
    grow3yr = round(bvps_grow_3yr * share_grow_3yr, 3)
    data['3yr_grow_rate'] = round(earn_to_annual(grow3yr-1, (max_date - ago3yr).days), 3) if grow3yr > 1 else 0

    bvps_grow = df.loc[max_date]['bvps'] / df.loc[min_date]['bvps']
    share_grow, share_split = get_share_grow(dividend_df, min_date, max_date)
    grow = round(bvps_grow * share_grow, 3)
    data['grow_rate'] = round(earn_to_annual(grow-1, (max_date - min_date).days), 3) if grow > 1 else 0
    data['grow'] = grow
    data['share_grow'] = round(share_grow, 2)
    #data['split'] = share_split

    data['start_bvps'] = df.iloc[0]['bvps']
    data['now_bvps'] = df.iloc[-1]['bvps']
    data['eps'] = df.iloc[-1]['eps']

    roes = df['roe']
    data['roe'] = round(sum(roes) / len(roes), 3)

    data['debt_ratio'] = df.iloc[-1]['debt_ratio']
    data['cash_ratio'] = df.iloc[-1]['cash_ratio']

    data['earn_ttm'] = round(df.iloc[-1]['earn_ttm'] / 100000000.0, 3)

    data['assets'] = round(df.iloc[-1]['assets'] / 100000000.0, 3)
    data['equity'] = round(df.iloc[-1]['equity'] / 100000000.0, 3)
    data['shares'] = round(df.iloc[-1]['shares'] / 100000000.0, 3)

    return data

def download_stock_pepb_history(symbol):
    print('\tfetching pe/pb data ...', symbol)
    df = ak.stock_a_lg_indicator(symbol)
    time.sleep(2)
    df = df.rename(columns={"trade_date":"date"}).sort_values(by='date')
    return df

def download_macro_bank_interest_rate(country):
    funcs = {
        'china': ak.macro_bank_china_interest_rate,
        'usa': ak.macro_bank_usa_interest_rate,
        'euro': ak.macro_bank_euro_interest_rate,
    }
    if country in funcs:
        func = funcs[ country ]
        data = func()
        time.sleep(2)
        return pd.DataFrame({'date':data.index, 'rate':data.values})
    else:
        raise ValueError('Invalid country, not supported yet: ' + country)
