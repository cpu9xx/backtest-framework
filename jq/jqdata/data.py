from .Env import Env
from .logger import log
from .setting import setting
# from userConfig import stock_column_tuple
from .object import TIME

import pandas as pd
import numpy as np
# from pathos.multiprocessing import ProcessingPool as Pool
# from multiprocessing import Pool
from functools import partial, lru_cache
import datetime

@lru_cache(maxsize=8)
def get_dtype(fields):
    dtype = []
    stock_column_tuple = Env().stock_column_tuple
    for f in fields:
        for item in stock_column_tuple:
            if item[0] == f:
                dtype.append((item[0], item[1]))
                break
    return dtype


def multi_get_price_by_index(security, data, fields, reshape, newindex):
    # env = Env()
    # print(security, data)
    stock_column_tuple = Env().stock_column_tuple
    res, _ = data[newindex[0]:newindex[-1], fields]
    trade_dates, _ = data[newindex[0]:newindex[-1], 'date']

    # 如果数据不全
    if len(res) != len(newindex):
        # 为nanarray指定dtype
        if isinstance(fields, str):
            nanarray = np.full(len(newindex), np.nan)
        else:
            dtype = []
            for f in fields:
                for item in stock_column_tuple:
                    if item[0] == f:
                        dtype.append((item[0], item[1]))
                        break

            nanarray = np.full(len(newindex), np.nan, dtype=dtype)

        # 补全数据
        if len(res) == 0:
            res = nanarray
        elif len(res) < len(newindex):
            trade_dates_i = 0
            for i, expected_date in enumerate(newindex):
                if trade_dates_i >= len(trade_dates):
                    break
                elif expected_date == trade_dates[trade_dates_i]:
                    nanarray[i] = res[trade_dates_i]
                    trade_dates_i += 1
            res = nanarray      
        elif len(res) > len(newindex):
            raise ValueError('res length is greater than newindex length')
    
    if reshape is not None:    
        return res.reshape(reshape)
    return res

def get_cb_price_by_index(security, fields, reshape, newindex, data):
    # env = Env()
    res, _ = data[security][newindex[0]:newindex[-1], fields]
    trade_dates, _ = data[security][newindex[0]:newindex[-1], 'date']
    # 如果数据不全
    if len(res) != len(newindex):
        # 为nanarray指定dtype
        if isinstance(fields, str):
            nanarray = np.full(len(newindex), np.nan)
        else:
            dtype = []
            for f in fields:
                for item in Env().cb_column_tuple:
                    if item[0] == f:
                        dtype.append((item[0], item[1]))
                        break

            nanarray = np.full(len(newindex), np.nan, dtype=dtype)

        # 补全数据
        if len(res) == 0:
            res = nanarray
        elif len(res) < len(newindex):
            trade_dates_i = 0
            for i, expected_date in enumerate(newindex):
                if trade_dates_i >= len(trade_dates):
                    break
                elif expected_date == trade_dates[trade_dates_i]:
                    nanarray[i] = res[trade_dates_i]
                    trade_dates_i += 1
            res = nanarray      
        elif len(res) > len(newindex):
            raise ValueError('res length is greater than newindex length')
    
    if reshape is not None:    
        return res.reshape(reshape)
    return res

