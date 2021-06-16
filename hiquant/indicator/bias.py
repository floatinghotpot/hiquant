# -*- coding: utf-8 -*-

from .ma import SMA
from ..core.indicator_signal import register_signal_indicator

# --------------------------------------------
def _bias(close, length):
    return (close / SMA(close, length) - 1) * 100.0

# --------------------------------------------
def BIAS(close, fast = 6, middle = 12, slow = 24):
    return _bias(close,fast), _bias(close,middle), _bias(close,slow)

def signal_bias(df, inplace=False, fast=6, middle=12, slow=24):
    bfast, bmiddle, bslow = BIAS(df.close, fast=fast, middle=middle, slow=slow)
    if inplace:
        df['bias_fast'], df['bias_middle'], df['bias_slow'] = bfast, bmiddle, bslow
    buy_signal = (bmiddle < -8) | (bslow < -16)
    sell_signal = (bmiddle > 8) | (bslow > 16)
    return buy_signal.astype(int) - sell_signal.astype(int)

register_signal_indicator('bias', signal_bias, ['bias_fast','bias_middle','bias_slow'], 'BIAS', 'obos')
