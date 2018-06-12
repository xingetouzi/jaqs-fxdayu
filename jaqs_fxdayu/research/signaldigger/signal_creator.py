# encoding=utf-8

from .analysis import compute_downside_returns, compute_upside_returns
from . import performance as pfm
import pandas as pd
import numpy as np
import jaqs.util as jutil


def _process_filter(_filter):
    if _filter is not None:
        _filter = jutil.fillinf(_filter)
        _filter = _filter.astype(int).fillna(0).astype(bool)
    return _filter


def _assert(standard, tmp):
    if tmp is not None:
        assert np.all(standard.index == tmp.index)
        assert np.all(standard.columns == tmp.columns)


def _get_df(index,columns,value):
    return pd.DataFrame(index=index, columns=columns, data=value)


class SignalCreator(object):
    def __init__(self,
                 price=None, daily_ret=None,
                 benchmark_price=None, daily_benchmark_ret=None,
                 high=None, low=None,
                 group=None,
                 period=5, n_quantiles=5,
                 mask=None,
                 can_enter=None,
                 can_exit=None,
                 forward=True,
                 commission=0.0008):

        if price is None and daily_ret is None:
            raise ValueError("One of price / daily_ret must be provided.")
        if price is not None and daily_ret is not None:
            raise ValueError("Only one of price / daily_ret should be provided.")
        if benchmark_price is not None and daily_benchmark_ret is not None:
            raise ValueError("Only one of benchmark_price / daily_benchmark_ret should be provided.")
        if not (n_quantiles > 0 and isinstance(n_quantiles, int)):
            raise ValueError("n_quantiles must be a positive integer. Input is: {}".format(n_quantiles))

        self.price = price
        self.daily_ret = daily_ret
        self.high = high
        self.low = low
        self.group = group
        self.n_quantiles = n_quantiles
        self.mask = _process_filter(mask)
        self.can_enter = _process_filter(can_enter)
        self.can_exit = _process_filter(can_exit)

        self.period = period
        self.benchmark_price = benchmark_price
        self.daily_benchmark_ret = daily_benchmark_ret
        self.forward = forward
        self.commission = commission

        self.benchmark_ret = None
        self.signal_data = None
        self.signal_ret = None

    def _judge(self, signal):
        # 生成filter的dataframe
        self.mask = _get_df(signal.index, signal.columns, False) if self.mask is None else self.mask
        self.can_enter = _get_df(signal.index, signal.columns, True) if self.can_enter is None else self.can_enter
        self.can_exit = _get_df(signal.index, signal.columns, True) if self.can_exit is None else self.can_exit

        # df shape确认
        _assert(signal, self.mask)
        _assert(signal, self.can_enter)
        _assert(signal, self.can_exit)
        _assert(signal, self.group)

        if self.signal_ret is not None:
            for ret_type in self.signal_ret.keys():
                _assert(signal, self.signal_ret[ret_type])
        else:
            _assert(signal, self.price)
            _assert(signal, self.daily_ret)
            _assert(signal, self.high)
            _assert(signal, self.low)

    def _cal_ret(self):
        if self.signal_ret is not None:
            return
        else:
            # 计算benchmark收益
            if self.benchmark_price is not None:
                self.benchmark_ret = pfm.price2ret(self.benchmark_price, self.period, axis=0, compound=True)
            elif self.daily_benchmark_ret is not None:
                self.benchmark_ret = pfm.daily_ret_to_ret(self.daily_benchmark_ret, self.period)

            # 计算区间持仓收益
            isRealPrice = False
            if self.daily_ret is not None:
                self.daily_ret = jutil.fillinf(self.daily_ret).fillna(0)
                self.price = pfm.daily_ret_to_cum(self.daily_ret)
            else:
                # 有price
                isRealPrice = True
                self.price = jutil.fillinf(self.price)

            self.can_enter = np.logical_and(self.price != np.NaN, self.can_enter)
            df_ret = pfm.price2ret(self.price, period=self.period, axis=0, compound=True)
            price_can_exit = self.price.copy()
            price_can_exit[~self.can_exit] = np.NaN
            price_can_exit = price_can_exit.fillna(method="bfill")
            ret_can_exit = pfm.price2ret(price_can_exit, period=self.period, axis=0, compound=True)
            df_ret[~self.can_exit] = ret_can_exit[~self.can_exit]

            if self.benchmark_ret is not None:
                # 计算持有期相对收益
                self.benchmark_ret = self.benchmark_ret.reindex(df_ret.index)
                residual_ret = df_ret.sub(self.benchmark_ret.values.flatten(), axis=0)
            else:
                residual_ret = df_ret
            residual_ret = jutil.fillinf(residual_ret)
            residual_ret -= self.commission

            # 计算潜在上涨空间和潜在下跌空间
            if self.high is not None and isRealPrice:
                self.high = jutil.fillinf(self.high)
            else:
                self.high = self.price
            upside_ret = compute_upside_returns(self.price, self.high, self.can_exit, self.period, compound=True)
            upside_ret = jutil.fillinf(upside_ret)
            upside_ret -= self.commission

            if self.low is not None and isRealPrice:
                self.low = jutil.fillinf(self.low)
            else:
                self.low = self.price
            downside_ret = compute_downside_returns(self.price, self.low, self.can_exit, self.period, compound=True)
            downside_ret = jutil.fillinf(downside_ret)
            downside_ret -= self.commission

            self.signal_ret = {
                "return": residual_ret,
                "upside_ret": upside_ret,
                "downside_ret": downside_ret
            }
            if self.forward:
                for ret_type in self.signal_ret.keys():
                    if self.signal_ret[ret_type] is not None:
                        # point-in-time signal and forward return
                        self.signal_ret[ret_type] = self.signal_ret[ret_type].shift(-self.period)
            else:
                self.can_enter = self.can_enter.shift(self.period)
                self.mask = self.mask.shift(self.period)

            # 处理mask
            self.mask = np.logical_or(self.mask.fillna(True), ~(self.can_enter.fillna(False)))

    def get_signal_data(self, signal):
        """
        Returns
        -------
        res : pd.DataFrame
            Index is pd.MultiIndex ['trade_date', 'symbol'], columns = ['signal', 'return', 'upside_ret(N)','downside_ret(N)','quantile']
        """
        self._judge(signal)  # 判断signal与其他关键参数是否格式一致
        self._cal_ret()  # 计算信号收益
        signal = jutil.fillinf(signal)
        signal = signal.shift(1)  # avoid forward-looking bias

        # forward or not
        if not self.forward:
            signal = signal.shift(self.period)

        # 处理mask
        mask = np.logical_or(self.mask, signal.isnull())

        # calculate quantile
        signal_masked = signal.copy()
        signal_masked = signal_masked[~mask]
        if self.n_quantiles == 1:
            df_quantile = signal_masked.copy()
            df_quantile.loc[:, :] = 1.0
        else:
            df_quantile = jutil.to_quantile(signal_masked, n_quantiles=self.n_quantiles)

        # ----------------------------------------------------------------------
        # stack
        def stack_td_symbol(df):
            df = pd.DataFrame(df.stack(dropna=False))  # do not dropna
            df.index.names = ['trade_date', 'symbol']
            df.sort_index(axis=0, level=['trade_date', 'symbol'], inplace=True)
            return df

        # ----------------------------------------------------------------------
        # concat signal value
        res = stack_td_symbol(signal)  # 信号
        res.columns = ['signal']

        for ret_type in self.signal_ret.keys():
            if self.signal_ret[ret_type] is not None:
                res[ret_type] = stack_td_symbol(self.signal_ret[ret_type]).fillna(0)  # 收益

        if self.group is not None:
            res["group"] = stack_td_symbol(self.group)

        res['quantile'] = stack_td_symbol(df_quantile)  # quantile
        mask = stack_td_symbol(mask)
        res = res.loc[~(mask.iloc[:, 0]), :]

        if len(res) > 0:
            print("Nan Data Count (should be zero) : {:d};  " \
                  "Percentage of effective data: {:.0f}%".format(res.isnull().sum(axis=0).sum(),
                                                                 len(res) * 100. / signal.size))
        else:
            print("No signal available.")
        res = res.astype({'signal': float, 'return': float, 'quantile': int})
        return res