def get_price_by_index(security, fields, reshape, newindex, data):
    # env = Env()
    # print(security, data)
    res, _ = data[security][newindex[0]:newindex[-1], fields]
    trade_dates, _ = data[security][newindex[0]:newindex[-1], 'date']
    # 如果数据不全
    if len(res) != len(newindex):
        # 为nanarray指定dtype
        if isinstance(fields, str):
            nanarray = np.full(len(newindex), np.nan)
        else:
            dtype = []
            for f in fields:
                for item in Env().stock_column_tuple:
                    if item[0] == f:
                        dtype.append((item[0], item[1]))
                        break

            nanarray = np.full(len(newindex), np.nan, dtype=dtype)

        # 补全数据
        if len(res) == 0:
            res = nanarray
        elif len(res) < len(newindex):
            trade_dates_i = 0
            for i, expected_date in enumerate(newindex):
                if trade_dates_i >= len(trade_dates):
                    break
                elif expected_date == trade_dates[trade_dates_i]:
                    nanarray[i] = res[trade_dates_i]
                    trade_dates_i += 1
            res = nanarray      
        elif len(res) > len(newindex):
            raise ValueError('res length is greater than newindex length')
    
    if reshape is not None:    
        return res.reshape(reshape)
    return res
    # print(trade_dates)
    # print('###')
    # print(res)
    # print(security)
    # if isinstance(fields, str):
    #     fields = [fields]
    # if df:
    #     if len(res) == 0:
    #         res = pd.DataFrame(index=newindex, columns=fields)
    #     else:
    #         res = pd.DataFrame(data=res, index=trade_dates, columns=fields)

    #     if len(res) != len(newindex):
    #         res = res.reindex(newindex)


        
def get_bar_by_count(security, end_dt, fields, count, df):
    env = Env()
    if df:
        return pd.DataFrame(data=env.data[security][:end_dt, fields][0][-count:], columns=fields)
    else:
        return env.data[security][:end_dt, fields][0][-count:]#.to_records(index=False)


