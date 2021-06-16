# -*- coding: utf-8 -*-

from .basic import CROSS
from .ma import SMA
from ..core.indicator_signal import register_signal_indicator

# --------------------------------------------
def ENE(close, length = 25, m1 = 6, m2 = 6):
    ma = SMA(close, length)
    up = ma * (1 + m1/100.0)
    dn = ma * (1 - m2/100.0)
    ene = (up + dn) / 2.0
    return ene, up, dn

