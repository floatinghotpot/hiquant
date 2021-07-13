# -*- coding: utf-8 -*-

import pandas as pd

from ..core.indicator_signal import register_signal_indicator, signal_no_dup

# Main Fund Flow Index, by Liming Xie
def signal_mffi(df, inplace=False, days= 1, percent= 5.0):
    mffi = df['main_pct'] if ('main_pct' in df.columns) else pd.Series(0, index=df.index)
    if inplace:
        df['mffi'] = mffi

    # main fundflow in/out for over two days
    signal = pd.Series(0, index=mffi.index)
    n = len(signal.tolist())
    for i in range(days-1, n):
        for j in range(0, days):
            if mffi.iloc[i-j] > percent:
                signal.iloc[i] += 1
            elif mffi.iloc[i-j] < -percent:
                signal.iloc[i] += -1
        signal.iloc[i] //= days

    return signal #signal_no_dup(signal)

register_signal_indicator('mffi', signal_mffi, ['mffi'], 'MFFI', 'volume')
