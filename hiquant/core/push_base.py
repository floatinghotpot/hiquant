
class PushBase:
    conf = None
    msg_queue = []

    def __init__(self, conf):
        self.conf = conf.copy()

    def add_msg(self, msg):
        self.msg_queue.append(msg)
        pass

    def add_order(self, symbol, name, count, price, earn_str = '', comment = ''):
        trade = '建议买入' if count > 0 else '建议卖出'
        msg = '{} {}, {} {} * {}, {} {}'.format(symbol, name, trade, count, price, earn_str, comment)
        self.msg_queue.append(msg)

    def clear(self):
        self.msg_queue = []

    def flush(self):
        pass
