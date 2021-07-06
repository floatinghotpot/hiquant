# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import configparser

from ..utils import dict_from_config_items

class OrderCost:
    close_tax = 0.001
    open_commission = 0.0003
    close_commission = 0.0003
    min_commission = 5.0

    def __init__(self, close_tax = 0.001, open_commission = 0.0003, close_commission = 0.0003, min_commission = 5.0):
        self.close_tax = close_tax
        self.open_commission = open_commission
        self.close_commision = close_commission
        self.min_commission = min_commission

def get_order_cost(global_config = None):
    order_cost_conf = None
    if (global_config is not None) and ('order_cost' in global_config.sections()):
        order_cost_conf = dict_from_config_items(global_config.items('order_cost'))
    else:
        hiquant_conf_file = 'hiquant.conf'
        if os.path.isfile(hiquant_conf_file):
            config = configparser.ConfigParser()
            config.read(hiquant_conf_file, encoding='utf-8')
            order_cost_conf = dict_from_config_items(config.items('order_cost'))

    if order_cost_conf is not None:
        return OrderCost(
            float(order_cost_conf['close_tax']),
            float(order_cost_conf['open_commission']),
            float(order_cost_conf['close_commission']),
            float(order_cost_conf['min_commission']),
        )
    else:
        return OrderCost(0.001, 0.0003, 0.0003, 5.0)
