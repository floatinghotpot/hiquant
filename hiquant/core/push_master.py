# -*- coding: utf-8; py-indent-offset:4 -*-

class MasterPush:
    services = []

    def __init__(self):
        self.services = []

    def add_service(self, push_service):
        self.services.append(push_service)

    def set_verbose(self, verbose = True):
        for k in self.services:
            k.set_verbose(verbose)

    def add_msg(self, msg):
        for k in self.services:
            k.add_msg(msg)

    def add_order(self, symbol, name, count, price, earn_str = '', comment = ''):
        for k in self.services:
            k.add_order(symbol, name, count, price, earn_str, comment)

    def flush(self):
        for k in self.services:
            k.flush()

    def clear(self):
        for k in self.services:
            k.clear()

