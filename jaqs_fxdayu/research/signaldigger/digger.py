from collections import OrderedDict

import numpy as np
import pandas as pd

import jaqs.util as jutil
from jaqs.research.signaldigger import SignalDigger as OriginSignalDigger, plotting
from jaqs.research.signaldigger.digger import get_dummy_grouper, calc_calendar_distribution
from jaqs.trade import common

from jaqs_fxdayu.patch_util import auto_register_patch
from .analysis import compute_downside_returns, compute_upside_returns
from . import performance as pfm


@auto_register_patch(parent_level=2)
class SignalDigger(OriginSignalDigger):
    def __init__(self, *args, **kwargs):
        super(SignalDigger, self).__init__(*args, **kwargs)
        self.ret = None

    def process_signal_before_analysis(self,
                                       signal, price=None, ret=None, benchmark_price=None,
                                       high=None, low=None,
                                       group=None,
                                       period=5, n_quantiles=5,
                                       mask=None,
                                       can_enter=None,
                                       can_exit=None,
                                       forward=True,
                                       commission=0.0008):
        """
        Prepare for signal analysis.

        Parameters
        ----------
        signal : pd.DataFrame
            Index is date, columns are stocks.
        price : pd.DataFrame
            Index is date, columns are stocks.
        high : pd.DataFrame
            Index is date, columns are stocks.
        low : pd.DataFrame
            Index is date, columns are stocks.
        ret : pd.DataFrame
            Index is date, columns are stocks.
        group : pd.DataFrame
            Index is date, columns are stocks.
        benchmark_price : pd.DataFrame or pd.Series or None
            Price of benchmark.
        mask : pd.DataFrame
            Data cells that should NOT be used.
        can_enter: pd.DataFrame
            Date the security can be trade and BUY.
        can_exit:pd.DataFrame
            Date the security can be trade and SELL.
        n_quantiles : int
        period : int
            periods to compute forward returns on.
        forward :bool
            Return cal method. True by default.
        commission: float
            commission ratio per trade.
        Returns
        -------
        res : pd.DataFrame
            Index is pd.MultiIndex ['trade_date', 'symbol'], columns = ['signal', 'return', 'upside_ret(N)','downside_ret(N)','quantile']
        """
        """
        Deal with suspensions:
            If the period of calculating return is d (from T to T+d), then
            we do not use signal values of those suspended on T,
            we do not calculate return for those suspended on T+d.
        """
        # ----------------------------------------------------------------------
        # parameter validation
        if price is None and ret is None:
            raise ValueError("One of price / ret must be provided.")
        if price is not None and ret is not None:
            raise ValueError("Only one of price / ret should be provided.")
        if ret is not None and benchmark_price is not None:
            raise ValueError("You choose 'return' mode but benchmark_price is given.")
        if not (n_quantiles > 0 and isinstance(n_quantiles, int)):
            raise ValueError("n_quantiles must be a positive integer. Input is: {}".format(n_quantiles))

        # ensure inputs are aligned
        if mask is not None:
            assert np.all(signal.index == mask.index)
            assert np.all(signal.columns == mask.columns)
            mask = jutil.fillinf(mask)
            mask = mask.astype(int).fillna(0).astype(bool)  # dtype of mask could be float. So we need to convert.
        else:
            mask = pd.DataFrame(index=signal.index, columns=signal.columns, data=False)
        if can_enter is not None:
            assert np.all(signal.index == can_enter.index)
            assert np.all(signal.columns == can_enter.columns)
            can_enter = jutil.fillinf(can_enter)
            can_enter = can_enter.astype(int).fillna(0).astype(
                bool)  # dtype of can_enter could be float. So we need to convert.
        else:
            can_enter = pd.DataFrame(index=signal.index, columns=signal.columns, data=True)
        if can_exit is not None:
            assert np.all(signal.index == can_exit.index)
            assert np.all(signal.columns == can_exit.columns)
            can_exit = jutil.fillinf(can_exit)
            can_exit = can_exit.astype(int).fillna(0).astype(
                bool)  # dtype of can_exit could be float. So we need to convert.
        else:
            can_exit = pd.DataFrame(index=signal.index, columns=signal.columns, data=True)
        if group is not None:
            assert np.all(signal.index == group.index)
            assert np.all(signal.columns == group.columns)

        signal = jutil.fillinf(signal)

        # ----------------------------------------------------------------------
        # save data
        self.n_quantiles = n_quantiles
        self.period = period

        # ----------------------------------------------------------------------
        # Get dependent variables
        upside_ret = None
        downside_ret = None
        if price is not None:
            assert np.all(signal.index == price.index)
            assert np.all(signal.columns == price.columns)
            price = jutil.fillinf(price)
            can_enter = np.logical_and(price != np.NaN, can_enter)
            df_ret = pfm.price2ret(price, period=self.period, axis=0, compound=True)
            price_can_exit = price.copy()
            price_can_exit[~can_exit] = np.NaN
            price_can_exit = price_can_exit.fillna(method="bfill")
            ret_can_exit = pfm.price2ret(price_can_exit, period=self.period, axis=0, compound=True)
            df_ret[~can_exit] = ret_can_exit[~can_exit]
            if benchmark_price is not None:
                benchmark_price = benchmark_price.loc[signal.index]
                bench_ret = pfm.price2ret(benchmark_price, self.period, axis=0, compound=True)
                self.benchmark_ret = bench_ret
                residual_ret = df_ret.sub(bench_ret.values.flatten(), axis=0)
            else:
                residual_ret = df_ret
            residual_ret = jutil.fillinf(residual_ret)
            residual_ret -= commission
            # 计算潜在上涨空间和潜在下跌空间
            if high is not None:
                assert np.all(signal.index == high.index)
                assert np.all(signal.columns == high.columns)
                high = jutil.fillinf(high)
                upside_ret = compute_upside_returns(price, high, can_exit, self.period, compound=True)
                upside_ret = jutil.fillinf(upside_ret)
                upside_ret -= commission
            if low is not None:
                assert np.all(signal.index == low.index)
                assert np.all(signal.columns == low.columns)
                low = jutil.fillinf(low)
                downside_ret = compute_downside_returns(price, low, can_exit, self.period, compound=True)
                downside_ret = jutil.fillinf(downside_ret)
                downside_ret -= commission
        else:
            residual_ret = jutil.fillinf(ret)

        # Get independent varibale
        signal = signal.shift(1)  # avoid forward-looking bias
        # forward or not
        if forward:
            # point-in-time signal and forward return
            residual_ret = residual_ret.shift(-self.period)
            if upside_ret is not None:
                upside_ret = upside_ret.shift(-self.period)
            if downside_ret is not None:
                downside_ret = downside_ret.shift(-self.period)
        else:
            # past signal and point-in-time return
            signal = signal.shift(self.period)
            can_enter = can_enter.shift(self.period)
            mask = mask.shift(self.period)

        self.ret = dict()
        self.ret["return"] = residual_ret
        if upside_ret is not None:
            self.ret["upside_ret"] = upside_ret
        if downside_ret is not None:
            self.ret["downside_ret"] = downside_ret

        # ----------------------------------------------------------------------
        # get masks
        # mask_prices = data.isnull()
        # Because we use FORWARD return, if one day's price is broken, the day that is <period> days ago is also broken.
        # mask_prices = np.logical_or(mask_prices, mask_prices.shift(self.period))
        # mask_price_return = residual_ret.isnull()
        mask_signal = signal.isnull()

        mask = np.logical_or(mask.fillna(True), np.logical_or(mask_signal, ~(can_enter.fillna(False))))
        # mask = np.logical_or(mask, mask_signal)

        # if price is not None:
        #     mask_forward = np.logical_or(mask, mask.shift(self.period).fillna(True))
        #     mask = np.logical_or(mask, mask_forward)

        # ----------------------------------------------------------------------
        # calculate quantile
        signal_masked = signal.copy()
        signal_masked = signal_masked[~mask]
        if n_quantiles == 1:
            df_quantile = signal_masked.copy()
            df_quantile.loc[:, :] = 1.0
        else:
            df_quantile = jutil.to_quantile(signal_masked, n_quantiles=n_quantiles)

        # ----------------------------------------------------------------------
        # stack
        def stack_td_symbol(df):
            df = pd.DataFrame(df.stack(dropna=False))  # do not dropna
            df.index.names = ['trade_date', 'symbol']
            df.sort_index(axis=0, level=['trade_date', 'symbol'], inplace=True)
            return df

        mask = stack_td_symbol(mask)
        df_quantile = stack_td_symbol(df_quantile)
        residual_ret = stack_td_symbol(residual_ret)

        # ----------------------------------------------------------------------
        # concat signal value
        res = stack_td_symbol(signal)
        res.columns = ['signal']
        res['return'] = residual_ret.fillna(0)
        if upside_ret is not None:
            res["upside_ret"] = stack_td_symbol(upside_ret).fillna(0)
        if downside_ret is not None:
            res["downside_ret"] = stack_td_symbol(downside_ret).fillna(0)
        if group is not None:
            res["group"] = stack_td_symbol(group)
        res['quantile'] = df_quantile
        res = res.loc[~(mask.iloc[:, 0]), :]

        if len(res) > 0:
            print("Nan Data Count (should be zero) : {:d};  " \
                  "Percentage of effective data: {:.0f}%".format(res.isnull().sum(axis=0).sum(),
                                                                 len(res) * 100. / signal.size))
        else:
            print("No signal available.")
        res = res.astype({'signal': float, 'return': float, 'quantile': int})
        self.signal_data = res

    def create_binary_event_report(self, signal, price, mask=None,
                                   can_enter=None, can_exit=None,
                                   benchmark_price=None, periods=(5, 10, 20),
                                   join_method_periods='inner', group_by=None):
        """
        Parameters
        ----------
        signal : pd.DataFrame
        price : pd.DataFrame
        mask : pd.DataFrame
        benchmark_price : pd.DataFrame
        periods : list of int
        join_method_periods : {'inner', 'outer'}.
            Whether to take intersection or union of data of different periods.
        group_by : {'year', 'month', None}
            Calculate various statistics within each year/month/whole sample.

        Returns
        -------
        res : dict

        """
        import scipy.stats as scst

        # Raw Data
        dic_signal_data = OrderedDict()
        for my_period in periods:
            self.process_signal_before_analysis(signal, price=price, mask=mask,
                                                can_enter=can_enter,
                                                can_exit=can_exit,
                                                n_quantiles=1, period=my_period,
                                                benchmark_price=benchmark_price,
                                                forward=True)
            if len(self.signal_data) > 0:
                dic_signal_data[my_period] = self.signal_data

        if not dic_signal_data:
            print("No binary event available.")
            return None, None, None
        # Processed Data
        dic_events = OrderedDict()
        dic_all = OrderedDict()
        for period, df in dic_signal_data.items():
            ser_ret = df['return']
            ser_sig = df['signal'].astype(bool)
            events_ret = ser_ret.loc[ser_sig]
            dic_events[period] = events_ret
            dic_all[period] = ser_ret
        df_events = pd.concat(dic_events, axis=1, join=join_method_periods)
        df_all = pd.concat(dic_all, axis=1, join=join_method_periods)

        # Data Statistics
        def _calc_statistics(df):
            df_res = pd.DataFrame(index=periods,
                                  columns=['Annu. Ret.', 'Annu. Vol.',
                                           # 'Annual Return (all sample)', 'Annual Volatility (all sample)',
                                           't-stat', 'p-value', 'skewness', 'kurtosis', 'occurance'],
                                  data=np.nan)
            df_res.index.name = 'Period'

            ser_periods = pd.Series(index=df.columns, data=df.columns.values)
            ratio = (1.0 * common.CALENDAR_CONST.TRADE_DAYS_PER_YEAR / ser_periods)
            mean = df.mean(axis=0)
            std = df.std(axis=0)
            annual_ret, annual_vol = mean * ratio, std * np.sqrt(ratio)

            t_stats, p_values = scst.ttest_1samp(df.values, np.zeros(df.shape[1]), axis=0)
            df_res.loc[:, 't-stat'] = t_stats
            df_res.loc[:, 'p-value'] = np.round(p_values, 5)
            df_res.loc[:, "skewness"] = scst.skew(df, axis=0)
            df_res.loc[:, "kurtosis"] = scst.kurtosis(df, axis=0)
            df_res.loc[:, 'Annu. Ret.'] = annual_ret
            df_res.loc[:, 'Annu. Vol.'] = annual_vol
            df_res.loc[:, 'occurance'] = len(df)
            # dic_res[period] = df
            return df_res

        if group_by == 'year':
            grouper_func = jutil.date_to_year
        elif group_by == 'month':
            grouper_func = jutil.date_to_month
        else:
            grouper_func = get_dummy_grouper

        idx_group = grouper_func(df_events.index.get_level_values('trade_date'))
        df_stats = df_events.groupby(idx_group).apply(_calc_statistics)
        idx_group_all = grouper_func(df_all.index.get_level_values('trade_date'))
        df_all_stats = df_all.groupby(idx_group_all).apply(_calc_statistics)
        df_all_stats = df_all_stats.loc[df_stats.index, ['Annu. Ret.', 'Annu. Vol.']]
        df_all_stats.columns = ['Annu. Ret. (all samp)', 'Annu. Vol. (all samp)']
        df_stats = pd.concat([df_stats, df_all_stats], axis=1)

        # return df_all, df_events, df_stats
        ser_signal_raw, monthly_signal, yearly_signal = calc_calendar_distribution(signal)

        # return
        # plot
        gf = plotting.GridFigure(rows=len(np.unique(idx_group)) * len(periods) + 3, cols=2, height_ratio=1.2)
        gf.fig.suptitle("Event Return Analysis (annualized)")

        plotting.plot_calendar_distribution(ser_signal_raw,
                                            monthly_signal=monthly_signal, yearly_signal=yearly_signal,
                                            ax1=gf.next_row(), ax2=gf.next_row())
        plotting.plot_event_bar(df_stats.reset_index(), x='Period', y='Annu. Ret.', hue='trade_date', ax=gf.next_row())

        # plotting.plot_event_pvalue(df_stats['p-value'], ax=gf.next_subrow())

        def _plot_dist(df):
            date = grouper_func(df.index.get_level_values('trade_date'))[0]
            plotting.plot_event_dist(df, group_by.title() + ' ' + str(date), axs=[gf.next_cell() for _ in periods])

        if group_by is not None:
            df_events.groupby(idx_group).apply(_plot_dist)
        else:
            plotting.plot_event_dist(df_events, "", axs=[gf.next_cell() for _ in periods])

        self.show_fig(gf.fig, 'event_report')

        # dic_res['df_res'] = df_res
        return df_all, df_events, df_stats