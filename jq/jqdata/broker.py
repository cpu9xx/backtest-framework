from .events import EVENT, Event
from .Env import Env
from .logger import log
from .api import setting
from .order import UserOrder, OrderStatus
from .scheduler import TIME
from collections import defaultdict
import datetime

from .object import TIME
# class Executor(object):
#     def __init__(self, env):
#         self._env = env

#     KNOWN_EVENTS = {
#         EVENT.TICK,
#         EVENT.BAR,
#         EVENT.BEFORE_TRADING,
#         EVENT.AFTER_TRADING,
#         EVENT.POST_SETTLEMENT,
#     }

#     def run(self, bar_dict):

#         start = self._env.usercfg['start']
#         end = self._env.usercfg['end']
#         frequency = self._env.config.base.frequency
#         event_bus = self._env.event_bus

#         for event in self._env.event_source.events(start, end, frequency):
#             if event.event_type in self.KNOWN_EVENTS:
#                 self._env.calendar_dt = event.calendar_dt
#                 #self._env.trading_dt = event.trading_dt

#                 event_bus.publish_event(event)
class UserTrade(object):
    _trade_id = 0
    def __init__(self, order, time):
        self.time = time
        self.order = order
        self.trade_id = UserTrade._trade_id
        UserTrade._trade_id += 1

    @classmethod
    def get_current_id(cls):
        return cls._trade_id
    
    @classmethod
    def cls_get_state(cls):
        return {'trade_id': cls._trade_id}
    
    @classmethod
    def cls_set_state(cls, state):
        cls._trade_id = state['trade_id']

    def __repr__(self):
        return f"UserTrade(trder_id={self.trade_id}, order_id={self.order.order_id}, time={self.time}, price={self.order.price}, amount={self.order.amount}, commission={self.order.commission})"


