from .Env import Env
from .events import EVENT
from .api import setting
from .logger import log
from .broker import UserTrade

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import numpy as np

class Recorder(object):
    def __init__(self):
        self._ucontext = None
        self._env = Env()
        self._returns_ls =[]
        self._Dp_ls = []
        self._Dm_ls = []
        self._bm_returns_ls = []
        self._hold_ls = []
        self._dt_ls = []
        self._holding_days_ls = []
        self._bm_start_price = None

        self.gain_trades = []
        self.loss_trades = []
        # self._winning_count
        event_bus = self._env.event_bus
        event_bus.add_listener(EVENT.DAY_END, self._pnl)
        event_bus.add_listener(EVENT.FIRST_TICK, self._set_bm_start_price)
        event_bus.add_listener(EVENT.RECORD_TRADE, self._record_trade)

    def set_user_context(self, ucontext):
        self._ucontext = ucontext

    def set_state(self, state):
        import pandas as pd
        self._returns_ls = state['returns_ls']
        self._Dp_ls = state['Dp_ls']
        self._Dm_ls = state['Dm_ls']
        self._bm_returns_ls = state['bm_returns_ls']
        self._hold_ls = state['hold_ls']
        self._dt_ls = pd.to_datetime(state['dt_ls']).date.tolist()
        self._holding_days_ls = state['holding_days_ls']
        self._bm_start_price = state['bm_start_price']
        self.gain_trades = state['gain_trades']
        self.loss_trades = state['loss_trades']


    def get_state(self):
        return {
            'returns_ls': self._returns_ls,
            'Dp_ls': self._Dp_ls,
            'Dm_ls': self._Dm_ls,
            'bm_returns_ls': self._bm_returns_ls,
            'hold_ls': self._hold_ls,
            'dt_ls': [date.strftime('%Y%m%d') for date in self._dt_ls],
            'holding_days_ls': self._holding_days_ls,
            'bm_start_price': self._bm_start_price,
            'gain_trades': self.gain_trades,
            'loss_trades': self.loss_trades
        }


    def get_index_price(self, security):
        dtime = self._env.current_dt
        if datetime.time(9, 30) <= dtime.time() < datetime.time(15, 0):
            field = 'open'
        else:
            field = 'close'
            if datetime.time(0, 0) <= dtime.time() < datetime.time(9, 30):
                dtime += datetime.timedelta(days=-1, hours=0, minutes=0)
        return self._env.index_data[security].loc[dtime.date():dtime.date(), [field]].iloc[-1][field]

    def _set_bm_start_price(self, event):
        if self._ucontext.current_dt:
            self._bm_start_price = self.get_index_price(setting.get_benchmark())
        return False

    def _pnl(self, event):
        if self._bm_start_price:
            bm_price = self.get_index_price(setting.get_benchmark())
            bm_prev_return = self._bm_returns_ls[-1] if self._bm_returns_ls else 0
            bm_current_return = bm_price/self._bm_start_price - 1
            current_return = self._ucontext.portfolio.returns
            prev_return  = self._returns_ls[-1] if self._returns_ls else 0
            self._Dp_ls.append(current_return - prev_return)
            self._returns_ls.append(current_return)

            self._Dm_ls.append(bm_current_return - bm_prev_return)
            self._bm_returns_ls.append(bm_current_return)
            self._hold_ls.append(len(self._ucontext.portfolio.positions))
            self._dt_ls.append(self._ucontext.current_dt.date())
        return False

    def _record_trade(self, event):
        trade = event.__dict__.get('trade')
        order = trade.order
        dt = trade.time
        holding_days = (dt - self._ucontext.portfolio.positions[order.security].init_time).days
        self._holding_days_ls.append(holding_days)
        profit = 100*((order.price - order.avg_cost)/order.avg_cost)
        if profit > 0:
            self.gain_trades.append(profit)
        else:
            self.loss_trades.append(profit)
        return True
    
    # def plot(self):
    #     plt.figure(figsize=(10, 6))
    #     plt.plot(self._dt_ls, self._returns_ls, label="Returns", color="blue", linewidth=2)
    #     plt.plot(self._dt_ls, self._bm_returns_ls, label="Benchmark Returns", color="red", linewidth=2)  # 绘制曲线

    #     plt.fill_between(self._dt_ls, self._returns_ls, color="#B9CFE9", alpha=0.5)
        
    #     # 添加网格和标题
    #     plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    #     plt.title("PNL", fontsize=16)
    #     plt.xlabel("Date", fontsize=12)
    #     plt.ylabel("Returns (%)", fontsize=12)
        
    #     plt.gcf().autofmt_xdate()
    #     plt.legend()
    #     plt.show()  # 显示图形
    #     plt.savefig('pnl.png')  # 保存到文件中
    #     plt.close()
    def fft(self, data_ls):
        data_array = np.array(data_ls)

        # 对时序数据进行快速傅里叶变换 (FFT)
        fft_result = np.fft.fft(data_array)

        # 计算频率分量对应的频率轴
        frequencies = np.fft.fftfreq(len(data_array))
        fft_result[np.abs(frequencies) > 50] = 0
        # 只保留正半轴 (非负频率部分)
        positive_frequencies = frequencies[:len(frequencies)//2]
        positive_fft_result = np.abs(fft_result[:len(fft_result)//2])

        # 忽略频率为 0 的部分，计算周期（1/频率）
        positive_frequencies = positive_frequencies[1:]  # 去掉频率为0的部分
        positive_fft_result = positive_fft_result[1:]  # 去掉对应的FFT结果

        # 计算周期
        periods = 1 / positive_frequencies

        return periods, positive_fft_result

    def is_delay(self, array1, array2, delay):
        if len(array1) != len(array2):
            return None
        corr_list = []
        correlation_matrix = np.corrcoef(array1, array2)
        correlation_coefficient = correlation_matrix[0, 1]
        # print(f"0: {correlation_coefficient}")
        corr_list.append(correlation_coefficient)
        for i in range(1, delay-1):
            correlation_coefficient = np.corrcoef(array1[:-i], array2[i:])[0, 1]
            corr_list.append(correlation_coefficient)

        return corr_list
    
    def autocorrelation(self, data, max_lag):
        data = np.asarray(data)
        mean = np.mean(data)
        n = len(data)
        corr_list = []
        for lag in range(1, max_lag-1):
            numerator = np.sum((data[:n-lag] - mean) * (data[lag:] - mean))
            denominator = np.sum((data - mean) ** 2)
            corr_list.append(numerator / denominator)
        
        return corr_list

    def plot(self):
        if len(self._dt_ls) < 2:
            return
        fig = plt.figure(figsize=(8, 8))
        import matplotlib.gridspec as gridspec
        gs = gridspec.GridSpec(2, 1, height_ratios=[2.5, 1])
        ax = fig.add_subplot(gs[0])

        line3, = ax.plot(self._dt_ls, self._hold_ls, label="Hold count", color="#ECB051", linewidth=1, picker=5)
        line2, = ax.plot(self._dt_ls, 100*np.array(self._bm_returns_ls), label="Benchmark Returns", color="red", linewidth=2, picker=5)
        line1, = ax.plot(self._dt_ls, 100*np.array(self._returns_ls), label="Returns", color="blue", linewidth=2, picker=5)

        ax.fill_between(self._dt_ls, 100*np.array(self._returns_ls), color="#B9CFE9", alpha=0.5)
        ax.fill_between(self._dt_ls, self._hold_ls, color="#ECB762", alpha=0.5)

        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        # ax.set_title("PNL", fontsize=16)
        # ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Returns (%)", fontsize=12)

        # 自动格式化 x 轴标签
        fig.autofmt_xdate()
        # ax.legend()

        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.3", fc="lightblue", ec="black", lw=0.5),
                    arrowprops=dict(arrowstyle="-", connectionstyle="arc3,rad=.1", color="gray"))

        annot.set_visible(False)

        def update_annot(line, ind):
            # 获取鼠标悬停点的索引
            pos = line.get_xydata()[ind["ind"][0]]
            annot.xy = pos
            date_str = mdates.num2date(pos[0]).strftime("%Y-%m-%d")
            padding_length = max(0, len(f"Date:  {date_str}") - len(f"Returns:  {pos[1]:.2f}%"))
            padding = ' ' * (padding_length+1)
            text = f"Date:  {date_str}\nReturns:  {padding}{pos[1]:.2f} %"
            annot.set_text(text)
            annot.get_bbox_patch().set_alpha(0.9)  # 设置背景透明度，使其略显高亮

        def hover(event):
            # 如果鼠标在坐标轴范围内
            if event.inaxes == ax:
                # 检查鼠标是否在任一条曲线的范围内
                cont1, ind1 = line1.contains(event)
                cont2, ind2 = line2.contains(event)
                if cont1:
                    update_annot(line1, ind1)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                elif cont2:
                    update_annot(line2, ind2)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

        # 连接鼠标移动事件和 hover 函数
        fig.canvas.mpl_connect("motion_notify_event", hover)

        avg_holding_days = np.mean(self._holding_days_ls)
        # avg_hold = np.mean(self._hold_ls)

        winning_rate = len(self.gain_trades)/(len(self.gain_trades)+len(self.loss_trades))
        pl_ratio = abs(np.sum(self.gain_trades)/np.sum(self.loss_trades))

        start_cash = self._env.usercfg['start_cash']
        total_return_rate = self._returns_ls[-1]
        bm_total_return_rate = self._bm_returns_ls[-1]

        Rp = ((1 + total_return_rate) ** (250/len(self._dt_ls)) - 1)
        Rm = ((1 + bm_total_return_rate) ** (250/len(self._dt_ls)) - 1)
        
        cov_matrix = np.cov(self._Dp_ls, self._Dm_ls)
        covDpDm = cov_matrix[0, 1]
        varDm = np.var(self._Dm_ls)

        hold_cov_matrix = np.cov(self._hold_ls, self._Dm_ls)
        covholdDm = hold_cov_matrix[0, 1]
        hold_beta = covholdDm / varDm

        Rf = 0.04
        beta = covDpDm / varDm
        alpha = Rp - (Rf + beta * (Rm - Rf))

        Op = np.sqrt(250 * np.var(self._Dp_ls, ddof=1))
        sharpe = (Rp - Rf) / Op

        peak = np.maximum.accumulate(self._returns_ls)
        drawdown = peak - self._returns_ls
        max_P_drawdown = np.max(drawdown) * start_cash
        max_drawdown_index = np.argmax(drawdown)
        # Py 最低点收益值
        Py = (self._returns_ls[max_drawdown_index] + 1) * start_cash
        Px = max_P_drawdown + Py
        max_drawdown = (Px - Py)/Px

        ax.scatter(self._dt_ls[max_drawdown_index], 100*self._returns_ls[max_drawdown_index], color='black', s=25, zorder=5)

        trade_count = UserTrade.get_current_id()
        avg_hold = np.mean(self._hold_ls)
        text_str = f"Alpha: {alpha:.2f}    Beta(hold): {beta:.2f}({hold_beta:.2f})    Avg hold(days): {avg_hold:.2f}({avg_holding_days:.1f})     Win rate: {100*winning_rate:.2f}%    PL ratio: {pl_ratio:.2f} : 1"
        text_str2 = f"\nSharpe: {sharpe:.2f}    Volatility: {Op:.2f}    Trade count: {trade_count}    Rp: {100*Rp:.2f}%    Rm: {100*Rm:.2f}%    Max drawdown: {100*max_drawdown:.2f}%"
        # text_str3 = f"\nSharpe: {sharpe:.2f}    Volatility: {Op:.2f}    Trade count: {trade_count}    Rp: {100*Rp:.2f}%    Rm: {100*Rm:.2f}%    Max drawdown: {100*max_drawdown:.2f}%"

        ax.text(-0.10, 1.2, text_str+text_str2, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", edgecolor='white', facecolor='white'))
        
        # corr_ls = self.is_delay(self._hold_ls, self._hold_ls, len(self._hold_ls))
        corr_ls = self.autocorrelation(self._hold_ls, len(self._hold_ls))

        # periods, positive_fft_result = self.fft(self._hold_ls)
        
        fftax = fig.add_subplot(gs[1])
        line_fft = fftax.plot(corr_ls, label="Corrcoef delay", color="blue", linewidth=1)
        # line_fft = fftax.plot(periods, positive_fft_result, label="Hold count FFT", color="blue", linewidth=1)
        fftax.grid(True, which='both', linestyle='--', linewidth=0.5)
        fftax.set_title("Hold count self corrcoef", fontsize=10)

        plt.subplots_adjust(hspace=0.8) 
        plt.savefig('pnl_fft.png')
        plt.show() 