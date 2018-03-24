# encoding=utf-8

from .analysis import compute_downside_returns, compute_upside_returns
from . import performance as pfm
import pandas as pd
import numpy as np
import jaqs.util as jutil


class SignalCreator(object):
    def __init__(self,
                 price=None,
                 ret=None,
                 high=None,
                 low=None,
                 group=None,
                 n_quantiles=5,
                 mask=None,
                 can_enter=None,
                 can_exit=None,
                 period=5,
                 benchmark_price=None,
                 forward=True,
                 commission=0.0008):

        if price is None and ret is None:
            raise ValueError("One of price / ret must be provided.")
        if price is not None and ret is not None:
            raise ValueError("Only one of price / ret should be provided.")
        if ret is not None and benchmark_price is not None:
            raise ValueError("You choose 'return' mode but benchmark_price is given.")
        if not (n_quantiles > 0 and isinstance(n_quantiles, int)):
            raise ValueError("n_quantiles must be a positive integer. Input is: {}".format(n_quantiles))

        self.price = price
        self.ret = ret
        self.high = high
        self.low = low
        self.group = group
        self.n_quantiles = n_quantiles

        if mask is not None:
            mask = jutil.fillinf(mask)
            mask = mask.astype(int).fillna(0).astype(bool)
        self.mask = mask

        if can_enter is not None:
            can_enter = jutil.fillinf(can_enter)
            can_enter = can_enter.astype(int).fillna(0).astype(bool)
        self.can_enter = can_enter

        if can_exit is not None:
            can_exit = jutil.fillinf(can_exit)
            can_exit = can_exit.astype(int).fillna(0).astype(bool)
        self.can_exit = can_exit

        self.period = period
        self.benchmark_price = benchmark_price
        self.forward = forward
        self.commission = commission

        self.signal_data = None
        self.signal_ret = None

    def _judge(self, signal):
        if self.mask is not None:
            assert np.all(signal.index == self.mask.index)
            assert np.all(signal.columns == self.mask.columns)
        else:
            self.mask = pd.DataFrame(index=signal.index, columns=signal.columns, data=False)

        if self.can_enter is not None:
            assert np.all(signal.index == self.can_enter.index)
            assert np.all(signal.columns == self.can_enter.columns)
        else:
            self.can_enter = pd.DataFrame(index=signal.index, columns=signal.columns, data=True)

        if self.can_exit is not None:
            assert np.all(signal.index == self.can_exit.index)
            assert np.all(signal.columns == self.can_exit.columns)
        else:
            self.can_exit = pd.DataFrame(index=signal.index, columns=signal.columns, data=True)

        if self.group is not None:
            assert np.all(signal.index == self.group.index)
            assert np.all(signal.columns == self.group.columns)

        if self.signal_ret is not None:
            for ret_type in self.signal_ret.keys():
                if self.signal_ret[ret_type] is not None:
                    assert np.all(signal.index == self.signal_ret[ret_type].index)
                    assert np.all(signal.columns == self.signal_ret[ret_type].columns)
        else:
            if self.price is not None:
                assert np.all(signal.index == self.price.index)
                assert np.all(signal.columns == self.price.columns)
            elif self.ret is not None:
                assert np.all(signal.index == self.ret.index)
                assert np.all(signal.columns == self.ret.columns)
            if self.high is not None:
                assert np.all(signal.index == self.high.index)
                assert np.all(signal.columns == self.high.columns)
            if self.low is not None:
                assert np.all(signal.index == self.low.index)
                assert np.all(signal.columns == self.low.columns)

    def _cal_ret(self):
        if self.signal_ret is not None:
            return
        else:
            upside_ret = None
            downside_ret = None
            if self.price is not None:
                self.price = jutil.fillinf(self.price)
                self.can_enter = np.logical_and(self.price != np.NaN, self.can_enter)
                df_ret = pfm.price2ret(self.price, period=self.period, axis=0, compound=True)
                price_can_exit = self.price.copy()
                price_can_exit[~self.can_exit] = np.NaN
                price_can_exit = price_can_exit.fillna(method="bfill")
                ret_can_exit = pfm.price2ret(price_can_exit, period=self.period, axis=0, compound=True)
                df_ret[~self.can_exit] = ret_can_exit[~self.can_exit]
                if self.benchmark_price is not None:
                    benchmark_price = self.benchmark_price.loc[self.price.index]
                    bench_ret = pfm.price2ret(benchmark_price, self.period, axis=0, compound=True)
                    residual_ret = df_ret.sub(bench_ret.values.flatten(), axis=0)
                else:
                    residual_ret = df_ret
                residual_ret = jutil.fillinf(residual_ret)
                residual_ret -= self.commission
                # 计算潜在上涨空间和潜在下跌空间
                if self.high is not None:
                    self.high = jutil.fillinf(self.high)
                    upside_ret = compute_upside_returns(self.price, self.high, self.can_exit, self.period,
                                                        compound=True)
                    upside_ret = jutil.fillinf(upside_ret)
                    upside_ret -= self.commission
                if self.low is not None:
                    self.low = jutil.fillinf(self.low)
                    downside_ret = compute_downside_returns(self.price, self.low, self.can_exit, self.period,
                                                            compound=True)
                    downside_ret = jutil.fillinf(downside_ret)
                    downside_ret -= self.commission
            else:
                residual_ret = jutil.fillinf(self.ret)
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
