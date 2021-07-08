# -*- coding: utf-8; py-indent-offset:4 -*-

import matplotlib.pyplot as plt

from hiquant import download_cn_market_fund_flow, ABS

def normalize_columns(df):
    df = df.copy()
    for col in df.columns:
        max_value = max( ABS(df[col]) )
        df[col] /= max_value
    return df

def plot_market_fund_flow():
    df = download_cn_market_fund_flow()

    df['price_change'] = (df['sh_change_pct'] + df['sz_change_pct']) * 0.5
    df = df[['price_change', 'main_pct']]
    df = normalize_columns(df)
    print(df)
    df['zero'] = 0.0

    plot_args = dict(
        kind= 'line',
        figsize= (10,5),
        title= 'Main fund flow vs. Market price'
    )
    df.plot( **plot_args )
    plt.show()

def plot_stock_fund_flow(symbol):
    pass

if __name__ == "__main__":
    plot_market_fund_flow()
    # jQuery112308950330806450804_1625742696588
    # jQuery1123015144527131069818_1625743152820
    #plot_market_fund_flow('600036')
    pass
