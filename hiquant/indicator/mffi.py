# -*- coding: utf-8 -*-

import pandas as pd

from ..core.indicator_signal import long_to_signal, register_signal_indicator, signal_to_long

# Main Fund Flow Index, by Liming Xie
def signal_mffi(df, inplace=False):
    mffi = df['main_pct'] if ('main_pct' in df.columns) else pd.Series(0, index=df.index)
    if inplace:
        df['mffi'] = mffi
    buy_signal = mffi > 3.0
    sell_signal = mffi < -3.0
    signal = buy_signal.astype(int) - sell_signal.astype(int)
    long = signal_to_long(signal)
    return long_to_signal(long)

register_signal_indicator('mffi', signal_mffi, ['mffi'], 'MFFI', 'volume')
