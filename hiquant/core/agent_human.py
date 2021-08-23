# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import pandas as pd

from ..utils import get_file_modify_time, str_now
from .agent_simulated import SimulatedAgent

class HumanAgent(SimulatedAgent):
    market = None
    conf = None

    push_service = None

    def set_verbose(self, verbose = True):
        super().set_verbose(verbose)
        if self.push_service is not None:
            self.push_service.set_verbose(verbose)

    def __init__(self, market, agent_conf = None):
        super().__init__(market, agent_conf)

        self.agent_type = 'human'

    def before_day(self):
        super().before_day()
        self.load_portoflio_from_file()
