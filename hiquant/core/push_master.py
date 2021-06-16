# -*- coding: utf-8; py-indent-offset:4 -*-

from .push_email import *

class MasterPush:
    services = []

    def __init__(self, global_config, str_services):
        self.services = []
        items = str_services.replace(' ','').split('.')
        for k in items:
            conf = {}
            for k, v in global_config.items(k):
                conf[k] = v
            push_type = conf['push_type']
            if push_type == 'email':
                self.services.append( EmailPush(conf.copy()) )
            elif push_type == 'wechat':
                #self.services.append( WeChatPush(conf.copy()) )
                pass
            elif push_type == 'sms':
                #self.services.append( SmsPush(conf.copy()) )
                pass

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

