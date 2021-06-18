# -*- coding: utf-8; py-indent-offset:4 -*-

import datetime as dt
from .lang import LANG

class PushBase:
    conf = None
    msg_queue = []
    verbose = False

    def __init__(self, conf):
        self.conf = conf.copy()

    def set_verbose(self, verbose = True):
        self.verbose = verbose

    def add_msg(self, msg):
        self.msg_queue.append(msg)
        pass

    def add_order(self, symbol, name, count, price, earn_str = '', comment = ''):
        trade = LANG('You can buy') if count > 0 else LANG('You can sell')
        msg = '{} {}, {} {} * {}, {} {}'.format(symbol, name, trade, count, price, earn_str, comment)
        self.msg_queue.append(msg)
        if self.verbose:
            print(msg)

    def clear(self):
        self.msg_queue = []

    def flush(self):
        if not self.msg_queue:
            return

        line = '-' * 40
        content = '\n\n'.join(self.msg_queue)
        content += '\n' + line + '\n' + dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n'

        if self.verbose:
            print(content)

        self.msg_queue = []
