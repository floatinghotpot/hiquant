# -*- coding: utf-8 -*-

from .basic import DIFF_SIGN, NON_ZERO
from .ma import SMA

# On Balance Volume (OBV)
# --------------------------------------------
def OBV(close, volume, length = 30):
    signed_vol = DIFF_SIGN(close, 1) * volume
    obv = signed_vol.cumsum()
    return obv

# Improved OBV
# --------------------------------------------
def OBV2(close, high, low, volume, length = 30):
    obv = ((close - low) - (high - close)) / NON_ZERO(high - low) * volume
    maobv = SMA(obv, length)
    return obv, maobv
