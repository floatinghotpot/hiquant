# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import configparser

_hiquant_conf = {
}

def load_hiquant_conf():
    hiquant_conf_file = 'hiquant.conf'
    if os.path.isfile(hiquant_conf_file):
        config = configparser.ConfigParser()
        config.read(hiquant_conf_file, encoding='utf-8')
        _hiquant_conf['config'] = config
    else:
        print('file not found:', hiquant_conf_file)

def get_hiquant_conf():
    if 'config' not in _hiquant_conf:
        load_hiquant_conf()
    return _hiquant_conf['config']

def init_hiquant_conf(config_file):
    hiquant_conf_template = '''
[main]
lang = en
market = cn, hk, us

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
    fp = open(config_file, 'w')
    fp.write(hiquant_conf_template)
    fp.close()
