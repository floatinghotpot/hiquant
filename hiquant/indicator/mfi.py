# -*- coding: utf-8 -*-

import pandas as pd

from .basic import CROSS, REF
from .ma import EMA
from ..core.indicator_signal import register_signal_indicator

# Money Flow Index, by Gene Quong & Avrum Soudack
# --------------------------------------------
def MFI(close, high, low, volume, length = 14, n = 6):
    tp = (high + low + close) / 3.0
    mf = tp * volume
    diff = tp - REF(tp, 1)

    tdf = pd.DataFrame({"diff": 0, "rmf": mf, "+mf": 0, "-mf": 0})
    tdf.loc[(diff > 0), "diff"] = 1
    tdf.loc[tdf["diff"] == 1, "+mf"] = mf

    tdf.loc[(diff < 0), "diff"] = -1
    tdf.loc[tdf["diff"] == -1, "-mf"] = mf

    psum = tdf["+mf"].rolling(length, min_periods=1).sum()
    nsum = tdf["-mf"].rolling(length, min_periods=1).sum()
    mfi = 100 * psum / (psum + nsum)

    return mfi

def signal_mfi(df, inplace=False, length=14, n=6):
    mfi = MFI(df.close, df.high, df.low, df.volume, length=length, n=n)
    if inplace:
        df['mfi'], df['mfi_upper'], df['mfi_lower'] = mfi, 80, 20
    buy_signal = CROSS(mfi, 80) < 0
    sell_signal = CROSS(mfi, 20) > 0
    return buy_signal.astype(int) - sell_signal.astype(int)

register_signal_indicator('mfi', signal_mfi, ['mfi','mfi_upper','mfi_lower'], 'MFI', 'volume')
