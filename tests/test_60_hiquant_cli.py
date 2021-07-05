# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant.cli import *

def test_hiquant_cli():
    #cli_create(['./test2'])
    cli_index(['list'], [])
    cli_stock(['list'], [])

    cli_stockpool(['create', 'output/mytest.csv', '600036', '000002'], [])
    cli_stockpool(['merge', 'output/mytest.csv', '600276', '002258'], [])
    cli_stockpool(['exclude', 'output/mytest.csv', '002258'], [])
    cli_stockpool(['same', 'output/mytest.csv', 'stockpool/mystocks.csv'], [])

    cli_finance(['view', '600036'], [])
    cli_finance(['view', 'all'], ['-roe=0.20-', '-sortby=roe', '-desc'])

    cli_pepb(['view', '600036', '000002'], [])
    cli_pepb(['view', 'output/mytest.csv'], ['-pb_pos=50-'])

    cli_stock(['600036'], ['-ma', '-macd', '-kdj', '-out=output/test_cli_stock.png'])
    cli_index(['sh000300'], ['-ma', '-macd', '-kdj', '-out=output/test_cli_index.png'])

    cli_indicator(['list'], [])

    cli_main_params_options(['help'], [])
    cli_main_params_options(['list', 'index'], [])
    cli_main_params_options(['list', 'stock'], [])

    cli_pattern(['list'], [])
    cli_pattern(['demo', '0'], ['-out=output/pattern0.png'])
    cli_pattern(['demo', 'CDL3BLACKCROWS'], ['-out=output/pattern1.png'])

    cli_strategy(['help'], [])

    cli_fund(['backtrade', 'etc/myfund.conf'], ['-q', '-out=output/test_cli_fund.png'])

if __name__ == "__main__":
    test_hiquant_cli()
