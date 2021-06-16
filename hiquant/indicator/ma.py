# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

from .basic import CROSS
from ..core.indicator_signal import register_signal_indicator

# Simple Moving Average (SMA)
# --------------------------------------------
def SMA(data, length):
    return data.rolling(length, min_periods=1).mean()

# Exponential Moving Average (EMA)
# --------------------------------------------
def EMA(data, length):
    return data.ewm(span=length, min_periods=1).mean()

# Rolling Moving Average
# --------------------------------------------
def RMA(data, length):
    alpha = (1.0 / length) if length > 0 else 0.5
    return data.ewm(alpha=alpha, min_periods=1).mean()

# Weighted Moving Average
# --------------------------------------------
def WMA(data, length=None, asc=None):
    asc = asc if asc else True

    total_weight = 0.5 * length * (length + 1)
    weights_ = pd.Series(np.arange(1, length + 1))
    weights = weights_ if asc else weights_[::-1]

    def linear(w):
        def _compute(x):
            diff = len(w) - len(x)
            if diff > 0:
                x = np.insert(x, 0, [ x[0] ] * diff)
            return np.dot(x, w) / total_weight
        return _compute

    close_ = data.rolling(length, min_periods=1)
    wma = close_.apply(linear(weights), raw=True)
    return wma

# Hull Moving Average，HMA
# --------------------------------------------
def HMA(data, length):
    half_length = int(length / 2)
    sqrt_length = int(np.sqrt(length))
    wmaf = WMA(data, length=half_length)
    wmas = WMA(data, length=length)
    hma = WMA(2 * wmaf - wmas, length=sqrt_length)
    return hma

# MA, call other implmentations
# --------------------------------------------
def MA(name:str = None, data:pd.Series = None, **kwargs) -> pd.Series:
    _mas = [
        "dema", "ema", "fwma", "hma", "linreg", "midpoint", "pwma", "rma",
        "sinwma", "sma", "swma", "t3", "tema", "trima", "vidya", "wma", "zlma"
    ]
    if name is None and data is None:
        return _mas
    elif isinstance(name, str) and name.lower() in _mas:
        name = name.lower()
    else: # "ema"
        name = _mas[1]

    if name == "sma": return SMA(data, **kwargs)
    elif name == "rma": return RMA(data, **kwargs)
    elif name == "hma": return HMA(data, **kwargs)
    elif name == "wma": return WMA(data, **kwargs)
    #elif name == "dema": return dema(data, **kwargs)
    #elif name == "fwma": return fwma(data, **kwargs)
    #elif name == "linreg": return linreg(data, **kwargs)
    #elif name == "midpoint": return midpoint(data, **kwargs)
    #elif name == "pwma": return pwma(data, **kwargs)
    #elif name == "sinwma": return sinwma(data, **kwargs)
    #elif name == "swma": return swma(data, **kwargs)
    #elif name == "t3": return t3(data, **kwargs)
    #elif name == "tema": return tema(data, **kwargs)
    #elif name == "trima": return trima(data, **kwargs)
    #elif name == "vidya": return vidya(data, **kwargs)
    #elif name == "zlma": return zlma(data, **kwargs)
    else: return EMA(data, **kwargs)

def signal_ma(df, inplace=False, fast=5, slow=20):
    periods = [5, 10, 20, 30, 60]
    if not fast in periods:
        periods.append(fast)
    if not slow in periods:
        periods.append(fast)
    for period in periods:
        ma = SMA(df.close, period)
        if inplace:
            df[ 'ma' + str(period) ] = ma
        if period == fast:
            ma_fast = ma
        elif period == slow:
            ma_slow = ma
    return CROSS(ma_fast, ma_slow)

register_signal_indicator('ma', signal_ma, ['ma5', 'ma10', 'ma20', 'ma30', 'ma60'], 'MA', 'trend')
