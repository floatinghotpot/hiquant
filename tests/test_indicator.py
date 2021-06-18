# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant import *

def test_basic():
    a = pd.Series([1 for i in range(10)])
    b = pd.Series([i for i in range(-10, 10)])

    print(a)
    print(b)

    print(MAX(a, 3))
    print(MIN(a, 3))
    print(REF(a, 1))

    print(NON_ZERO(b))

    print(SIGN(b))
    print(DIFF_SIGN(b))

    print(SUM(a, 3))

    print(ADD(a, 2))
    print(SUB(a, 2))
    print(MUL(a, 2))
    print(MUL(a, 0.5))

    print(ADD(a, b))
    print(SUB(a, b))
    print(MUL(a, b))
    print(DIV(a, b))

    print(ABS(b))
    print(POW(b, 2))

    print(VAR(b, 3))
    print(STDEV(b, 3))
    print(MAD(b, 3))

    print(CROSS(b, a))
    print(PEAK(b))

def test_indicators():
    df = get_daily('600036')
    df = df.iloc[-90:]
    indicators = get_all_signal_indicators()
    for k, item in indicators.items():
        print(k, item['type'], item['label'])
        func = item['func']
        signals = func(df)
