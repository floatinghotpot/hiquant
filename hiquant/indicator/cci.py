# -*- coding: utf-8 -*-

from .basic import CROSS, NON_ZERO, MAD
from .ma import SMA
from ..core.indicator_signal import register_signal_indicator

# Commodity Channel Index, by Donald Lambert, 1980s
# --------------------------------------------
def CCI(close, high, low, length = 14, c = None):
    c = float(c) if c and c > 0 else 0.015
    tp = (high + low + close) / 3.0
    mtp = SMA(tp, length)
    mad_tp = MAD(tp, length)
    cci = (tp - mtp) / NON_ZERO(mad_tp * c)
    return cci

def signal_cci(df, inplace=False, length=14):
    cci = CCI(df.close, df.high, df.low, length=length)
    if inplace:
        df['cci'], df['cci_upper'], df['cci_lower'] = cci, 100, -100
    cross_up = CROSS(cci, 100)
    cross_md = CROSS(cci, 0)
    cross_dn = CROSS(cci, -100)
    buy_signal = (cross_up > 0) | (cross_md > 0) | (cross_dn > 0)
    sell_signal = (cross_up < 0) | (cross_md < 0) | (cross_dn < 0)
    return buy_signal.astype(int) - sell_signal.astype(int)

register_signal_indicator('cci', signal_cci, ['cci', 'cci_upper', 'cci_lower'], 'CCI', 'obos')
