from .Env import Env
from .object import OrderStatus, TIME

from enum import Enum
import datetime

    
class UserOrder(object):
    _order_id = 0
    @classmethod
    def cls_get_state(cls):
        return {'order_id': cls._order_id}
    
    @classmethod
    def cls_set_state(cls, state):
        cls._order_id = state['order_id']

    def __init__(self, security, add_time, amount=None, value=None):

        self._status = OrderStatus.new
        self.add_time = add_time
        self.amount = None
        self.value = None
        if amount is not None:
            if amount > 0:
                self._is_buy = True
            else:
                self._is_buy = False
            self.amount = abs(amount)
        elif value is not None:
            if value > 0:
                self._is_buy = True
            else:
                self._is_buy = False
            self.value = abs(value)
        else:
            raise ValueError(f"{security} order: amount or value must be provided")

        self.value = value
        self.filled = None
        self.security = security
        self.order_id = UserOrder._order_id
        UserOrder._order_id += 1
        self._price = None
        self.avg_cost = None
        self.side = None
        self.action = None
        self.commission = None

    @property
    def price(self):
        # 访问 self.price 时会自动调用这个函数
        if self._price is None:
            env = Env()
            dtime = env.current_dt
            if TIME.OPEN.value <= dtime.time() < TIME.BEFORE_CLOSE.value:
                field = 'open'
            else:
                field = 'close'

            if TIME.DAY_START.value <= dtime.time() < TIME.OPEN.value:
                dtime += datetime.timedelta(days=-1, hours=0, minutes=0)

            if self.security in env.data:
                self._price =  env.data[self.security][dtime, field][0]
            elif self.security in env.cb_data:
                self._price =  env.cb_data[self.security][dtime, field][0]
            else:
                raise KeyError(f" {self.security} 不在回测数据中")
        return self._price

    def is_buy(self):
        return self._is_buy
    
    def status(self):
        return self._status
    
    def reject(self):
        self._status = OrderStatus.rejected

    def open(self):
        self._status = OrderStatus.open

    def held(self):
        self._status = OrderStatus.held
        self.price

    def expired(self):
        self._status = OrderStatus.expired

    def __repr__(self):
        return f"UserOrder(order_id={self.order_id}, security={self.security}, price={self.price}, amount={self.amount}, buy={self._is_buy}, status={self._status}, filled={self.filled}, add_time={self.add_time}, avg_cost={self.avg_cost}, commission={self.commission})"
    
    def get_state(self):
        return {
            'order_id': self.order_id,
            'security': self.security,
            '_price': self._price,
            'amount': self.amount,
            'value': self.value,
            '_is_buy': self._is_buy,
            '_status': str(self._status),
            'filled': self.filled,
            'add_time': self.add_time.strftime('%Y-%m-%d %H:%M:%S'),
            'avg_cost': self.avg_cost,
            'commission': self.commission,
            'action': self.action,
            'side': self.side
        }
    
    def set_state(self, state):
        state['add_time'] = datetime.datetime.strptime(state['add_time'], '%Y-%m-%d %H:%M:%S')
        state['_status'] = OrderStatus[state['_status']]
        self.__dict__.update(state)

class ConvertRequest(object):
    _request_id = 0
    @classmethod
    def cls_get_state(cls):
        return {'request_id': cls._request_id}
    
    @classmethod
    def cls_set_state(cls, state):
        cls._request_id = state['request_id']

    def __init__(self, security, add_time, amount=None, value=None):

        self._status = OrderStatus.new
        self.add_time = add_time
        self.amount = None
        self.value = None
        if amount is not None:
            if amount > 0:
                self._is_buy = True
            else:
                self._is_buy = False
            self.amount = abs(amount)
        elif value is not None:
            if value > 0:
                self._is_buy = True
            else:
                self._is_buy = False
            self.value = abs(value)
        else:
            raise ValueError(f"{security} order: amount or value must be provided")

        self.value = value
        self.filled = None
        self.security = security
        self.request_id = ConvertRequest._request_id
        ConvertRequest._request_id += 1
        self._price = None
        self.avg_cost = None
        self.side = None
        self.action = None
        self.commission = None

    @property
    def price(self):
        # 访问 self.price 时会自动调用这个函数
        if self._price is None:
            env = Env()
            dtime = env.current_dt
            if TIME.OPEN.value <= dtime.time() < TIME.BEFORE_CLOSE.value:
                field = 'open'
            else:
                field = 'close'

            if TIME.DAY_START.value <= dtime.time() < TIME.OPEN.value:
                dtime += datetime.timedelta(days=-1, hours=0, minutes=0)

            if self.security in env.data:
                self._price =  env.data[self.security][dtime, field][0]
            elif self.security in env.cb_data:
                self._price =  env.cb_data[self.security][dtime, field][0]
            else:
                raise KeyError(f" {self.security} 不在回测数据中")
        return self._price

    
    def status(self):
        return self._status
    
    def reject(self):
        self._status = OrderStatus.rejected

    def open(self):
        self._status = OrderStatus.open

    def held(self):
        self._status = OrderStatus.held
        self.price

    def expired(self):
        self._status = OrderStatus.expired

    def __repr__(self):
        return f"UserOrder(order_id={self.order_id}, security={self.security}, price={self.price}, amount={self.amount}, buy={self._is_buy}, status={self._status}, filled={self.filled}, add_time={self.add_time}, avg_cost={self.avg_cost}, commission={self.commission})"
    
    def get_state(self):
        return {
            'order_id': self.order_id,
            'security': self.security,
            '_price': self._price,
            'amount': self.amount,
            'value': self.value,
            '_is_buy': self._is_buy,
            '_status': str(self._status),
            'filled': self.filled,
            'add_time': self.add_time.strftime('%Y-%m-%d %H:%M:%S'),
            'avg_cost': self.avg_cost,
            'commission': self.commission,
            'action': self.action,
            'side': self.side
        }
    
    def set_state(self, state):
        state['add_time'] = datetime.datetime.strptime(state['add_time'], '%Y-%m-%d %H:%M:%S')
        state['_status'] = OrderStatus[state['_status']]
        self.__dict__.update(state)
