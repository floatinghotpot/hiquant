# -*- coding: utf-8 -*-

from .basic import MIN, MAX, NON_ZERO, CROSS
from .ma import RMA
from ..core.indicator_signal import register_signal_indicator

# KDJ index, by George Lane
# --------------------------------------------
def KDJ(close, high, low, length = 9, signal = 3):
    lowest_low = MIN(low, length)
    highest_high = MAX(high, length)
    rsv = (close - lowest_low) / NON_ZERO(highest_high - lowest_low) * 100.0
    k = RMA(rsv, length=signal)
    d = RMA(k, length=signal)
    j = 3 * k - 2 * d
    return k, d, j

def signal_kdj(df, inplace=False, length=9, signal=3):
    k, d, j = KDJ(df.close, df.high, df.low, length=length, signal=signal)
    if inplace:
        df['kdj_k'], df['kdj_d'], df['kdj_j'] = k, d, j
    cross = CROSS(k, d)
    buy_signal = (cross > 0) | (k < 20)
    sell_signal = (cross < 0) | (k > 80)
    return buy_signal.astype(int) - sell_signal.astype(int)

register_signal_indicator('kdj', signal_kdj, ['kdj_k', 'kdj_d', 'kdj_j'], 'KDJ', 'obos')
