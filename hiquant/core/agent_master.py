# -*- coding: utf-8; py-indent-offset:4 -*-

from .agent_simulated import *
from .agent_human import *

class MasterAgent:
    fund = None
    agents = []
    def __init__(self, fund, str_agents):
        self.fund = fund
        self.agents = []
        items = str_agents.replace(' ','').split(',')
        for agent_id in items:
            agent_conf = {}
            for k, v in fund.global_config.items( agent_id ):
                agent_conf[k] = v
            agent_type = agent_conf['agent_type']
            if agent_type == 'simulated':
                self.agents.append( SimulatedAgent(fund, agent_conf) )
            elif agent_type == 'human':
                self.agents.append( HumanAgent(fund, agent_conf) )
            elif agent_type == 'automated':
                #self.agents.append( AutomatedAgent(fund, agent_conf) )
                pass

    def before_day(self):
        for agent in self.agents:
            agent.before_day()

    def after_day(self):
        for agent in self.agents:
            agent.after_day()

    def before_tick(self):
        for agent in self.agents:
            agent.before_tick()

    def after_tick(self):
        for agent in self.agents:
            agent.after_tick()

    def get_portfolio(self):
        return self.agents[0].get_portfolio()

    def get_transaction_count(self):
        return self.agents[0].get_transaction_count()

    def init_portfolio(self, start_cash):
        for agent in self.agents:
            agent.init_portfolio( start_cash )

    def transfer_cash(self, amount, bank_to_security = True):
        for agent in self.agents:
            agent.transfer_cash(amount, bank_to_security)

    def order(self, symbol, count, price = None, comment = ''):
        for agent in self.agents:
            agent.order(symbol, count, price, comment)

    def order_target(self, symbol, target_count, price = None, comment = ''):
        for agent in self.agents:
            agent.order_target(symbol, target_count, price, comment)

    def order_value(self, symbol, value, price = None, comment = ''):
        for agent in self.agents:
            agent.order_value(symbol, value, price, comment)

    def order_target_value(self, symbol, target_value, price = None, comment = ''):
        for agent in self.agents:
            agent.order_target_value(symbol, target_value, price, comment)
