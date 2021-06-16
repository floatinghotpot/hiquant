# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

from .basic import CROSS
from .ma import EMA
from ..core.indicator_signal import register_signal_indicator

# Parabolic Stop And Reverse (psar)
# --------------------------------------------
def SAR(close, high, low, af=0.02, max_af=0.2):
    af = float(af) if af and af > 0 else 0.02
    max_af = float(max_af) if max_af and max_af > 0 else 0.2

    # initialize
    m = high.shape[0]
    af0 = af
    bullish = True
    high_point = high.iloc[0]
    low_point = low.iloc[0]

    if close is not None:
        sar = close.copy()
    else:
        sar = low.copy()
        
    long = pd.Series(np.NAN, index=sar.index)
    short = long.copy()
    reversal = pd.Series(False, index=sar.index)
    _af = long.copy()
    _af.iloc[0:2] = af0

    # Calculate Result
    for i in range(2, m):
        reverse = False
        _af.iloc[i] = af

        if bullish:
            sar.iloc[i] = sar.iloc[i - 1] + af * (high_point - sar.iloc[i - 1])

            if low.iloc[i] < sar.iloc[i]:
                bullish, reverse, af = False, True, af0
                sar.iloc[i] = high_point
                low_point = low.iloc[i]
        else:
            sar.iloc[i] = sar.iloc[i - 1] + af * (low_point - sar.iloc[i - 1])

            if high.iloc[i] > sar.iloc[i]:
                bullish, reverse, af = True, True, af0
                sar.iloc[i] = low_point
                high_point = high.iloc[i]

        reversal.iloc[i] = reverse

        if not reverse:
            if bullish:
                if high.iloc[i] > high_point:
                    high_point = high.iloc[i]
                    af = min(af + af0, max_af)
                if low.iloc[i - 1] < sar.iloc[i]:
                    sar.iloc[i] = low.iloc[i - 1]
                if low.iloc[i - 2] < sar.iloc[i]:
                    sar.iloc[i] = low.iloc[i - 2]
            else:
                if low.iloc[i] < low_point:
                    low_point = low.iloc[i]
                    af = min(af + af0, max_af)
                if high.iloc[i - 1] > sar.iloc[i]:
                    sar.iloc[i] = high.iloc[i - 1]
                if high.iloc[i - 2] > sar.iloc[i]:
                    sar.iloc[i] = high.iloc[i - 2]

        if bullish:
            long.iloc[i] = sar.iloc[i]
        else:
            short.iloc[i] = sar.iloc[i]

    return long, short, _af, reversal

def signal_sar(df, inplace=False, af=0.02, max_af=0.2):
    long, short, af, reversal = SAR(df.close, df.high, df.low, af=af, max_af=max_af)
    if inplace:
        df['sar_long'], df['sar_short'] = long, short
    tmp = long.fillna(0) - short.fillna(0)
    tmp[ tmp > 0 ] = 1
    tmp[ tmp < 0 ] = 0
    return tmp.diff(1)

register_signal_indicator('sar', signal_sar, ['sar_long', 'sar_short'], 'SAR', 'trend')
