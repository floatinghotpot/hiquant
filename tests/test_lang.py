# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant import *

def test_lang():
    set_lang('zh')
    assert(get_lang() == 'zh')
    assert LANG('buy') == '买入'
    assert LANG('sell') == '卖出'

    set_lang('en')
    assert(get_lang() == 'en')
    assert LANG('buy') == 'buy'
    assert LANG('sell') == 'sell'
