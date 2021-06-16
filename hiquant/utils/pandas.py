# -*- coding: utf-8; py-indent-offset:4 -*-

# { df[key]: df[value] }
def dict_from_df(df, key_col = 'symbol', value_col = 'name'):
    mapping = {}
    for i, row in df.iterrows():
        mapping[ row[key_col] ] = row[value_col]
    return mapping

# -sortby=<col> -desc
def sort_with_options(df, options, by_default=''):
    sortby = by_default
    for k in options:
        if k.startswith('-'):
            k = k[1:]
            if k in df.columns:
                sortby = k
                break
    asc = '-desc' not in options
    return df.sort_values(by= sortby, ascending= asc).reset_index(drop= True) if sortby else df

# -<col>=<from>-<to>
def filter_with_options(df, options):
    for k in options:
        if k.startswith('-') and ('=' in k):
            k = k[1:]
            items = k.split('=')
            key = items[0]
            if (key in df.columns) and ('-' in items[1]):
                values = items[1].split('-')
                if values[0]:
                    df = df[ df[key] > float(values[0]) ]
                if values[1]:
                    df = df[ df[key] < float(values[1]) ]
    return df
