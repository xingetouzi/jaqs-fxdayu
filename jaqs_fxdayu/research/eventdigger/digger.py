# encoding = utf-8
from functools import reduce
import numpy as np
import pandas as pd
import jaqs.util as jutil
from . import performance as pfm


def get_exit_pos(signal,
                 value=None,
                 exit_type="close_long"):

    if value is None:
        if exit_type == "close_long":
            value = [1]
        else:
            value = [-1]

    # get sig pos
    sig_pos = pd.DataFrame(signal.index.values.reshape(-1, 1).repeat(len(signal.columns), axis=1))
    sig_pos.columns = signal.columns
    sig_pos.index = signal.index

    # get exit bool
    can_exit = signal.isin(value)

    sig_pos[~can_exit] = np.nan
    return sig_pos.fillna(method="bfill")


def get_period_exit_pos(signal,period):
    sig_pos = pd.DataFrame(signal.index.values.reshape(-1, 1).repeat(len(signal.columns), axis=1))
    sig_pos.columns = signal.columns
    sig_pos.index = signal.index
    return sig_pos.shift(-period)


def get_first_pos(a,b):
    a = a.replace(np.nan, 99999999)
    b = b.replace(np.nan, 99999999)
    c = (a[a <= b].fillna(0) + b[b < a].fillna(0))
    return c


def get_exit_value(value,exit_pos):
    def get_loc(x):
        return x.loc[exit_pos[x.name]].values

    exit_value = value.apply(lambda x: get_loc(x))
    return exit_value


def get_stop_pos_bool(stop_data,
                      now_data,
                      sig_type,
                      stop_type):
    if (sig_type=="long" and stop_type=="stop_loss") or \
            (sig_type=="short" and stop_type=="stop_profit"):
        dir = "+"
    else:
        dir = "-"
    if dir == "+":
        return stop_data - now_data >= 0
    else:
        return stop_data - now_data <= 0


def get_stop_pos(price,
                 target=0.08,
                 sig_type="long",
                 stop_type="stop_loss"):

    count = 0
    length = len(price)
    pos = []
    for index, row in price.iterrows():
        stop_row = row * (1+target)
        # data 止损价位
        data = pd.DataFrame(stop_row.values.reshape(-1, 1).T.repeat(length - count, axis=0))
        data.index = price.index[count:]
        data.columns = price.columns
        pos_bool = get_stop_pos_bool(data,price.iloc[count:, ],sig_type,stop_type).astype(int)
        pos.append(get_exit_pos(pos_bool, value=[1]).loc[index])
        count += 1
    return pd.DataFrame(pos)


# stack
def stack_td_symbol(df):
    df = pd.DataFrame(df.stack(dropna=False))  # do not dropna
    df.index.names = ['trade_date', 'symbol']
    df.sort_index(axis=0, level=['trade_date', 'symbol'], inplace=True)
    return df


def get_perf(ret):
    win_ret = ret[ret > 0].dropna()
    loss_ret = ret[ret <= 0].dropna()
    ret = ret.dropna()
    perf = pd.concat([pfm.cal_return_stats(win_ret),
                      pfm.cal_return_stats(loss_ret),
                      pfm.cal_return_stats(ret)])
    perf.index = ["win", "loss", "all"]
    perf["win_ratio"] = [np.nan, np.nan,
                         perf.loc["win", "occurance"] / perf.loc["all", "occurance"]]
    perf["win_mean/loss_mean"] = [np.nan, np.nan,
                                  -1 * perf.loc["win", "mean"] / perf.loc["loss", "mean"]]
    perf["expected_return_per_trade"] = perf["win_ratio"]*(1+perf["win_mean/loss_mean"]) -1
    return perf


