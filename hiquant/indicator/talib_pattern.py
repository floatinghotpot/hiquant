# -*- coding: utf-8 -*-

import pandas as pd
import talib as tl
from talib import abstract

from .basic import SIGN

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

positive_patterns = [
    'CDLSTALLEDPATTERN',
    'CDLINNECK',
    'CDLXSIDEGAP3METHODS',
    'CDLGAPSIDESIDEWHITE',
]

negative_patterns = [
    'CDLADVANCEBLOCK',
    'CDLHAMMER',
    'CDLINVERTEDHAMMER',
    'CDLGRAVESTONEDOJI',
    'CDLEVENINGSTAR',
    'CDLEVENINGDOJISTAR',
]

def PATTERN_SIGNAL(price):
    signals = pd.Series([0] * price.shape[0], index=price.index)
    all_patterns = tl.get_function_groups()['Pattern Recognition']

    for name in positive_patterns:
        if name in all_patterns:
            func = abstract.Function(name)
            pattern_signals = func(price)
            signals += pattern_signals

    for name in negative_patterns:
        if name in all_patterns:
            func = abstract.Function(name)
            pattern_signals = func(price)
            signals -= pattern_signals

    return SIGN(signals)
