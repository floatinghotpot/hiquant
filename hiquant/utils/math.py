# -*- coding: utf-8; py-indent-offset:4 -*-

import math

def earn_to_annual(earn, days):
    if days > 365:
        year = days / 365
        return math.pow(earn+1, 1/year) -1
    else:
        return earn
