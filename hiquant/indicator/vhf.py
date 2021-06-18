# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from sys import float_info as sflt

from .basic import CROSS
from ..core.indicator_signal import register_signal_indicator

# Vertical Horizontal Filter
# --------------------------------------------
def VHF(close, length = 28):
    hcp = close.rolling(length, min_periods=1).max()
    lcp = close.rolling(length, min_periods=1).min()
    sm = (close - close.shift(1)).abs().rolling(length, min_periods=1).sum()
    vhf = (hcp - lcp) / sm
    return vhf

def signal_vhf(df, inplace=False, length=28):
    vhf = VHF(df.close)
    if inplace:
        df['vhf'], df['vhf_lower'] = vhf, 0.35
    return CROSS(vhf, 0.35)

register_signal_indicator('vhf', signal_vhf, ['vhf', 'vhf_lower'], 'VHF', 'trend')
