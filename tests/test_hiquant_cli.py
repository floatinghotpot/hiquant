# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant.cli.cli_main import cli_main_params_options
import os
from hiquant.cli import *

def test_hiquant_cli():
    #cli_create(['./test2'])
    cli_index(['list'], [])
    cli_stock(['list'], [])

    cli_finance(['view', '600036'], [])
    cli_finance(['view', 'all'], ['-roe=0.20-', '-sortby=roe', '-desc'])

    cli_fund(['backtrade', 'etc/myfund.comf'], ['-q'])

    cli_index(['600036'], ['-ma'])

    cli_indicator(['list'], [])

    cli_main_params_options(['help'], [])
    cli_main_params_options(['list', 'index'], [])
    cli_main_params_options(['list', 'stock'], [])

    cli_pattern(['list'], [])
    cli_pattern(['pattern', '1'], ['-to_file=output/pattern.png'])
    cli_pattern(['pattern', 'CDL3BLACKCROWS'], ['-to_file=output/pattern2.png'])

    cli_pepb(['view', '600036', '000002'], [])
    cli_pepb(['view', 'stockpool/mystocks.csv'], ['-pb_pos=50-'])

    cli_stockpool(['create', 'stockpool/mytest.csv', '600036', '000002'], [])
    cli_stockpool(['merge', 'stockpool/mytest.csv', '600276', '002258'], [])
    cli_stockpool(['exclude', 'stockpool/mytest.csv', '002258'], [])
    cli_stockpool(['same', 'stockpool/mytest.csv', 'stockpool/mystocks.csv'], [])

    cli_strategy(['help'], [])
