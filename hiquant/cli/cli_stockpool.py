# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
import pandas as pd
from tabulate import tabulate

from ..core import get_stockpool_df

def cli_stockpool(params, options):
    syntax_tips = '''Syntax:
    __argv0__ stockpool <action> <file.csv> [<symbols> | <another.csv>] [-out=<out.csv>]

Action:
    create .................... create a new stock pool csv file
    view ...................... show the content of the stock pool
    merge ..................... merge the stock pool with other symbols or another stock pool csv
    exclude ................... exclude symbols or another csv from this stock pool csv
    same ...................... find the same symbols existing in both csv file

Symbols:
    symbols ................... a list of stock symbols, like 600036 000002 300033
    file.csv .................. a csv file with stock symbol and names

Export:
    -out=<out.csv> ............ save result into a new csv file

Example:
    __argv0__ stockpool create mystocks.csv 600036 000002 300033
    __argv0__ stockpool view mystocks.csv
    __argv0__ stockpool exclude mystocks.csv 000651 600276 -out=mystocks.csv
    __argv0__ stockpool merge mystocks.csv file2.csv -out=mystocks.csv
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    if (len(params) == 0) or (params[0] == 'help'):
        print(syntax_tips)
        return

    action = params[0]
    params = params[1:]

    if (len(params) == 0) or ('.csv' not in params[0]):
        print('\nError: A filename with .csv is expected.\n')
        return

    csv_file = params[0]
    params = params[1:]

    # create csvfile with symbols
    if action == 'create':
        if len(params) > 0:
            df = get_stockpool_df(params)
            df.to_csv(csv_file, index=False)
            print('Stockpool file created:', os.path.abspath(csv_file))
            print( tabulate(df, headers='keys', tablefmt='psql') )
            print('')
            return
        else:
            print('\nError: Symbol list is expected.\n')
            print( syntax_tips )
            return

    # load the csv file
    df1 = pd.read_csv(csv_file, dtype=str)
    if action in ['view', 'show']:
        print( tabulate(df1, headers='keys', tablefmt='psql') )
        return

    if (len(params) == 0):
        print('\nError: Symbols or another csv file is expected.\n')
        print( syntax_tips )
        return

    # load or create the second csv file
    if '.csv' in params[0]:
        csv_file2 = params[0]
        df2 = pd.read_csv(csv_file2, dtype=str)
    else:
        df2 = get_stockpool_df( params )

    # now, merge, exclude, or find same
    if action == 'merge':
        df3 = pd.merge(df1, df2, on=['symbol','name'], how='outer').reset_index(drop=True)
    elif action == 'exclude':
        df3 = pd.concat([df1, df2, df2]).drop_duplicates(keep=False).reset_index(drop=True)
    elif action == 'same':
        df3 = pd.merge(df1, df2, on=['symbol','name'], how='inner').reset_index(drop=True)
    else:
        print('\nError: Unkown action:', action, '\n')
        print( syntax_tips )
        return

    print( tabulate(df3, headers='keys', tablefmt='psql') )

    for option in options:
        if ('-out=' in option) and option.endswith('.csv'):
            out_csv_file = option.replace('-out=','')
            df3.to_csv(out_csv_file, index=False)
            print('Saved to:', os.path.abspath(out_csv_file))

    print('')