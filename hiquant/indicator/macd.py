# -*- coding: utf-8 -*-

from .basic import CROSS
from .ma import EMA
from ..core.indicator_signal import register_signal_indicator

# Moving Average Convergence and Divergence, by Geral Appel, 1979
# ----------------------------------------------------------------
def MACD(close, fast = 12, slow = 26, signal = 9):
    dif = EMA(close, fast) - EMA(close, slow)
    dea = EMA(dif, signal)
    macd = (dif - dea) * 2.0
    return dif, dea, macd

def signal_macd(df, inplace=False, fast=12, slow=26, signal=9):
    dif, dea, macd_hist = MACD(df.close, fast=fast, slow=slow, signal=signal)
    if inplace:
        df['macd_dif'], df['macd_dea'], df['macd_hist'] = dif, dea, macd_hist
    return CROSS(dif, dea)

register_signal_indicator('macd', signal_macd, ['macd_dif', 'macd_dea', 'macd_hist'], 'MACD', 'trend')
