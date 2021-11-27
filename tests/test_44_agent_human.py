# -*- coding: utf-8; py-indent-offset:4 -*-

from hiquant import *

def test_agent_human():
    date_start = date_from_str('3 months ago')
    date_end = date_from_str('1 week ago')
    market = Market(date_start, date_end)

    agent_conf = {
        'portfolio_load': 'data/account_1_portfolio_load.csv',
        'portfolio_save': 'data/account_1_portfolio_save.csv',
        'order': 'data/account_1_order.csv',
    }
    agent = HumanAgent(market, agent_conf)
    agent.init_portfolio(start_cash = 1000000.00)

    agent.order('600036', 1000)
    agent.order_target('600036', 0)
    agent.order_value('600036', 100000.00)
    agent.order_target_value('600036', 200000.00)
    agent.before_day()
    agent.after_day()
    agent.before_tick()
    agent.after_tick()

    agent.get_transaction_count()

    p = agent.get_portfolio()
    df = p.to_dataframe()
    value = p.total_value()

if __name__ == "__main__":
    test_agent_human()
