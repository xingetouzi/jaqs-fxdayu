# encoding = utf-8
from functools import reduce
import numpy as np
import pandas as pd
import os
import jaqs.util as jutil
from . import plotting
from . import performance as pfm

LONGINT = 999999999999999


def get_sig_pos(signal):
    sig_pos = pd.DataFrame(signal.index.values.reshape(-1, 1).repeat(len(signal.columns), axis=1))
    sig_pos.columns = signal.columns
    sig_pos.index = signal.index
    return sig_pos


def get_exit_pos(signal,
                 value=None,
                 exit_type="close_long"):

    if value is None:
        if exit_type == "close_long":
            value = [1]
        else:
            value = [-1]

    # get sig pos
    sig_pos = get_sig_pos(signal)

    # get exit bool
    can_exit = signal.isin(value)

    sig_pos[~can_exit] = np.nan
    return sig_pos.fillna(method="bfill")


def get_period_exit_pos(signal,period):
    # get sig pos
    sig_pos = get_sig_pos(signal)
    return sig_pos.shift(-period)


def get_first_pos(a,b):
    a = a.replace(np.nan, LONGINT)
    b = b.replace(np.nan, LONGINT)
    c = (a[a <= b].fillna(0) + b[b < a].fillna(0))
    return c


def get_exit_value(value,exit_pos):
    def get_loc(x):
        if exit_pos[x.name].isnull().all():
            return exit_pos[x.name].values
        else:
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

    if sig_type=="short":
        target = -1*target
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
    return perf


