# -*- coding: utf-8 -*-

import pandas as pd

from ..core.indicator_signal import register_signal_indicator, signal_no_dup

# Main Fund Flow Index, by Liming Xie
def signal_mffi(df, inplace=False):
    mffi = df['main_pct'] if ('main_pct' in df.columns) else pd.Series(0, index=df.index)
    if inplace:
        df['mffi'] = mffi

    buy_signal = 5
    sell_signal = -5

    signal = (mffi >= buy_signal).astype(int) - (mffi <= sell_signal).astype(int)
    return signal #signal_no_dup(signal)

register_signal_indicator('mffi', signal_mffi, ['mffi'], 'MFFI', 'volume')
