import pandas as pd
from jaqs_fxdayu.patch_util import auto_register_patch

from jaqs.research.signaldigger.performance import calc_ic_stats_table as __calc_ic_stats_stable


@auto_register_patch()
def calc_signal_ic(signal_data, by_group=False):
    """
    Computes the Spearman Rank Correlation based Information Coefficient (IC)
    between signal values and N period forward returns for each period in
    the signal index.

    Parameters
    ----------
    signal_data : pd.DataFrame - MultiIndex
        Index is pd.MultiIndex ['trade_date', 'symbol'], columns = ['signal', 'return', 'quantile']
    by_group : bool
        If True, compute period wise IC separately for each group.
    Returns
    -------
    ic : pd.DataFrame
        Spearman Rank correlation between signal and provided forward returns.

    """

    def src_ic(df):
        _ic = scst.spearmanr(df['signal'], df['return'])[0]
        return _ic

    signal_data = signal_data.copy()

    grouper = ['trade_date']
    if by_group:
        grouper.append('group')

    ic = signal_data.groupby(grouper).apply(src_ic)
    ic = pd.DataFrame(ic)
    ic.columns = ['ic']

    return ic


@auto_register_patch()
def mean_information_coefficient(ic, by_time=None, by_group=False):
    """
    Get the mean information coefficient of specified groups.
    Answers questions like:
    What is the mean IC for each month?
    What is the mean IC for each group for our whole timerange?
    What is the mean IC for for each group, each week?

    Parameters
    ----------
    by_time : str (pd time_rule), optional
        Time window to use when taking mean IC.
        See http://pandas.pydata.org/pandas-docs/stable/timeseries.html
        for available options.
    by_group : bool
        If True, compute period wise IC separately for each group.
    Returns
    -------
    ic : pd.DataFrame
        Mean Spearman Rank correlation between signal and provided
        forward price movement windows.
    """
    grouper = []
    if by_time is not None:
        grouper.append(pd.TimeGrouper(by_time))
    if by_group:
        grouper.append('group')

    if len(grouper) == 0:
        ic = ic.mean()
    else:
        if isinstance(ic.index, pd.MultiIndex):
            ic.index = pd.MultiIndex(levels=[pd.to_datetime(ic.index.levels[0],
                                                            format="%Y%m%d"),
                                             ic.index.levels[1]],
                                     labels=ic.index.labels,
                                     names=ic.index.names)
        else:
            ic.index = pd.to_datetime(ic.index, format="%Y%m%d")
        ic = (ic.reset_index().set_index('trade_date').groupby(grouper).mean())

    return ic


@auto_register_patch()
def calc_quantile_return_mean_std(signal_data, time_series=False):
    """
    Computes mean returns for signal quantiles across
    provided forward returns columns.

    Parameters
    ----------
    signal_data : pd.DataFrame - MultiIndex
        Index is pd.MultiIndex ['trade_date', 'symbol'], columns = ['signal', 'return', 'quantile']
    Returns
    -------
    res : pd.DataFrame of dict

    """
    signal_data = signal_data.copy()
    grouper = ['quantile']
    if time_series:
        grouper.append('trade_date')

    group_mean_std = signal_data.groupby(grouper)['return'].agg(['mean', 'std', 'count'])
    # TODO: why?
    '''
    std_error_ret = group_mean_std.loc[:, 'std'].copy() / np.sqrt(group_mean_std.loc[:, 'count'].copy())
    '''
    indexes = []
    if time_series:
        quantile_daily_mean_std_dic = dict()
        quantiles = np.unique(group_mean_std.index.get_level_values(level='quantile'))
        for q in quantiles:  # loop for different quantiles
            df_q = group_mean_std.loc[pd.IndexSlice[q, :], :]  # bug
            df_q.index = df_q.index.droplevel(level='quantile')
            indexes.append(pd.Series(df_q.index))
            quantile_daily_mean_std_dic[q] = df_q
        new_index = sorted(pd.concat(indexes).unique())
        for q in quantiles:
            quantile_daily_mean_std_dic[q] = quantile_daily_mean_std_dic[q].reindex(new_index).fillna(0)
        return quantile_daily_mean_std_dic
    else:
        return group_mean_std


