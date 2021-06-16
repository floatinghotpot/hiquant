
from hiquant import *

def test_market():
    date_start = date_from_str('3 months ago')
    date_end = date_from_str('yesterday')

    market = Market(date_start, date_end)

    assert market is not None
