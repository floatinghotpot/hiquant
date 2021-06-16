
import pandas as pd
from hiquant import *

def test_calc():
  a = pd.Series([1 for i in range(10)])
  b = pd.Series([i for i in range(10)])

  print(a)
  print(b)

  print(ADD(a, 1))
  print(MUL(a, 2))

  print(ADD(a, b))
  print(MUL(a, b))

  print(REF(b, 1))
  print(SUM(a, 3))
