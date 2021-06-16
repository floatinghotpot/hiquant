# -*- coding: utf-8 -*-

from .basic import CROSS, NON_ZERO, STDEV
from .ma import SMA
from ..core.indicator_signal import register_signal_indicator

# Bollinger Bands, by John Bollinger, 1980s
# --------------------------------------------
def BOLL(close, length = 20, std = 2.0, ddof=0):
    std = float(std) if std and std > 0 else 2.0
    ddof = int(ddof) if ddof >= 0 and ddof < length else 1
    stdev = STDEV(close, length, ddof)
    dev = std * stdev
    mid = SMA(close, length)
    lower = mid - dev
    upper = mid + dev
    bandwidth = (upper - lower) / NON_ZERO(mid) * 100.0
    return mid, upper, lower, bandwidth

def signal_boll(df, inplace=False, length=20, std=2, ddof=0):
    mb, up, dn, width = BOLL(df.close, length=length, std=std, ddof=ddof)
    if inplace:
        df['boll'], df['boll_upper'], df['boll_lower'], df['boll_width'] = mb, up, dn, width
    buy_signal = CROSS(df.close, dn) > 0
    sell_signal = CROSS(df.close, up) < 0
    return buy_signal.astype(int) - sell_signal.astype(int)

register_signal_indicator('boll', signal_boll, ['boll', 'boll_upper', 'boll_lower'], 'BOLL', 'obos')
