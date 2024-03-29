# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from sys import float_info as sflt

# --------------------------------------------
def MAX(data, length):
    return data.rolling(length, min_periods=1).max()

# --------------------------------------------
def MIN(data, length):
    return data.rolling(length, min_periods=1).min()

# --------------------------------------------
def REF(data, length):
    return data.shift(length).fillna(method='bfill')

# --------------------------------------------
def NON_ZERO(data):
    if data.eq(0).any():
        return data + sflt.epsilon
    return data

# --------------------------------------------
def SIGN(data):
    data = data.copy()
    data[data > 0] = 1
    data[data < 0] = -1
    return data

# --------------------------------------------
def DIFF_SIGN(data, initial = 0, drift = 1):
    sign = data.diff(drift)
    sign[sign > 0] = 1
    sign[sign < 0] = -1
    sign.iloc[0] = initial
    return sign

# --------------------------------------------
def SUM(data, length):
    return data.rolling(length, min_periods=1).sum()

# ---------------------------------------------------------
def ADD(data1, data2):
    return data1 + data2

# ---------------------------------------------------------
def SUB(data1, data2):
    return data1 - data2

# ---------------------------------------------------------
def MUL(data1, data2):
    return data1 * data2

# ---------------------------------------------------------
def DIV(data1, data2):
    return data1 / NON_ZERO(data2)

# --------------------------------------------
def ABS(data):
    return data.abs()

# --------------------------------------------
def POW(data, x):
    return data.pow(x)

# --------------------------------------------
def VAR(data, length, ddof=None):
    ddof = int(ddof) if ddof and ddof >= 0 and ddof < length else 0
    var = data.rolling(length, min_periods=1).var(ddof)
    return var

# --------------------------------------------
def STDEV(data, length, ddof=None):
    ddof = int(ddof) if ddof and ddof >= 0 and ddof < length else 0
    stdev = VAR(data, length, ddof=ddof).apply(np.sqrt)
    return stdev

# --------------------------------------------
def MAD(data, length, ddof=None):
    def _mad(series):
        return np.fabs(series - series.mean()).mean()

    mad = data.rolling(length, min_periods=1).apply(_mad, raw=True)
    return mad

# return, up = 1, down = -1, no = 0
# --------------------------------------------
def CROSS(fast, slow):
    d = fast - slow
    d[ d <= 0 ] = 0
    d[ d > 0 ] = 1
    return d.diff(1)

# return, top = 1, bottom = -1, no = 0
# --------------------------------------------
def PEAK(data):
    # we cannot predict future, so shift 2 days
    data = REF(data, 2)
    data = DIFF_SIGN(data,drift=1) + DIFF_SIGN(data,drift=-1) + DIFF_SIGN(data,drift=2) + DIFF_SIGN(data,drift=-2)
    # if >= 3, large than near 3 or 4 values, we regard it a peak
    return data // 3

def is_percent(x: int or float) -> bool:
    if isinstance(x, (int, float)):
        return x is not None and x >= 0 and x <= 100
    return False

def INCREASING(close, length=1, strict=False, asint=True, percent=None, drift=1):
    # Validate Arguments
    length = int(length) if length and length > 0 else 1
    strict = strict if isinstance(strict, bool) else False
    asint = asint if isinstance(asint, bool) else True
    percent = float(percent) if is_percent(percent) else False

    if close is None: return

    # Calculate Result
    close_ = (1 + 0.01 * percent) * close if percent else close
    if strict:
        # Returns value as float64? Have to cast to bool
        increasing = close > close_.shift(drift)
        for x in range(3, length + 1):
            increasing = increasing & (close.shift(x - (drift + 1)) > close_.shift(x - drift))

        increasing.fillna(0, inplace=True)
        increasing = increasing.astype(bool)
    else:
        increasing = close_.diff(length) > 0

    if asint:
        increasing = increasing.astype(int)

    return increasing

def DECREASING(close, length=1, strict=False, asint=True, percent=0, drift=1):
    length = int(length) if length and length > 0 else 1
    strict = strict if isinstance(strict, bool) else False
    asint = asint if isinstance(asint, bool) else True
    percent = float(percent) if percent else False

    # Calculate Result
    close_ = (1 - 0.01 * percent) * close if percent else close
    if strict:
        # Returns value as float64? Have to cast to bool
        decreasing = close < close_.shift(drift)
        for x in range(3, length + 1):
            decreasing = decreasing & (close.shift(x - (drift + 1)) < close_.shift(x - drift))

        decreasing.fillna(0, inplace=True)
        decreasing = decreasing.astype(bool)
    else:
        decreasing = close_.diff(length) < 0

    if asint:
        decreasing = decreasing.astype(int)

    return decreasing