@auto_register_patch()
def daily_ret_to_cum(df_ret, axis=0):
    cum = df_ret.add(1.0).cumprod(axis=axis)
    return cum


@auto_register_patch()
def daily_ret_to_ret(daily_ret, period=5, axis=0):
    ret = daily_ret.add(1).rolling(period,axis=axis).apply(np.product).sub(1)
    return ret


@auto_register_patch()
def calc_ic_stats_table(ic_data):
    ic_data = ic_data.dropna()
    return __calc_ic_stats_stable(ic_data)


@auto_register_patch()
def price2ret(prices, period=5, axis=None, compound=True):
    """

    Parameters
    ----------
    prices : pd.DataFrame or pd.Series
        Index is datetime.
    period : int
    axis : {0, 1, None}

    Returns
    -------
    ret : pd.DataFrame or pd.Series

    """
    if axis is None:
        kwargs = dict()
    else:
        kwargs = {'axis': axis}

    if compound:
        ret = prices.pct_change(periods=period, **kwargs)
    else:
        ret = prices.diff(periods=period, **kwargs) / prices.iloc[0]
    return ret


@auto_register_patch()
def period_wise_ret_to_cum(ret, period, compound=True):
    """
    Calculate cumulative returns from N-periods returns, no compounding.
    When 'period' N is greater than 1 the cumulative returns plot is computed
    building and averaging the cumulative returns of N interleaved portfolios
    (started at subsequent periods 1,2,3,...,N) each one rebalancing every N
    periods.

    Parameters
    ----------
    ret: pd.Series or pd.DataFrame
        pd.Series containing N-periods returns
    period: integer
        Period for which the returns are computed
    compound : bool
        Whether calculate using compound return.

    Returns
    -------
    pd.Series
        Cumulative returns series starting from zero.

    """
    if isinstance(ret, pd.DataFrame):
        # deal with each column recursively
        return ret.apply(period_wise_ret_to_cum, axis=0, args=(period,))
    elif isinstance(ret, pd.Series):
        if period == 1:
            return ret.add(1).cumprod().sub(1.0)

        # invest in each portfolio separately

        periods_index = np.arange(len(ret.index)) // period
        period_portfolios = ret.groupby(by=periods_index, axis=0).apply(lambda ser: pd.DataFrame(np.diag(ser))).fillna(0)
        period_portfolios.index = ret.index


        # cumulate returns separately
        if compound:
            cum_returns = period_portfolios.add(1).cumprod().sub(1.0)
        else:
            cum_returns = period_portfolios.cumsum()

        # since capital of all portfolios are the same, return in all equals average return
        res = cum_returns.mean(axis=1)

        return res
    else:
        raise NotImplementedError("ret must be Series or DataFrame.")


_calc_signal_ic = calc_signal_ic
_mean_information_coefficient = mean_information_coefficient
_calc_ic_stats_table = calc_ic_stats_table
_calc_quantile_return_mean_std = calc_quantile_return_mean_std
_daily_ret_to_cum = daily_ret_to_cum
_daily_ret_to_ret = daily_ret_to_ret
_price2ret = price2ret
_period_wise_ret_to_cum = period_wise_ret_to_cum

from jaqs.research.signaldigger.performance import *

calc_signal_ic = _calc_signal_ic
mean_information_coefficient = _mean_information_coefficient
calc_quantile_return_mean_std = _calc_quantile_return_mean_std
daily_ret_to_cum = _daily_ret_to_cum
daily_ret_to_ret = _daily_ret_to_ret
price2ret = _price2ret
calc_ic_stats_table = _calc_ic_stats_table
period_wise_ret_to_cum = _period_wise_ret_to_cum
