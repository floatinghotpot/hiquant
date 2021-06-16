
    df = ak.stock_zh_a_daily(symbol=symbol, start_date=start, end_date=end, adjust=adjust)
  File "/usr/local/lib/python3.9/site-packages/akshare/stock/zh_stock_a_sina.py", line 181, in stock_zh_a_daily
    temp_df = pd.merge(
  File "/usr/local/lib/python3.9/site-packages/pandas/core/reshape/merge.py", line 89, in merge
    return op.get_result()
  File "/usr/local/lib/python3.9/site-packages/pandas/core/reshape/merge.py", line 684, in get_result
    join_index, left_indexer, right_indexer = self._get_join_info()
  File "/usr/local/lib/python3.9/site-packages/pandas/core/reshape/merge.py", line 896, in _get_join_info
    join_index, left_indexer, right_indexer = left_ax.join(
  File "/usr/local/lib/python3.9/site-packages/pandas/core/indexes/datetimelike.py", line 893, in join
    this, other = self._maybe_utc_convert(other)
  File "/usr/local/lib/python3.9/site-packages/pandas/core/indexes/datetimes.py", line 413, in _maybe_utc_convert
    raise TypeError("Cannot join tz-naive with tz-aware DatetimeIndex")
TypeError: Cannot join tz-naive with tz-aware DatetimeIndex

This error will happen when using py-mini-racer 0.6.0, and will fix if replace with 0.5.0

$ pip install py-mini-racer==0.5.0


