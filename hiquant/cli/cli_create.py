
import os
import sys
from ..core.data_cache import *

def init_hiquant_conf(config_file):
    hiquant_conf_template = '''
[order_cost]
close_tax = 0.001
open_commission = 0.0003
close_commission = 0.0003
min_commission = 5

[indicator]
# add your own indicators here
# my_abc = indicator/my_abc.py

[strategy]
# add your own strategy here
# 001 = strategy/001_macd.py
'''

    print('  Creating', config_file)
    fp = open(config_file, 'w')
    fp.write(hiquant_conf_template)
    fp.close()
    pass

def cli_create(params, options):
    syntax_tips = '''Syntax:
    __argv0__ create <folder>

Example:
    __argv0__ create myProj
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    if (len(params) == 0) or (params[0] == 'help'):
        print(syntax_tips)
        return

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

    # change to current working folder
    os.chdir(folder)

    # init hiquant config file
    init_hiquant_conf( 'hiquant.conf' )

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
        subfolder = sub
        print('  Creating', subfolder)
        os.mkdir(subfolder)

    # download all stock list and index list
    print('Downloading China A-market stock list and index list ...')
    get_all_stock_list_df()
    get_all_index_list_df()

    print('Done.\n')
