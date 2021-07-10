# -*- coding: utf-8 -*-

import pandas as pd

def signal_no_dup(signal):
    sig = signal[0]
    for i in range(1, signal.size):
        s = signal.iloc[i]
        if s == 0:
            continue
        elif s == sig: # same
            signal.iloc[i] = 0
        else: # different, change compare target
            sig = s

    return signal

def signal_to_long(signal, time_factor = 1.0):
    # remove dup signal to avoid cumsum exceed 1
    signal = signal_no_dup(signal)

    # remove first trade signal if it's sell signal
    for i in range(signal.size):
        s = signal.iloc[i]
        if s == 0:
            continue
        elif s > 0:
            break
        else:
            signal.iloc[i] = 0
            break

    # cumsum, valid pos value should be either 0 or 1
    long_pos = signal.cumsum().fillna(0)

    if time_factor < 0 or time_factor > 1.0:
        raise ValueError('please make sure 0 <= long_factor <= 1')

    # if buy/sell in time, we can earn more and lose less
    long_factor = 1.0 - time_factor
    short_factor = time_factor
    pos = 0
    for i in range(long_pos.size):
        p = long_pos.iloc[i]
        if p > pos: # first long pos, it's a buy
            long_pos.iloc[i] = long_factor
            pos = p
        elif p < pos: # first short pos, it's a sell
            long_pos.iloc[i] = short_factor
            pos = p

    return long_pos

_registered_signal_indicators = {
    # id: {
    # 'func': function(),
    # 'cols': [],
    # 'type': '',
    # 'label': '',
    # }
}

def get_all_signal_indicators():
    return _registered_signal_indicators

def list_signal_indicators():
    return _registered_signal_indicators.keys()

def register_signal_indicator(id, func, cols, label, ind_type):
    _registered_signal_indicators[ id ] = {
        'func': func,
        'cols': cols,
        'type': ind_type,
        'label': label,
    }

def gen_indicator_signal(df, indicators, time_factor = 1.0, inplace=False):
    signal = pd.Series(0, index=df.index)
    for k in indicators:
        if k in _registered_signal_indicators:
            values = _registered_signal_indicators[k]
            signal_func = values['func']
            # use + to merge the signals
            signal += signal_func(df, inplace=inplace)
            if len(indicators) == 1:
                return signal
        else:
            print(k, 'not found in registered indicators')

    return signal_no_dup(signal)