class Broker(object):
    # _broker = None
    def __init__(self):
        # Broker._broker = self
        self._ucontext = None
        self._env = Env()
        self._order_recieved = defaultdict(list)
        self._overnight_orders = list()
        self._trades = defaultdict(dict)
        self._closed_positions = list()
        # self.start = datetime.datetime.strptime(env.usercfg['start'], "%Y-%m-%d")
        # self.end = datetime.datetime.strptime(env.usercfg['end'], "%Y-%m-%d")
        event_bus = self._env.event_bus
        event_bus.add_listener(EVENT.MARKET_OPEN, self._before_trading)
        # event_bus.add_listener(EVENT.MARKET_OPEN, self._trading)
        # event_bus.add_listener(EVENT.MARKET_OPEN, self._after_trading)

        event_bus.add_listener(EVENT.STOCK_ORDER, self._before_trading)
        event_bus.add_listener(EVENT.TRADE, self._trading)
        event_bus.add_listener(EVENT.TRADE, self._after_trading)

        event_bus.add_listener(EVENT.MARKET_CLOSE, self._market_close)
        event_bus.add_listener(EVENT.DAY_END, self._close_pos)
        # event_bus.add_listener(EVENT.GET_TRADES, self._get_trades)

    def set_state(self, state):
        overnight_orders = state['overnight_orders']
        order_ls = []
        for _, order_state in overnight_orders.items():
            order = UserOrder(security=order_state['security'], add_time=order_state['add_time'], amount=order_state['amount'], value=order_state['value'])
            order.set_state(order_state)
            order_ls.append(order)
        self._overnight_orders = order_ls

    def get_state(self):
        overnight_orders = {order.order_id: order.get_state() for order in self._overnight_orders}
        return {
            'overnight_orders': overnight_orders,
        }

    def set_user_context(self, ucontext):
        self._ucontext = ucontext
    # @classmethod
    # def get_instance(cls):
    #     """
    #     返回已经创建的 broker 对象
    #     """
    #     if Broker._broker is None:
    #         raise RuntimeError("Broker还未初始化")
    #     return Broker._broker    

    #check order
    def _before_trading(self, event):
        if 'order' in event.__dict__:
            order = event.__dict__['order']
            order_time = order.add_time
            time = order_time.time()
            # 隔夜单
            if TIME.CLOSE.value < time <= TIME.DAY_END.value:
                self._overnight_orders.append(order)
                # order_time = order_time + datetime.timedelta(days=1)
            else:
                self._order_recieved[order_time.date()].append(order)

        if TIME.OPEN.value <= self._env.current_dt.time() < TIME.CLOSE.value:
            if len(self._overnight_orders) > 0:
                self._order_recieved[self._env.current_dt.date()].extend(self._overnight_orders)
                self._overnight_orders.clear()

            event_bus = self._env.event_bus
            for order in self._order_recieved[self._env.current_dt.date()]:
                if order.status() == OrderStatus.new:
                    if order.is_buy():
                        log.orderinfo(f"订单已委托：{order}")
                        order.open()
                        event_bus.publish_event(Event(EVENT.TRADE, order=order))
                        # total_price = order.price * order.amount
                        # if total_price < self.portfolio.available_cash:
                        #     order.open()
                        # else:
                        #     order.reject()
                        #     log.warning(f"可用资金不足：{order.security}")
                        #     return True
                    else:
                        if order.security in self._ucontext.portfolio.positions and self._ucontext.portfolio.positions[order.security].closeable_amount >= order.amount:
                            self._ucontext.portfolio.positions[order.security].closeable_amount -= order.amount
                            order.open()
                            log.orderinfo(f"订单已委托：{order}")
                            event_bus.publish_event(Event(EVENT.TRADE, order=order))
                        else:
                            order.reject()
                            log.warning(f"可卖出股数不足：{order.security}")
                            return True
                        
        return False

    def _trading(self, event):
        order = event.__dict__['order']
        # ordertime = order.add_time

        if order.security in self._env.data:
            data = self._env.data[order.security]
        elif order.security in self._env.cb_data:
            data = self._env.cb_data[order.security]
        else:
            log.error(f" {order.security} 不在回测数据中")
        current_data = data[self._ucontext.current_dt, ['date', 'high', 'low']][0]
        if isinstance(current_data, int) and current_data == 0:
            order.reject()
            log.warning(f"已退市无法成交：{order}")
            return True
        elif current_data['date'].astype('datetime64[D]') != self._ucontext.current_dt.date():
            order.reject()
            log.warning(f"停牌无法成交：{order.security}, 数据时间：{current_data['date']}")
            return True
        elif current_data['high'] == current_data['low']:
            prev_data = data[self._ucontext.previous_date, ['close']][0]
            if order.is_buy() and prev_data['close'] < current_data['high']:
                order.reject()
                log.warning(f"涨停一字板无法买入：{order.security}")
                return True
            elif not order.is_buy() and prev_data['close'] > current_data['high']:
                order.reject()
                log.warning(f"跌停一字板无法卖出：{order.security}")
                return True
            else:
                log.warning(f"当日一字板, 注意风险：{order.security}")

        if order.amount is None:
            total_price = order.value
            order.amount = order.value / order.price
        else:
            total_price = order.price * order.amount
        order_cost = setting.get_order_cost(type='stock')

        if order.is_buy():
            commission = (order_cost.open_tax + order_cost.open_commission) * total_price
            order.commission = commission if commission > order_cost.min_commission else order_cost.min_commission
            total_cost = total_price + order.commission
            if total_cost <= self._ucontext.portfolio.available_cash:
                # avg_cost 买入时表示此次买入的均价
                order.avg_cost = total_cost/order.amount
                
                self._ucontext.portfolio.available_cash -= total_cost
                self._ucontext.portfolio.positions.create_key(order.security)
                self._ucontext.portfolio.positions[order.security].init_position(order.security, total_cost/order.amount, self._ucontext.current_dt, order.amount)
                order.held()
            else:
                log.warning(f"可用资金不足：{order}, 需要：{total_cost}, 现有：{self._ucontext.portfolio.available_cash}")
                order.reject()
                return True
        else:
            commission = (order_cost.close_tax + order_cost.close_commission) * total_price
            order.commission = commission if commission > order_cost.min_commission else order_cost.min_commission
            if total_price > order.commission:
                # avg_cost 卖出时表示下卖单前的此股票的持仓成本, 用来计算此次卖出的收益
                order.avg_cost =  self._ucontext.portfolio.positions[order.security].avg_cost

                total_gain = total_price - order.commission
                self._ucontext.portfolio.available_cash += total_gain
                self._ucontext.portfolio.positions[order.security].close_position(order.amount, self._env.current_dt)

                order.held()
            else:
                log.warning(f"本次成交收益小于手续费：{order}")
                order.held()
        
        return False
        
    def _after_trading(self, event):
        order = event.__dict__['order']
        if order.status() == OrderStatus.held:
            trade = UserTrade(order, self._env.current_dt)
            self._trades[self._env.current_dt.date()][trade.trade_id] = trade
            log.orderinfo(f"订单完成：{order}")
            if not order.is_buy():
                Env().event_bus.publish_event(Event(EVENT.RECORD_TRADE, trade=trade))
        return True

    def _get_trades(self):
        return self._trades[self._env.current_dt.date()]

    def _market_close(self, event):
        for order in self._order_recieved[self._env.current_dt.date()]:
            if order.status() == OrderStatus.open:
                log.warning(f"订单未完成, 过期：{order}")
                order.expired()
        # T+1, orders expired
        for security in list(self._ucontext.portfolio.positions.keys()):
            self._ucontext.portfolio.positions[security].update_closeable_amount()
            if self._ucontext.portfolio.positions[security].total_amount <= 0:
                self._closed_positions.append(security)
        return False

    def _close_pos(self, event):
        for security in self._closed_positions:
            self._ucontext.portfolio.positions.remove_key(security)
        self._closed_positions.clear()
        return False
