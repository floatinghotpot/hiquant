import pandas as pd
import numpy as np

def test_series():
  s1 = pd.Series([1, 3, 5, np.nan, 6, 8])
  s2 = pd.Series([i for i in range(6)])
  print(s1)
  print(s2)
  print(s1 * 2)
  print(s1 * s1)
  print(1.0 / s2)
  print(s2 - s1)
  print(abs(s2-s1))
  print(s2.pow(2))

