# -*- coding: utf-8 -*-

from .basic import REF, CROSS
from .ma import SMA, EMA
from ..core.indicator_signal import register_signal_indicator

# Triple ExponentiallySmoothed Average
# --------------------------------------------
def TRIX(close, length = 12, signal = 20):
    tr = EMA(EMA(EMA(close,length),length),length)
    ref = REF(tr,1)
    trix = (tr - ref) / ref * 100.0
    trma = SMA(trix, signal)
    return trix, trma
 
def signal_trix(df, inplace=False, length=10, signal=20):
    trix, trix_ma = TRIX(df.close, length=length, signal=signal)
    if inplace:
        df['trix'], df['trix_ma'] = trix, trix_ma
    return CROSS(trix, trix_ma)

register_signal_indicator('trix', signal_trix, ['trix', 'trix_ma'], 'TRIX', 'trend')
