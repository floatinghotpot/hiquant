# -*- coding: utf-8 -*-

import pandas as pd

def signal_to_long(signal, long_value = 1, short_value = 0):
    trend = [0 for i in range(signal.size)]
    for i in range(0, signal.size):
        s = signal.iloc[i]
        if s > 0:
            trend[i] = long_value
        elif s < 0:
            trend[i] = short_value
        elif i > 0:
            trend[i] = trend[i-1]
    return pd.Series(trend, index=signal.index)

def long_to_signal(trend):
    return trend.diff(1).fillna(0)

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
 
def gen_indicator_signal(df, indicators, inplace=False):
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

    long = signal_to_long(signal)
    return long.diff(1).fillna(0)