class Data(object):
    def __init__(self):
        self._ucontext = None
        # self.pool = Pool(processes=25)
        
    def set_user_context(self, ucontext):
        self._ucontext = ucontext

    def _get_hm_detail(self, date):
        env = Env()
        if isinstance(date, datetime.datetime) or isinstance(date, datetime.date):
            date = date.strftime('%Y%m%d')
        else:
            raise ValueError('date should be datetime.datetime or datetime.date')
        # log.test(date)
        df = env.hm_detail.get(date, None)
        return df

    def _get_cb_price(self, security, start_date=None, end_date=None, frequency='daily', fields=None, skip_paused=False, fq='post', count=None, panel=False, fill_paused=True, df=True):
        Env().need_cb_daily()
        if isinstance(fields, str):
            fields = [fields]

        for f in fields:
            if f not in Env().cb_columns:
                log.error(f'field should be one of {Env().cb_columns}')

        if skip_paused or not fill_paused:
            log.warning('skip_paused = True and fill_paused = False are not supported in this version, missing data will be filled with NaN')

        env = Env()
        # end_dt = pd.Timestamp(env.current_dt.date())#pd.Timestamp(self._ucontext.previous_date)
        benchmark = setting.get_benchmark()
        benchmark_index = env.index_data[benchmark].index

        end_date = pd.Timestamp(end_date) if end_date is not None else pd.Timestamp(env.current_dt.date())
        if start_date and count:
            log.error('start_date and count cannot be set at the same time')
        elif start_date:
            start_date = pd.Timestamp(start_date)
            if start_date.time() != TIME.DAY_START:
                log.warning("Time accuracy current version supported in start_date of get_cb_price() is only to the day, time will be ignored")
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            last_index = benchmark_index.get_loc(end_date)+1
            first_index = benchmark_index.get_loc(start_date)
            newindex = benchmark_index[first_index:last_index]
        elif count:
            # log.test(benchmark_index)
            last_index = benchmark_index.get_loc(end_date)+1
            # log.test(end_date)
            # log.test(last_index)
            if count > 0:
                newindex = benchmark_index[last_index-count:last_index]
                # log.test(newindex)
            else:
                # log.warning(f"get_price() 使用了 {last_index}({end_date}+1) - {last_index-count} 的未来数据")
                newindex = benchmark_index[last_index:last_index-count]
        else:
            log.error('start_date or count should be set')
        # log.test(end_date, benchmark_index[last_index])
        if isinstance(security, str):
            res = get_cb_price_by_index(security=security, fields=fields, reshape=None, newindex=newindex, data=env.cb_data)
            if df:
                res = pd.DataFrame(res, index=newindex, columns=fields)
            else:
                return res
            
        else:
            if df:
                res_ls = [None] * len(security)
            else:
                res = {}
            # log.live('getprice 1')
            for idx, s in enumerate(security):
                resarray = get_cb_price_by_index(security=s, fields=fields, reshape=None, newindex=newindex, data=env.cb_data)
                if df:
                    res_ls[idx] = resarray
                else:
                    res[s] = resarray    

            
            # log.live('getprice 2')

            if df:
                res = np.concatenate(res_ls, axis=0)
                res = pd.DataFrame(res, columns=fields)#.rename(columns={'date': 'time'})
                res.insert(0, 'time', np.tile(newindex, len(security)))
                name_ls = []
                for s in security:
                    name_ls += [s] * len(newindex)
                res.insert(1, 'code', name_ls)
                # log.live('getprice 3')

        return res

    def _get_price(self, security, start_date=None, end_date=None, frequency='daily', fields=None, skip_paused=False, fq='post', count=None, panel=False, fill_paused=True, df=True):
        if isinstance(fields, str):
            fields = [fields]

        stock_columns = Env().stock_columns
        for f in fields:
            if f not in stock_columns:
                log.error(f'field should be one of {stock_columns}')

        if skip_paused or not fill_paused:
            log.warning('skip_paused = True and fill_paused = False are not supported in this version, missing data will be filled with NaN')

        env = Env()
        # end_dt = pd.Timestamp(env.current_dt.date())#pd.Timestamp(self._ucontext.previous_date)
        benchmark = setting.get_benchmark()
        benchmark_index = env.index_data[benchmark].index

        end_date = pd.Timestamp(end_date) if end_date is not None else pd.Timestamp(env.current_dt.date())
        if start_date and count:
            log.error('start_date and count cannot be set at the same time')
        elif start_date:
            start_date = pd.Timestamp(start_date)
            if start_date.time() != TIME.DAY_START:
                log.warning("Time accuracy current version supported in start_date of get_price() is only to the day, time will be ignored")
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            last_index = benchmark_index.get_loc(end_date)+1
            first_index = benchmark_index.get_loc(start_date)
            newindex = benchmark_index[first_index:last_index]
        elif count:
            # log.test(benchmark_index)
            last_index = benchmark_index.get_loc(end_date)+1
            # log.test(end_date)
            # log.test(last_index)
            if count > 0:
                newindex = benchmark_index[last_index-count:last_index]
                # log.test(newindex)
            else:
                # log.warning(f"get_price() 使用了 {last_index}({end_date}+1) - {last_index-count} 的未来数据")
                newindex = benchmark_index[last_index:last_index-count]
        else:
            log.error('start_date or count should be set')
        # log.test(end_date, benchmark_index[last_index])
        if isinstance(security, str):
            res = get_price_by_index(security=security, fields=fields, reshape=None, newindex=newindex, data=env.data)
            if df:
                res = pd.DataFrame(res, index=newindex, columns=fields)
            else:
                return res
            
        else:
            if df:
                res_ls = [None] * len(security)
            else:
                res = {}
            # log.live('getprice 1')
            for idx, s in enumerate(security):
                resarray = get_price_by_index(security=s, fields=fields, reshape=None, newindex=newindex, data=env.data)
                if df:
                    res_ls[idx] = resarray
                else:
                    res[s] = resarray    

            
            # log.live('getprice 2')

            if df:
                res = np.concatenate(res_ls, axis=0)
                res = pd.DataFrame(res, columns=fields)#.rename(columns={'date': 'time'})
                res.insert(0, 'time', np.tile(newindex, len(security)))
                name_ls = []
                for s in security:
                    name_ls += [s] * len(newindex)
                res.insert(1, 'code', name_ls)
                # log.live('getprice 3')

        return res

    def _history(self, count, unit='1d', field='avg', security_list=None, df=True, skip_paused=False, fq='pre'):
        # ['open', 'close', 'high', 'low', 'volume', 'money', 'avg', 'high_limit', 'low_limit', 'pre_close', 'paused', 'factor', 'open_interest']
        if not isinstance(field, str) or field not in Env().stock_columns:
            log.error(f'field should be one of {Env().stock_columns}')

        env = Env()
        end_dt = pd.Timestamp(env.current_dt.date())#pd.Timestamp(self._ucontext.previous_date)
        benchmark = setting.get_benchmark()
        benchmark_index = env.index_data[benchmark].index

        last_index = benchmark_index.get_loc(end_dt)
        newindex = benchmark_index[last_index-count:last_index]
        if isinstance(security_list, str):
            security_list = [security_list]
        if df:
            res_ls = [None] * len(security_list)
            # log.live(1)
            # pool = Pool(processes=20)
            # multi_get_price= partial(multi_get_price_by_index, fields=field, reshape=(len(newindex), 1), newindex=newindex)
            # res_ls = self.pool.map(multi_get_price, security_list, list(map(env.data.get, security_list)))

            # pool.close()
            for idx, s in enumerate(security_list):
                resarray = get_price_by_index(security=s, fields=field, reshape=(len(newindex), 1), newindex=newindex, data=env.data)
                res_ls[idx] = resarray    
            # log.live(2)
            res = np.concatenate(res_ls, axis=1)
            res = pd.DataFrame(res, index=newindex, columns=security_list)
            # print(res)
            # log.live(3)
            pass
        else:
            res = {}
            # log.live(1)
            for s in security_list:
                res[s] = get_price_by_index(security=s, fields=field, reshape=None, newindex=newindex, data=env.data)
            # log.live(2)
        return res

    def _get_bars(self, security, count, unit='1d', fields=['close'], include_now=False, end_dt=None, fq_ref_date=None, df=False):
        end_dt = pd.to_datetime(end_dt) if end_dt else pd.to_datetime(self._ucontext.current_dt)

        if not include_now:
            end_dt -= pd.Timedelta(days=1)

        # 处理数据
        if isinstance(security, str):
            res = get_bar_by_count(security, end_dt, fields, count, df)
        else:
            res = {s: get_bar_by_count(s, end_dt, fields, count, df) for s in security}

        return res
    
    
    def _get_all_securities(self, types):
        env = Env()
        index = []
        if 'stock' in types:
            index += list(env.data.keys())
        if 'index' in types:
            index += list(env.index_data.keys())    
        if 'cb' in types:
            Env().need_cb_daily()
            index += list(env.cb_data.keys())
        return pd.DataFrame(index=index)
    
    def _get_all_trade_days(self):
        env = Env()
        benchmark = setting.get_benchmark()
        return np.array(env.index_data[benchmark].index.date)

    def _filter_kcbj_stock(self, stock_list):
        for stock in stock_list[:]:
            if stock[0] == '4' or stock[0] == '8' or stock[0] == '9' or stock[:2] == '68':
                stock_list.remove(stock)
        return stock_list
    
    def _filter_kcbj_stock(self, stock_list):
        for stock in stock_list[:]:
            if stock[0] == '2' or stock[:2] == '90':
                stock_list.remove(stock)
        return stock_list
    
    def _b_filter(self, stock_list):
        for stock in stock_list[:]:
            if stock[0] == '2' or stock[:2] == '90':
                stock_list.remove(stock)
        return stock_list

    def _bj_filter(self, stock_list):
        for stock in stock_list[:]:
            if stock[0] == '4' or stock[0] == '8' or stock[:2] == '92':
                stock_list.remove(stock)
        return stock_list
    
    def _kc_filter(self, stock_list):
        for stock in stock_list[:]:
            if stock[:2] == '68':
                stock_list.remove(stock)
        return stock_list
    
    def _cy_filter(self, stock_list):
        for stock in stock_list[:]:
            if stock[0] == '3':
                stock_list.remove(stock)
        return stock_list