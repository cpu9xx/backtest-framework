# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from functools import lru_cache

from .Env import Env
from .events import Event, EVENT
from .logger import log
from .setting import setting, OrderCost
from .data import Data
_scheduler = None # main.py中的scheduler
_data = None
_strategy = None
_broker = None
_strategy = None
# setting = Setting()



##################################### time ################################
def run_daily(func, time, reference_security='000300.XSHG'):
    _scheduler._run_daily(func, time, reference_security)

##################################### time ################################




##################################### data ################################
# 返回行数与count强相关，不检查时期，退市股票仍能取到数据，设置 df=False 时性能强，推荐优先使用
def get_bars(security, count, unit='1d', fields=['close'], include_now=False, end_dt=None, fq_ref_date=None, df=False):
    return _data._get_bars(security, count, unit, fields, include_now, end_dt, fq_ref_date, df)

def get_cb_price(security, start_date=None, end_date=None, frequency='daily', fields=None, skip_paused=False, fq='post', count=None, panel=False, fill_paused=True, df=True):
    return _data._get_cb_price(security, start_date, end_date, frequency, fields, skip_paused, fq, count, panel, fill_paused, df)

# 取不到退市数据，包含end_date当天数据
def get_price(security, start_date=None, end_date=None, frequency='daily', fields=None, skip_paused=False, fq='post', count=None, panel=False, fill_paused=True, df=True):
    return _data._get_price(security, start_date, end_date, frequency, fields, skip_paused, fq, count, panel, fill_paused, df)

def get_all_securities(types=['stock']):
    return _data._get_all_securities(types)

def get_all_trade_days():
    return _data._get_all_trade_days()

def get_hm_detail(date):
    return _data._get_hm_detail(date)

@lru_cache(maxsize=8192)
def trans_name(name):
    if name.lower().endswith('sz') or name.lower().endswith('SZ'):
        return name[:-2] + 'XSHE'
    elif name.lower().endswith('sh') or name.lower().endswith('SH'):
        return name[:-2] + 'XSHG'
    return name

# 取不到退市数据，不包含当日数据,即使是在收盘后
def history(count, unit='1d', field='avg', security_list=None, df=True, skip_paused=False, fq='pre'):
    return _data._history(count, unit, field, security_list, df, skip_paused, fq)

def filter_kcbj_stock(stock_list):
    return _data._filter_kcbj_stock(stock_list)

def b_filter(stock_list):
    return _data._b_filter(stock_list)

def bj_filter(stock_list):
    return _data._bj_filter(stock_list)

def kc_filter(stock_list):
    return _data._kc_filter(stock_list)

def cy_filter(stock_list):
    return _data._cy_filter(stock_list)
##################################### data ################################






##################################### strategy ################################
def order(security, amount, style=None, side='long', pindex=0, close_today=False):
    return _strategy._order(security, amount)

def order_target(security, target, style=None, side='long', pindex=0, close_today=False):
    return _strategy._order_target(security, target)

def order_value(security, value, style=None, side='long', pindex=0, close_today=False):    
    return _strategy._order_value(security, value)

def order_target_value(security, value, style=None, side='long', pindex=0, close_today=False):    
    return _strategy._order_target_value(security, value)
##################################### strategy ################################



##################################### broker ################################
def get_trades():
    return _broker._get_trades()
##################################### broker ################################





##################################### setting ################################
def set_order_cost(cost, type: str, ref=None):
    setting._set_order_cost(cost, type, ref)

def set_benchmark(security):
    setting._set_benchmark(security)

def set_option(option: str, value):
    setting._set_option(option, value)
##################################### setting ################################
    



