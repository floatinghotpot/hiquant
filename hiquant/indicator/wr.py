# -*- coding: utf-8 -*-

from .basic import CROSS, NON_ZERO, MIN, MAX
from ..core.indicator_signal import register_signal_indicator

# William %R, by Larry Williams, 1973
# --------------------------------------------
def WR(close, high, low, length = 30):
    lowest_low = MIN(low, length)
    highest_high = MAX(high, length)
    wr = (highest_high - close) / NON_ZERO(highest_high - lowest_low) * 100.0
    return wr

def signal_wr(df, inplace=False, length=10):
    wr = WR(df.close, df.high, df.low, length=length)
    if inplace:
        df['wr'], df['wr_upper'], df['wr_lower'] = wr, 80, 20
    buy_signal = CROSS(wr, 80) > 0
    sell_signal = CROSS(wr, 20) < 0
    return buy_signal.astype(int) - sell_signal.astype(int)

register_signal_indicator('wr', signal_wr, ['wr', 'wr_upper', 'wr_lower'], 'W%R', 'obos')
