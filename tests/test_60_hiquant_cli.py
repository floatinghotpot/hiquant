# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant.cli import *

def test_hiquant_cli():
    #cli_create(['./test2'])
    cli_main_params_options(['help'], [])

    cli_stockpool(['create', 'output/mytest.csv', '600036', '000002'], [])
    cli_stockpool(['merge', 'output/mytest.csv', '600276', '002258'], [])
    cli_stockpool(['exclude', 'output/mytest.csv', '002258'], [])
    cli_stockpool(['same', 'output/mytest.csv', 'stockpool/mystocks.csv'], [])

    cli_stock(['eval', '600036'], [])
    cli_stock(['eval', 'all'], ['-roe=0.20-', '-sortby=roe', '-desc'])

    cli_stock(['pepb', '600036', '000002'], [])
    cli_stock(['pepb', 'output/mytest.csv'], ['-pb_pos=50-'])

    cli_stock(['list', 'cn'], [])
    cli_stock(['plot', '600036'], ['-ma', '-macd', '-kdj', '-out=output/test_cli_stock.png'])

    cli_index(['list', 'cn'], [])
    cli_index(['plot', 'sh000300'], ['-ma', '-macd', '-kdj', '-out=output/test_cli_index.png'])

    cli_indicator(['list'], [])

    cli_strategy(['help'], [])

    cli_trade(['backtrade', 'etc/myfund.conf'], ['-q', '-out=output/test_cli_fund.png'])

if __name__ == "__main__":
    test_hiquant_cli()
