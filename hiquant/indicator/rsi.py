# -*- coding: utf-8 -*-

from .basic import CROSS, NON_ZERO, REF
from .ma import RMA
from ..core.indicator_signal import register_signal_indicator

# --------------------------------------------
def _rsi(up, dn, length):
    # Notice!!
    # It's not correct to use SUM or SMA as mentioned in many website
    # should use EMA instead.
    # a = SUM(up, period)
    # b = SUM(dn, period)
    # see: https://zhuanlan.zhihu.com/p/351213302
    a = RMA(up, length)
    b = RMA(dn, length)
    return a / NON_ZERO(a + b) * 100.0

# Relative Strength Index, by Welles Wilder, 1978
# --------------------------------------------
def RSI(close, fast = 6, middle = 12, slow = 24):
    up = close - REF(close, 1)
    dn = up.copy()
    up[ up < 0 ] = 0
    dn[ dn > 0 ] = 0
    return _rsi(up,dn,fast), _rsi(up,dn,middle), _rsi(up,dn,slow)

def signal_rsi(df, inplace=False, fast=6, middle=12, slow=24):
    rfast, rmid, rslow = RSI(df.close, fast=fast, middle=middle, slow=slow)
    if inplace:
        df['rsi_fast'], df['rsi_middle'], df['rsi_slow'] = rfast, rmid, rslow
        df['rsi_upper'], df['rsi_lower'] = 70, 30
    cross = CROSS(rfast, rmid)
    cross_up = CROSS(rfast, 70)
    cross_dn = CROSS(rfast, 30)
    buy_signal = (cross > 0) | (cross_dn < 0)
    sell_signal = (cross < 0) | (cross_up > 0)
    return buy_signal.astype(int) - sell_signal.astype(int)

register_signal_indicator('rsi', signal_rsi, ['rsi_fast', 'rsi_middle', 'rsi_slow', 'rsi_upper', 'rsi_lower'], 'RSI', 'obos')
