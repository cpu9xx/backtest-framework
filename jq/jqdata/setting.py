from .Env import Env
import datetime
import numpy as np
class OrderCost(object):
    def __init__(self, open_tax=0, close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5):
        self.open_tax = open_tax
        self.close_tax = close_tax
        self.open_commission = open_commission
        self.close_commission = close_commission
        self.min_commission = min_commission

    def __str__(self):
        return (f"OrderCost(open_tax={self.open_tax}, "
            f"close_tax={self.close_tax}, "
            f"open_commission={self.open_commission}, "
            f"close_commission={self.close_commission}, "
            f"min_commission={self.min_commission})")


class Setting(object):
    def __init__(self):
        self._ucontext = None
        self._order_cost = dict()
        self._benchmark = None
        

    def get_order_cost(self, type: str, ref=None):
        return self._order_cost.get(type, None)

    def get_benchmark(self):
        return self._benchmark

    def set_user_context(self, ucontext):
        self._ucontext = ucontext

    def _set_benchmark(self, security: str):
        self._benchmark = security
        self._set_trade_dates(security)

    def _set_trade_dates(self, benchmark):
        env = Env()
        start = datetime.datetime.strptime(env.usercfg['start'], "%Y%m%d")
        end = datetime.datetime.strptime(env.usercfg['end'], "%Y%m%d")
        trade_dates = env.index_data[benchmark].loc[start:end, :].index
        env.set_trade_dates(trade_dates)
    
    def _set_order_cost(self, cost: OrderCost, type: str, ref=None):
        if type in ['stock']:
            self._order_cost[type] = cost
            return True
        return False
    
    def _set_option(self, option, value):
        pass

    def _set_universe(self, security_list):
        self._ucontext.universe = security_list

setting = Setting()