class EventDigger():
    def __init__(self):
        self.final_exit_pos = dict()
        self.ret = dict()
        self.signal_data = dict()
        self.perf = dict()

    def process_signal(self,
                       enter_signal,
                       exit_signal=None,
                       sig_type="long",
                       price=None, daily_ret=None,
                       max_holding_period=None,
                       stoploss = None,
                       stopprofit = None,
                       mask=None,
                       can_enter=None,
                       can_exit=None,
                       commission=0.0008):
        """
        Prepare for signal analysis.

        Parameters
        ----------
        enter_signal : pd.DataFrame
            Index is date, columns are stocks.value can only be -2/0/2
        exit_signal : pd.DataFrame/list of pd.DataFrame
            Index is date, columns are stocks.value can only be -1/0/1
        sig_type: str
            "long"/"short", which type of signal to process
        price : pd.DataFrame
            Index is date, columns are stocks.
        daily_ret : pd.DataFrame
            Index is date, columns are stocks.
        mask : pd.DataFrame
            Data cells that should NOT be used.
        can_enter: pd.DataFrame
            Date the security can open.
        can_exit:pd.DataFrame
            Date the security can close.
        max_holding_period : int
            Limit the max holding period
        stoploss:float
            stoploss ratio per trade
        stopprofit:float
            stopprofit ratio per trade
        commission: float
            commission ratio per trade.
        Returns
        -------
        res : pd.DataFrame
            Signal processed
        """
        # ensure inputs are aligned
        # parameter validation
        if sig_type not in ["long","short"]:
            raise ValueError("信号类型(sig_type)只能为long/short.")

        if price is None and daily_ret is None:
            raise ValueError("One of price / daily_ret must be provided.")
        if price is not None and daily_ret is not None:
            raise ValueError("Only one of price / daily_ret should be provided.")

        # 确保enter_signal里的信号只能为-2(开空),0(不做操作),2(开多)
        enter_signal = jutil.fillinf(enter_signal).fillna(0)
        if not enter_signal.isin([-2,0,2]).all().all():
            raise ValueError("请确保enter_signal里的信号只能为-2(开空),0(不做操作),2(开多))")

        # 确保至少有一种出场信号
        if (exit_signal is None) and (max_holding_period is None) and \
                (stoploss is None) and (stopprofit is None):
            raise ValueError("确保至少有一种出场信号(exit_signal/max_holding_period/stoploss/stopprofit)")

        if exit_signal is not None:
            # 确保exit_signal里的信号只能为-1(平空),0(不做操作),1(平多)
            if not isinstance(exit_signal,list):
                exit_signal = [exit_signal]
            for i in range(len(exit_signal)):
                exit_signal[i] = exit_signal[i].reindex_like(enter_signal)
                exit_signal[i] = jutil.fillinf(exit_signal[i]).fillna(0)
                if not exit_signal[i].isin([-1,0,1]).all().all():
                    raise ValueError("请确保所有exit_signal里的信号只能为-1(平空),0(不做操作),1(平多)")
        else:
            exit_signal = []

        sig_filter = {
            "mask":mask,
            "can_enter":can_enter,
            "can_exit":can_exit,
        }

        for _filter in sig_filter.keys():
            if sig_filter[_filter] is not None:
                sig_filter[_filter] = sig_filter[_filter].reindex_like(enter_signal)
                sig_filter[_filter] = jutil.fillinf(sig_filter[_filter]).astype(int).fillna(0)
            else:
                sig_filter[_filter] = pd.DataFrame(index=enter_signal.index,
                                                   columns=enter_signal.columns,
                                                   data=0 if _filter=="mask" else 1)

        # process
        #=============================================================
        # 信号在当天的收盘时候统计，具体执行则在下一天的交易日的开盘－－设置price=open,
        # 或下一天交易日的收盘－－设置price=close,或别的价格－－如设置price=vwap
        # 防止未来函数
        enter_signal = enter_signal.shift(1)
        for i in range(len(exit_signal)):
            exit_signal[i] = exit_signal[i].shift(1)

        # 处理价格数据
        if daily_ret is not None:
            daily_ret = daily_ret.reindex_like(enter_signal)
            daily_ret = jutil.fillinf(daily_ret).fillna(0)
            price = pfm.daily_ret_to_cum(daily_ret) # 取净值
        else:
            # 有price
            price = price.reindex_like(enter_signal)
            price = jutil.fillinf(price) # 取价格

        #=====================
        # 调整出场点
        pos = []
        # 定时出场位置
        if max_holding_period is not None:
            pos.append(get_period_exit_pos(enter_signal,period=max_holding_period))

        # 止损出场位置
        if stoploss is not None:
            pos.append(get_stop_pos(price,stoploss,
                                    sig_type=sig_type,
                                    stop_type="stop_loss"))

        # 止盈出场位置
        if stopprofit is not None:
            pos.append(get_stop_pos(price, stopprofit,
                                    sig_type=sig_type,
                                    stop_type="stop_profit"))

        # 自定义出场信号位置
        for es in exit_signal:
            pos.append(get_exit_pos(es,
                                    exit_type="close_%s"%(sig_type,)))

        # 综合了各种出场条件，选择最先触发的出场条件出场
        exit_pos = reduce(get_first_pos, pos).replace(99999999,np.nan)
        # 每天允许出场的最近的出场点
        exit_permited_pos = get_exit_pos(sig_filter["can_exit"],
                                         value=[1])
        self.final_exit_pos[sig_type] = get_exit_value(exit_permited_pos,
                                                       exit_pos)
        # =====================
        # 计算信号收益
        price_exit = get_exit_value(price,self.final_exit_pos[sig_type])
        ret_exit = jutil.fillinf((price_exit - price)/price)
        if sig_type == "short":
            ret_exit = -1*ret_exit
        self.ret[sig_type] = ret_exit-commission

        # =====================
        # 计算signal_data
        # ----------------------------------------------------------------------
        # mask signal
        if sig_type=="long":
            value=2
        else:
            value=-2
        mask_signal = enter_signal != value
        mask_signal = np.logical_or(mask_signal,
                                    np.logical_or(sig_filter["mask"],
                                                  sig_filter["can_enter"]!=1))

        # ----------------------------------------------------------------------
        # concat signal value
        res = stack_td_symbol(enter_signal)
        res.columns = ['signal']
        res["return"] = stack_td_symbol(self.ret[sig_type])
        res["exit_time"] = stack_td_symbol(self.final_exit_pos[sig_type])
        mask_signal = stack_td_symbol(mask_signal)
        res = res.loc[~(mask_signal.iloc[:, 0]), :]

        if len(res) > 0:
            print("Nan Data Count (should be zero) : {:d};  " \
                  "Percentage of effective data: {:.0f}%".format(res.isnull().sum(axis=0).sum(),
                                                                 len(res) * 100. / enter_signal.size))
            res = res.astype({'signal': float, 'return': float})
            self.signal_data[sig_type] = res
        else:
            print("sig_type %s:No signal available."%(sig_type,))

    def create_event_report(self,sig_type="long"):
        if sig_type in self.signal_data.keys():
            ret = self.signal_data[sig_type]["return"]
            self.perf[sig_type] = get_perf(ret)
        else:
            print("请先处理%s信号(process_signal),方可进行%s绩效分析."%(sig_type,sig_type))

    def create_full_report(self):
        for sig_type in ["long","short"]:
            self.create_event_report(sig_type)

        if ("long" in self.signal_data.keys()) and ("short" in self.signal_data.keys()):
            ret = pd.concat([self.signal_data["long"]["return"],
                             self.signal_data["short"]["return"]])
            self.perf["all"] = get_perf(ret)




