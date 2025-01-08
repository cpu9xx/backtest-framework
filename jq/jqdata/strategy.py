from .events import Event, EVENT
from .order import UserOrder
from .Env import Env
from .logger import log
from .api import setting
from .object import OrderStatus, TIME
from userConfig import userconfig

import datetime

class Strategy(object):
    def __init__(self):
        self._ucontext = None
        
    def set_user_context(self, ucontext):
        self._ucontext = ucontext

    def _order(self, security, amount, style=None, side='long', pindex=0, close_today=False):
        env = Env()
        if userconfig['backtest']:
            if security in env.data:
                flag = env.data[security][self._ucontext.current_dt, 'close'][0]
            elif security in env.cb_data:
                flag = env.cb_data[security][self._ucontext.current_dt, 'close'][0]
            else:
                log.error(f" {security} 不在回测数据中")
            if flag == 0:
                log.warning(f" {security} 进入退市整理期或已退市, 取消下单")
                return None
        event_bus = env.event_bus
        order = UserOrder(security, add_time=self._ucontext.current_dt, amount=amount)
        event_bus.publish_event(Event(EVENT.STOCK_ORDER, order=order))
        if order.status() != OrderStatus.rejected:
            return order
        else:
            return None

    def _order_target(self, security, amount, style=None, side='long', pindex=0, close_today=False):
        current_amount = self._ucontext.portfolio.positions[security].total_amount
        amount = amount - current_amount
        return self._order(security, amount, style, side, pindex, close_today)

    def _order_value(self, security, value, style=None, side='long', pindex=0, close_today=False):
        order_cost = setting.get_order_cost(type='stock')
        #买入时需要预留手续费
        if value > 0:
            commission= (order_cost.open_tax + order_cost.open_commission) * value
            commission = commission if commission > order_cost.min_commission else order_cost.min_commission
            value -= commission
            if value <= 0:
                log.warning(f" {security} 下单金额少于成交所需手续费, 取消下单")
                return None
        
        # env = Env()
        # dtime = env.current_dt
        # if TIME.OPEN.value < dtime.time() <= TIME.CLOSE.value:
        #     # 日频数据, 开盘后的下一个价格是收盘价
        #     field = 'close'
        # else:
        #     # 夜间下单, 按开盘价成交
        #     field = 'open'

        # if TIME.CLOSE.value < dtime.time() < TIME.DAY_END.value:
        #     # 按下一个交易日开盘价成交
        #     dtime += datetime.timedelta(days=1, hours=0, minutes=0)

        # current_price = env.data[security][dtime, field][0]
        # if current_price == 0:
        #     log.warning(f" {security} 进入退市整理期或已退市, 取消下单")
        #     return None
        # # current_price = self._ucontext.portfolio.positions[security].price
        # amount = value / current_price
        env = Env()
        if userconfig['backtest']:
            if security in env.data:
                flag = env.data[security][self._ucontext.current_dt, 'close'][0]
            elif security in env.cb_data:
                flag = env.cb_data[security][self._ucontext.current_dt, 'close'][0]
            else:
                log.error(f" {security} 不在回测数据中")
            if flag == 0:
                log.warning(f" {security} 进入退市整理期或已退市, 取消下单")
                return None
        event_bus = env.event_bus
        order = UserOrder(security, add_time=self._ucontext.current_dt, value=value)
        event_bus.publish_event(Event(EVENT.STOCK_ORDER, order=order))
        if order.status() != OrderStatus.rejected:
            return order
        else:
            return None

    def _order_target_value(self, security, value, style=None, side='long', pindex=0, close_today=False):
        value -= self._ucontext.portfolio.positions[security].value
        return self._order_value(security, value, style, side, pindex, close_today)
    
    def _convert_bond(self, security, amount, price, style=None, side='long', pindex=0, close_today=False):
        pass