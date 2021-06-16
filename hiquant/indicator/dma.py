# -*- coding: utf-8 -*-

from .basic import CROSS
from .ma import SMA

from ..core.indicator_signal import register_signal_indicator
# Different of Moving Average, by
# --------------------------------------------
def DMA(close, fast = 10, slow = 50, signal = 10):
    dma = SMA(close, fast) - SMA(close, slow)
    ama = SMA(dma, signal)
    return dma, ama

def signal_dma(df, inplace=False, fast=10, slow=50, signal=10):
    dma, ama = DMA(df.close, fast=fast, slow=slow, signal=signal)
    if inplace:
        df['dma'], df['dma_ama'] = dma, ama
    return CROSS(dma, ama)

register_signal_indicator('dma', signal_dma, ['dma', 'dma_ama'], 'DMA', 'trend')
