# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant import *

def test_push_base():
    push = PushBase({
        # keep empty
    })
    push.add_order('600036', '招商银行', 1000, 54.69, '', 'just test')
    push.add_order('600276', '恒瑞医药', 2000, 71.44, '', 'just test')
    push.flush()
    push.add_msg('hello, world!')
    push.clear()