class TimingDigger():
    def __init__(self, output_folder=".", output_format='pdf', signal_name=None):
        self.output_format = output_format
        self.output_folder = os.path.abspath(output_folder)
        self.signal_name = signal_name

        self.returns_report_data = dict()
        self.ic_report_data = dict()
        self.event_perf = dict()
        self.symbol_event_perf = dict()
        self.fig_data = dict()
        self.fig_objs = dict()

        self.final_exit_pos = dict()
        self.ret = dict()
        self.signal_data = dict()
        self.price = None

        self.period = None

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
                       group=None,
                       n_quantiles=1,
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
        n_quantiles: int
        group : pd.DataFrame
            Index is date, columns are stocks.
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
        if not (n_quantiles > 0 and isinstance(n_quantiles, int)):
            raise ValueError("n_quantiles must be a positive integer. Input is: {}".format(n_quantiles))

        enter_signal = jutil.fillinf(enter_signal)
        if n_quantiles==1: #　事件类进场信号
            # 确保enter_signal里的信号只能为-2(开空),0(不做操作),2(开多)
            enter_signal = enter_signal.fillna(0)
            if not enter_signal.isin([-2,0,2]).all().all():
                raise ValueError("检测到n_quantiles为1,该模式下测试的enter_signal为事件类因子."
                                 "请确保enter_signal里的信号只能为-2(开空),0(不做操作),2(开多))."
                                 "如需测试普通因子,请指定n_quantiles为大于1的整数.")
            # 确保至少有一种出场信号
            if (exit_signal is None) and (max_holding_period is None) and \
                    (stoploss is None) and (stopprofit is None):
                raise ValueError("确保至少有一种出场信号(exit_signal/max_holding_period/stoploss/stopprofit)")
        else: # 普通进场信号
            if max_holding_period is None:
                raise ValueError("检测到n_quantiles不为1,该模式下测试的enter_signal为普通因子."
                                 "该模式下,max_holding_period参数不能为空.")
            self.period = max_holding_period

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

        if group is not None:
            group = group.reindex_like(enter_signal)

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

        self.price = price

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
        exit_pos = reduce(get_first_pos, pos).replace(LONGINT,np.nan)
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
        if n_quantiles==1:# 事件因子
            if sig_type == "long":
                value = 2
            else:
                value = -2
            mask_signal = enter_signal != value
        else: # 普通因子
            mask_signal = enter_signal.isnull()

        mask_signal = np.logical_or(mask_signal,
                                    np.logical_or(sig_filter["mask"],
                                                  sig_filter["can_enter"]!=1))
        mask_signal = np.logical_or(mask_signal,
                                    self.ret[sig_type].isnull())

        # ban掉出场信号在进场那天的
        # get sig pos
        sig_pos = get_sig_pos(self.final_exit_pos[sig_type])
        mask_signal = np.logical_or(mask_signal,
                                    sig_pos == self.final_exit_pos[sig_type])

        # calculate quantile
        if n_quantiles == 1:
            df_quantile = pd.DataFrame(1,index=enter_signal.index,columns=enter_signal.columns)
        else:
            signal_masked = enter_signal.copy()
            signal_masked = signal_masked[~mask_signal]
            if group is None:
                df_quantile = jutil.to_quantile(signal_masked, n_quantiles=n_quantiles)
            else:
                from jaqs_fxdayu.data.py_expression_eval import Parser
                ps = Parser()
                ps.index_member = None
                df_quantile = ps.group_quantile(df=signal_masked,
                                                group=group,
                                                n_quantiles=n_quantiles)

        # ----------------------------------------------------------------------
        # concat signal value
        res = stack_td_symbol(enter_signal)
        res.columns = ['signal']
        res["return"] = stack_td_symbol(self.ret[sig_type])
        res["exit_time"] = stack_td_symbol(self.final_exit_pos[sig_type])
        res['quantile'] = stack_td_symbol(df_quantile)
        if group is not None:
            res["group"] = stack_td_symbol(group)
        res["sig_type"] = sig_type
        mask_signal = stack_td_symbol(mask_signal)
        res = res.loc[~(mask_signal.iloc[:, 0]), :]

        if len(res) > 0:
            print("Nan Data Count (should be zero) : {:d};  " \
                  "Percentage of effective data: {:.0f}%".format(res.isnull().sum(axis=0).sum(),
                                                                 len(res) * 100. / enter_signal.size))
            res = res.astype({'signal': float, 'return': float, 'quantile': int})
            self.signal_data[sig_type] = res
        else:
            print("sig_type %s:No signal available."%(sig_type,))

    def show_fig(self, fig, file_name):
        """
        Save fig object to self.output_folder/filename.

        Parameters
        ----------
        fig : matplotlib.figure.Figure
        file_name : str

        """

        self.fig_objs[file_name] = fig

        if self.output_format in ['pdf', 'png', 'jpg']:
            fp = os.path.join(self.output_folder, '.'.join([file_name, self.output_format]))
            jutil.create_dir(fp)
            fig.savefig(fp, dpi=200)
            print("Figure saved: {}".format(fp))
        elif self.output_format == 'base64':
            fig_b64 = jutil.fig2base64(fig, 'png')
            self.fig_data[file_name] = fig_b64
            print("Base64 data of figure {} will be stored in dictionary.".format(file_name))
        elif self.output_format == 'plot':
            fig.show()
        else:
            raise NotImplementedError("output_format = {}".format(self.output_format))

    # todo show fig
    def create_event_report(self,
                            sig_type="long",
                            by_symbol=False):
        """
        sig_type:long/short
        """
        def plot_entry_exit(x):
            gf = plotting.GridFigure(rows=1, cols=1)
            ax, symbol = plotting.get_entry_exit(x, self.price,
                                                 ax=gf.next_row())
            file_name = '%s_entry_exit_position/%s' % (sig_type,symbol)
            if self.signal_name is not None:
                file_name = self.signal_name + "/" + file_name
            self.show_fig(gf.fig, file_name)

        perf = None
        if sig_type in self.signal_data.keys():
            n_quantiles = self.signal_data[sig_type]['quantile'].max()
            if n_quantiles != 1:
                print("非事件因子不能进行事件分析.")
                return
            ret = self.signal_data[sig_type]["return"]
            perf = self.event_perf[sig_type] = get_perf(ret)
            if by_symbol:
                self.symbol_event_perf[sig_type] = ret.groupby("symbol").apply(lambda x: get_perf(x))
                # 画图
                if self.output_format:
                    self.signal_data[sig_type].groupby("symbol").apply(lambda x: plot_entry_exit(x))
        elif sig_type=="long_short":
            if ("long" in self.signal_data.keys()) and ("short" in self.signal_data.keys()):
                n_quantiles = max(self.signal_data["long"]['quantile'].max(),
                                  self.signal_data["short"]['quantile'].max())
                if n_quantiles != 1:
                    print("非事件因子不能进行事件分析.")
                    return
                ret = pd.concat([self.signal_data["long"]["return"],
                                 self.signal_data["short"]["return"]])
                perf = self.event_perf["long_short"] = get_perf(ret)
                if by_symbol:
                    self.symbol_event_perf["long_short"] = ret.groupby("symbol").apply(lambda x: get_perf(x))
                    if self.output_format:
                        signal_data = pd.concat([self.signal_data["long"],self.signal_data["short"]],axis=0).sort_index()
                        signal_data.groupby("symbol").apply(lambda x: plot_entry_exit(x))

        if perf is None:
            raise ValueError("无法分析绩效.当前待分析信号类型为%s,而%s信号未计算(需通过process_data进行计算.)"%(sig_type,sig_type))
        else:
            print("*****-Summary-*****")
            plotting.plot_event_table(perf)

    @plotting.customize
    def create_returns_report(self,sig_type="long"):
        """
        Creates a tear sheet for returns analysis of a signal.
        sig_type:long/short
        """
        if sig_type in self.signal_data.keys():
            n_quantiles = self.signal_data[sig_type]['quantile'].max()
            if n_quantiles==1:
                print("事件因子不能进行quantile收益分析.")
                return
            else:
                signal_data = self.signal_data[sig_type]

                # ----------------------------------------------------------------------------------
                # Daily Signal Return Time Series
                # quantile return
                period_wise_quantile_ret_stats = pfm.calc_quantile_return_mean_std(signal_data, time_series=True)
                cum_quantile_ret = pd.concat({k: pfm.period_wise_ret_to_cum(v['mean'], period=self.period, compound=True)
                                              for k, v in period_wise_quantile_ret_stats.items()},
                                             axis=1)

                # top quantile minus bottom quantile return
                period_wise_tmb_ret = pfm.calc_return_diff_mean_std(period_wise_quantile_ret_stats[n_quantiles],
                                                                    period_wise_quantile_ret_stats[1])
                cum_tmb_ret = pfm.period_wise_ret_to_cum(period_wise_tmb_ret['mean_diff'], period=self.period, compound=True)

                # start plotting
                if self.output_format:
                    vertical_sections = 4
                    gf = plotting.GridFigure(rows=vertical_sections, cols=1)
                    gf.fig.suptitle("Returns Tear Sheet\n\n(compound)\n (period length = {:d} days)".format(self.period))

                    plotting.plot_quantile_returns_ts(period_wise_quantile_ret_stats,
                                                      ax=gf.next_row())

                    plotting.plot_cumulative_returns_by_quantile(cum_quantile_ret,
                                                                 ax=gf.next_row())

                    plotting.plot_mean_quantile_returns_spread_time_series(period_wise_tmb_ret,
                                                                           self.period,
                                                                           bandwidth=0.5,
                                                                           ax=gf.next_row())

                    plotting.plot_cumulative_return(cum_tmb_ret,
                                                    title="Top Minus Bottom (long top, short bottom)"
                                                          "Portfolio Cumulative Return",
                                                    ax=gf.next_row())

                    file_name = 'sig_type:%s_returns_report'%(sig_type,)
                    if self.signal_name is not None:
                        file_name = self.signal_name+"#"+file_name
                    self.show_fig(gf.fig, file_name)

                self.returns_report_data[sig_type] = {'period_wise_quantile_ret': period_wise_quantile_ret_stats,
                                                      'cum_quantile_ret': cum_quantile_ret,
                                                      'period_wise_tmb_ret': period_wise_tmb_ret,
                                                      'cum_tmb_ret': cum_tmb_ret}

    @plotting.customize
    def create_information_report(self,sig_type="long"):
        """
        Creates a tear sheet for information analysis of a signal.

        """
        if sig_type in self.signal_data.keys():
            n_quantiles = self.signal_data[sig_type]['quantile'].max()
            if n_quantiles==1:
                print("事件因子不能进行ic分析.")
                return
            else:
                signal_data = self.signal_data[sig_type]
                ic = pfm.calc_signal_ic(signal_data)
                ic.index = pd.to_datetime(ic.index, format="%Y%m%d")
                monthly_ic = pfm.mean_information_coefficient(ic, "M")

                if self.output_format:
                    ic_summary_table = pfm.calc_ic_stats_table(ic.dropna())
                    plotting.plot_information_table(ic_summary_table)

                    columns_wide = 2
                    fr_cols = len(ic.columns)
                    rows_when_wide = (((fr_cols - 1) // columns_wide) + 1)
                    vertical_sections = fr_cols + 3 * rows_when_wide + 2 * fr_cols
                    gf = plotting.GridFigure(rows=vertical_sections, cols=columns_wide)
                    gf.fig.suptitle("Information Coefficient Report\n\n(period length = {:d} days)"
                                    "\ndaily IC = rank_corr(period-wise forward return, signal value)".format(self.period))

                    plotting.plot_ic_ts(ic, self.period, ax=gf.next_row())
                    plotting.plot_ic_hist(ic, self.period, ax=gf.next_row())

                    plotting.plot_monthly_ic_heatmap(monthly_ic, period=self.period, ax=gf.next_row())

                    file_name = 'sig_type:%s_information_report'% (sig_type,)
                    if self.signal_name is not None:
                        file_name = self.signal_name+"#"+file_name
                    self.show_fig(gf.fig, file_name)

                self.ic_report_data[sig_type] = {'daily_ic': ic,
                                                 'monthly_ic': monthly_ic}





