# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys

from ..core import init_hiquant_conf

def cli_create_help():
    syntax_tips = '''Syntax:
    __argv0__ create <folder>

Example:
    __argv0__ create myProj
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    print(syntax_tips)

def cli_create_folder(params, options):
    folder = params[0]
    if os.path.exists(folder):
        print('Folder', folder, 'already exists.\n')
        return

    # create following folder structure
    '''
hiquant.conf
cache/
cache/finance/
cache/market/
cache/pepb/
cache/bank/
cache/A_index_all.csv
cache/A_stock_all.csv
etc/
stockpool/
strategy/
data/
output/
log/
'''

    # create working folder first
    print('Initializing hiquant project folder ...')
    print('  Creating', folder)
    os.mkdir(folder)

    # create sub folders
    for sub in [
        'cache',
        'cache/finance',
        'cache/market',
        'cache/pepb',
        'cache/bank',
        'etc',
        'stockpool',
        'strategy',
        'data',
        'output',
        'log',
        ]:
        subfolder = folder + '/' + sub
        print('  Creating', subfolder)
        os.mkdir(subfolder)

    # init hiquant config file
    conf_file = folder + '/hiquant.conf'
    print('  Creating', conf_file)
    init_hiquant_conf(conf_file)

    print('Done.\n')

def cli_create(params, options):

    if (len(params) == 0) or (params[0] == 'help'):
        cli_create_help()
        return

    cli_create_folder(params, options)
