# encoding = utf-8

from collections import OrderedDict

import numpy as np
import pandas as pd

import jaqs.util as jutil
from jaqs.research.signaldigger import SignalDigger as OriginSignalDigger
from jaqs.research.signaldigger.digger import get_dummy_grouper, calc_calendar_distribution
from jaqs.trade import common

from jaqs_fxdayu.patch_util import auto_register_patch
from .analysis import compute_downside_returns, compute_upside_returns
from . import performance as pfm
from . import plotting
import warnings


@auto_register_patch(parent_level=2)
class SignalDigger(OriginSignalDigger):
    def __init__(self, *args, signal_name=None, **kwargs):
        super(SignalDigger, self).__init__(*args, **kwargs)
        self.ret = None
        self.signal_name = signal_name

    def process_signal_before_analysis(self,
                                       signal,
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
        daily_ret : pd.DataFrame
            Index is date, columns are stocks.
        daily_benchmark_ret : pd.DataFrame or pd.Series or None
            Daily ret of benchmark.
        group : pd.DataFrame
            Index is date, columns are stocks.
        benchmark_price : pd.DataFrame or pd.Series or None
            Price of benchmark.
        mask : pd.DataFrame
            Data cells that should NOT be used.
        can_enter: pd.DataFrame
            Date the security can be traded and BUY.
        can_exit:pd.DataFrame
            Date the security can be traded and SELL.
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
        if price is None and daily_ret is None:
            raise ValueError("One of price / daily_ret must be provided.")
        if price is not None and daily_ret is not None:
            raise ValueError("Only one of price / daily_ret should be provided.")
        if benchmark_price is not None and daily_benchmark_ret is not None:
            raise ValueError("Only one of benchmark_price / daily_benchmark_ret should be provided.")
        if not (n_quantiles > 0 and isinstance(n_quantiles, int)):
            raise ValueError("n_quantiles must be a positive integer. Input is: {}".format(n_quantiles))

        if daily_ret is not None:
            warnings.warn("Warning: 检查到使用daily_ret模式。未避免未来函数，请注意确保daily_ret格式为对应日期能实现的日收益.")

        # ensure inputs are aligned
        if mask is not None:
            try:
                assert np.all(signal.index == mask.index)
                assert np.all(signal.columns == mask.columns)
            except:
                warnings.warn("Warning: signal与mask的index/columns不一致,请检查输入参数!")
                mask = mask.reindex_like(signal)
            mask = jutil.fillinf(mask)
            mask = mask.astype(int).fillna(0).astype(bool)  # dtype of mask could be float. So we need to convert.
        else:
            mask = pd.DataFrame(index=signal.index, columns=signal.columns, data=False)
        if can_enter is not None:
            try:
                assert np.all(signal.index == can_enter.index)
                assert np.all(signal.columns == can_enter.columns)
            except:
                warnings.warn("Warning: signal与can_enter的index/columns不一致,请检查输入参数!")
                can_enter = can_enter.reindex_like(signal)
            can_enter = jutil.fillinf(can_enter)
            can_enter = can_enter.astype(int).fillna(0).astype(
                bool)  # dtype of can_enter could be float. So we need to convert.
        else:
            can_enter = pd.DataFrame(index=signal.index, columns=signal.columns, data=True)
        if can_exit is not None:
            try:
                assert np.all(signal.index == can_exit.index)
                assert np.all(signal.columns == can_exit.columns)
            except:
                warnings.warn("Warning: signal与can_exit的index/columns不一致,请检查输入参数!")
                can_exit = can_exit.reindex_like(signal)
            can_exit = jutil.fillinf(can_exit)
            can_exit = can_exit.astype(int).fillna(0).astype(
                bool)  # dtype of can_exit could be float. So we need to convert.
        else:
            can_exit = pd.DataFrame(index=signal.index, columns=signal.columns, data=True)
        if group is not None:
            try:
                assert np.all(signal.index == group.index)
                assert np.all(signal.columns == group.columns)
            except:
                warnings.warn("Warning: signal与group的index/columns不一致,请检查输入参数!")
                group = group.reindex_like(signal)
            group = group.astype(str)

        # ----------------------------------------------------------------------
        # save data
        self.n_quantiles = n_quantiles
        self.period = period

        # ----------------------------------------------------------------------
        # Get dependent variables

        # 计算benchmark收益
        self.benchmark_ret = None
        if benchmark_price is not None:
            benchmark_price = benchmark_price.reindex(index=signal.index)
            self.benchmark_ret = pfm.price2ret(benchmark_price, self.period, axis=0, compound=True)
        elif daily_benchmark_ret is not None:
            daily_benchmark_ret = daily_benchmark_ret.reindex(index=signal.index)
            self.benchmark_ret = pfm.daily_ret_to_ret(daily_benchmark_ret,self.period)

        # 计算区间持仓收益
        isRealPrice = False
        if daily_ret is not None:
            try:
                assert np.all(signal.index == daily_ret.index)
                assert np.all(signal.columns == daily_ret.columns)
            except:
                warnings.warn("Warning: signal与daily_ret的index/columns不一致,请检查输入参数!")
                daily_ret = daily_ret.reindex_like(signal)
            daily_ret = jutil.fillinf(daily_ret).fillna(0)
            price = pfm.daily_ret_to_cum(daily_ret)
        else:
            # 有price
            isRealPrice=True
            try:
                assert np.all(signal.index == price.index)
                assert np.all(signal.columns == price.columns)
            except:
                warnings.warn("Warning: signal与price的index/columns不一致,请检查输入参数!")
                price = price.reindex_like(signal)
            price = jutil.fillinf(price)

        can_enter = np.logical_and(price != np.NaN, can_enter)
        df_ret = pfm.price2ret(price, period=self.period, axis=0, compound=True)
        price_can_exit = price.copy()
        price_can_exit[~can_exit] = np.NaN
        price_can_exit = price_can_exit.fillna(method="bfill")
        ret_can_exit = pfm.price2ret(price_can_exit, period=self.period, axis=0, compound=True)
        df_ret[~can_exit] = ret_can_exit[~can_exit]

        if self.benchmark_ret is not None:
            # 计算持有期相对收益
            residual_ret = df_ret.sub(self.benchmark_ret.values.flatten(), axis=0)
        else:
            residual_ret = df_ret
        residual_ret = jutil.fillinf(residual_ret)
        residual_ret -= commission

        # 计算潜在上涨空间和潜在下跌空间
        if high is not None and isRealPrice:
            try:
                assert np.all(signal.index == high.index)
                assert np.all(signal.columns == high.columns)
            except:
                warnings.warn("Warning: signal与high的index/columns不一致,请检查输入参数!")
                high = high.reindex_like(signal)
            high = jutil.fillinf(high)
        else:
            high = price
        upside_ret = compute_upside_returns(price, high, can_exit, self.period, compound=True)
        upside_ret = jutil.fillinf(upside_ret)
        upside_ret -= commission

        if low is not None and isRealPrice:
            try:
                assert np.all(signal.index == low.index)
                assert np.all(signal.columns == low.columns)
            except:
                warnings.warn("Warning: signal与low的index/columns不一致,请检查输入参数!")
                low = low.reindex_like(signal)
            low = jutil.fillinf(low)
        else:
            low = price
        downside_ret = compute_downside_returns(price, low, can_exit, self.period, compound=True)
        downside_ret = jutil.fillinf(downside_ret)
        downside_ret -= commission

        # ----------------------------------------------------------------------
        # Get independent varibale
        signal = jutil.fillinf(signal)
        signal = signal.shift(1)  # avoid forward-looking bias
        # forward or not
        if forward:
            # point-in-time signal and forward return
            residual_ret = residual_ret.shift(-self.period)
            upside_ret = upside_ret.shift(-self.period)
            downside_ret = downside_ret.shift(-self.period)
        else:
            # past signal and point-in-time return
            signal = signal.shift(self.period)
            can_enter = can_enter.shift(self.period)
            mask = mask.shift(self.period)

        self.ret = dict()
        self.ret["return"] = residual_ret
        self.ret["upside_ret"] = upside_ret
        self.ret["downside_ret"] = downside_ret

        # ----------------------------------------------------------------------
        # get masks
        # mask_prices = data.isnull()
        # Because we use FORWARD return, if one day's price is broken, the day that is <period> days ago is also broken.
        # mask_prices = np.logical_or(mask_prices, mask_prices.shift(self.period))
        # mask_price_return = residual_ret.isnull()
        mask_signal = signal.isnull()

        mask = np.logical_or(mask.fillna(True), np.logical_or(mask_signal, ~(can_enter.fillna(False))))
        mask = np.logical_or(mask,
                             self.ret["return"].isnull())
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
        # stack
        def stack_td_symbol(df):
            df = pd.DataFrame(df.stack(dropna=False))  # do not dropna
            df.index.names = ['trade_date', 'symbol']
            df.sort_index(axis=0, level=['trade_date', 'symbol'], inplace=True)
            return df

        # ----------------------------------------------------------------------
        # concat signal value
        res = stack_td_symbol(signal)
        res.columns = ['signal']
        for ret_type in self.ret.keys():
            res[ret_type] = stack_td_symbol(self.ret[ret_type]).fillna(0)
        res['quantile'] = stack_td_symbol(df_quantile)
        if group is not None:
            res["group"] = stack_td_symbol(group)
        mask = stack_td_symbol(mask)
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

        file_name = 'event_report'
        if self.signal_name is not None:
            file_name = self.signal_name + "#" + file_name
        self.show_fig(gf.fig, file_name)

        # dic_res['df_res'] = df_res
        return df_all, df_events, df_stats

    @plotting.customize
    def create_returns_report(self):
        """
        Creates a tear sheet for returns analysis of a signal.

        """
        n_quantiles = self.signal_data['quantile'].max()

        # ----------------------------------------------------------------------------------
        # Daily Signal Return Time Series
        # Use regression or weighted average to calculate.
        period_wise_long_ret = \
            pfm.calc_period_wise_weighted_signal_return(self.signal_data, weight_method='long_only')
        period_wise_short_ret = \
            pfm.calc_period_wise_weighted_signal_return(self.signal_data, weight_method='short_only')
        cum_long_ret = pfm.period_wise_ret_to_cum(period_wise_long_ret, period=self.period, compound=True)
        cum_short_ret = pfm.period_wise_ret_to_cum(period_wise_short_ret, period=self.period, compound=True)
        # period_wise_ret_by_regression = perf.regress_period_wise_signal_return(signal_data)
        # period_wise_ls_signal_ret = \
        #     pfm.calc_period_wise_weighted_signal_return(signal_data, weight_method='long_short')
        # daily_ls_signal_ret = pfm.period2daily(period_wise_ls_signal_ret, period=period)
        # ls_signal_ret_cum = pfm.daily_ret_to_cum(daily_ls_signal_ret)

        # ----------------------------------------------------------------------------------
        # Period-wise Quantile Return Time Series
        # We calculate quantile return using equal weight or market value weight.
        # Quantile is already obtained according to signal values.

        # quantile return
        period_wise_quantile_ret_stats = pfm.calc_quantile_return_mean_std(self.signal_data, time_series=True)
        cum_quantile_ret = pd.concat({k: pfm.period_wise_ret_to_cum(v['mean'], period=self.period, compound=True)
                                      for k, v in period_wise_quantile_ret_stats.items()},
                                     axis=1)

        # top quantile minus bottom quantile return
        period_wise_tmb_ret = pfm.calc_return_diff_mean_std(period_wise_quantile_ret_stats[n_quantiles],
                                                            period_wise_quantile_ret_stats[1])
        cum_tmb_ret = pfm.period_wise_ret_to_cum(period_wise_tmb_ret['mean_diff'], period=self.period, compound=True)

        # ----------------------------------------------------------------------------------
        # Alpha and Beta
        # Calculate using regression.
        '''
        weighted_portfolio_alpha_beta
        tmb_alpha_beta =
        '''

        # start plotting
        if self.output_format:
            vertical_sections = 6
            gf = plotting.GridFigure(rows=vertical_sections, cols=1)
            gf.fig.suptitle("Returns Tear Sheet\n\n(compound)\n (period length = {:d} days)".format(self.period))

            plotting.plot_quantile_returns_ts(period_wise_quantile_ret_stats,
                                              ax=gf.next_row())

            plotting.plot_cumulative_returns_by_quantile(cum_quantile_ret,
                                                         ax=gf.next_row())

            plotting.plot_cumulative_return(cum_long_ret,
                                            title="Signal Weighted Long Only Portfolio Cumulative Return",
                                            ax=gf.next_row())

            plotting.plot_cumulative_return(cum_short_ret,
                                            title="Signal Weighted Short Only Portfolio Cumulative Return",
                                            ax=gf.next_row())

            plotting.plot_mean_quantile_returns_spread_time_series(period_wise_tmb_ret, self.period,
                                                                   bandwidth=0.5,
                                                                   ax=gf.next_row())

            plotting.plot_cumulative_return(cum_tmb_ret,
                                            title="Top Minus Bottom (long top, short bottom)"
                                                  "Portfolio Cumulative Return",
                                            ax=gf.next_row())

            file_name = 'returns_report'
            if self.signal_name is not None:
                file_name = self.signal_name+"#"+file_name
            self.show_fig(gf.fig, file_name)

        self.returns_report_data = {'period_wise_quantile_ret': period_wise_quantile_ret_stats,
                                    'cum_quantile_ret': cum_quantile_ret,
                                    'cum_long_ret': cum_long_ret,
                                    'cum_short_ret': cum_short_ret,
                                    'period_wise_tmb_ret': period_wise_tmb_ret,
                                    'cum_tmb_ret': cum_tmb_ret}

    @plotting.customize
    def create_information_report(self):
        """
        Creates a tear sheet for information analysis of a signal.

        """
        ic = pfm.calc_signal_ic(self.signal_data)
        ic.index = pd.to_datetime(ic.index, format="%Y%m%d")
        monthly_ic = pfm.mean_information_coefficient(ic, "M")

        if self.output_format:
            ic_summary_table = pfm.calc_ic_stats_table(ic)
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
            # plotting.plot_ic_qq(ic, ax=ax_ic_hqq[1::2])

            plotting.plot_monthly_ic_heatmap(monthly_ic, period=self.period, ax=gf.next_row())

            file_name = 'information_report'
            if self.signal_name is not None:
                file_name = self.signal_name+"#"+file_name
            self.show_fig(gf.fig, file_name)

        self.ic_report_data = {'daily_ic': ic,
                               'monthly_ic': monthly_ic}
