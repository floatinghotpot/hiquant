# -*- coding: utf-8; py-indent-offset:4 -*-

import multiprocessing as mp
import datetime as dt

def func(i):
    for j in range(2000000):
        n = i * i
    return n

def test_for(n = 20):
    input = [i for i in range(n)]
    output = [func(i) for i in input]
    print(input[-1], output[-1])

def test_pool(n = 20):
    with mp.Pool(10) as p:
        input = [i for i in range(n)]
        output = p.map(func, input)
        print(input[-1], output[-1])

class A:
    def method(self, i):
        return func(i)

def test_pool_class(n = 20):
    a = A()
    with mp.Pool(10) as p:
        input = [i for i in range(n)]
        output = p.map(a.method, input)
        print(input[-1], output[-1])

if __name__ == "__main__":
    print('cpu count:', mp.cpu_count())

    n = 40
    t1 = dt.datetime.now()
    test_for(n)
    t2 = dt.datetime.now()
    test_pool(n)
    t3 = dt.datetime.now()
    test_pool_class(n)
    t4 = dt.datetime.now()
    print(t2 - t1, '\n', t3 - t2, '\n', t4 - t3)
