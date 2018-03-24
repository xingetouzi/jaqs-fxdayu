# encoding = utf-8

import numpy as np
import pandas as pd
import scipy.stats as scst
from jaqs.trade import common

from . import performance as pfm


def compute_downside_returns(price,
                             low,
                             can_exit=None,
                             period=5,
                             compound=True):
    """
    Finds the N period downside_returns for each asset provided.

    Parameters
    ----------
    price : pd.DataFrame
        Pricing data to use in forward price calculation.
        Assets as columns, dates as index. Pricing data must
        span the factor analysis time period plus an additional buffer window
        that is greater than the maximum number of expected periods
        in the forward returns calculations.
    low : pd.DataFrame
        Low pricing data to use in forward price calculation.
        Assets as columns, dates as index. Pricing data must
        span the factor analysis time period plus an additional buffer window
        that is greater than the maximum number of expected periods
        in the forward returns calculations.
    can_exit:bool
        shape like price&low
    period : int
        periods to compute returns on.
    compound : bool


    Returns
    -------
    downside_returns : pd.DataFrame
        downside_returns in indexed by date
    """
    if compound:
        downside_ret = (low.rolling(period).min() - price.shift(period)) / price.shift(period)
    else:
        downside_ret = (low.rolling(period).min() - price.shift(period)) / price.iloc[0]
    if can_exit is not None:
        low_can_exit = low.copy()
        low_can_exit[~can_exit] = np.NaN
        low_can_exit = low_can_exit.fillna(method="bfill")
        if compound:
            downside_ret_can_exit = (low_can_exit.rolling(period).min() - price.shift(period)) / price.shift(period)
        else:
            downside_ret_can_exit = (low_can_exit.rolling(period).min() - price.shift(period)) / price.iloc[0]
        downside_ret[~can_exit] = (downside_ret[downside_ret <= downside_ret_can_exit].fillna(0) + \
                                   downside_ret_can_exit[downside_ret_can_exit < downside_ret].fillna(0))[~can_exit]

    return downside_ret


def compute_upside_returns(price,
                           high,
                           can_exit=None,
                           period=5,
                           compound=True):
    """
    Finds the N period upside_returns for each asset provided.

    Parameters
    ----------
    price : pd.DataFrame
        Pricing data to use in forward price calculation.
        Assets as columns, dates as index. Pricing data must
        span the factor analysis time period plus an additional buffer window
        that is greater than the maximum number of expected periods
        in the forward returns calculations.
    high : pd.DataFrame
        High pricing data to use in forward price calculation.
        Assets as columns, dates as index. Pricing data must
        span the factor analysis time period plus an additional buffer window
        that is greater than the maximum number of expected periods
        in the forward returns calculations.
    can_exit:bool
        shape like price&low
    period : int
        periods to compute returns on.
    compound : bool


    Returns
    -------
    upside_returns : pd.DataFrame
        upside_returns in indexed by date
    """
    if compound:
        upside_ret = (high.rolling(period).max() - price.shift(period)) / price.shift(period)
    else:
        upside_ret = (high.rolling(period).max() - price.shift(period)) / price.iloc[0]
    if can_exit is not None:
        high_can_exit = high.copy()
        high_can_exit[~can_exit] = np.NaN
        high_can_exit = high_can_exit.fillna(method="bfill")
        if compound:
            upside_ret_can_exit = (high_can_exit.rolling(period).max() - price.shift(period)) / price.shift(period)
        else:
            upside_ret_can_exit = (high_can_exit.rolling(period).max() - price.shift(period)) / price.iloc[0]
        upside_ret[~can_exit] = (upside_ret[upside_ret >= upside_ret_can_exit].fillna(0) + \
                                 upside_ret_can_exit[upside_ret_can_exit > upside_ret].fillna(0))[~can_exit]

    return upside_ret


def cal_rets_stats(rets, period):
    ret_summary_table = pd.DataFrame()
    ratio = (1.0 * common.CALENDAR_CONST.TRADE_DAYS_PER_YEAR / period)
    mean = rets.mean()
    std = rets.std()
    annual_ret, annual_vol = mean * ratio, std * np.sqrt(ratio)
    t_stats, p_values = scst.ttest_1samp(rets, np.zeros(rets.shape[1]), axis=0)
    ret_summary_table['t-stat'] = t_stats
    ret_summary_table['p-value'] = np.round(p_values, 5)
    ret_summary_table["skewness"] = scst.skew(rets, axis=0)
    ret_summary_table["kurtosis"] = scst.kurtosis(rets, axis=0)
    ret_summary_table['Ann. Ret'] = annual_ret
    ret_summary_table['Ann. Vol'] = annual_vol
    ret_summary_table['Ann. IR'] = annual_ret / annual_vol
    ret_summary_table['occurance'] = len(rets)
    return ret_summary_table.T


def ic_stats(signal_data):
    ICs = get_ics(signal_data)
    stats = []
    for item in ICs.keys():
        ic = ICs[item]
        ic.index = pd.to_datetime(ic.index, format="%Y%m%d")
        ic_summary_table = pfm.calc_ic_stats_table(ic).T
        ic_summary_table.columns = [item]
        stats.append(ic_summary_table)
    if len(stats) > 0:
        stats = pd.concat(stats, axis=1)
    return stats


def get_ics(signal_data):
    ICs = dict()
    if not ("upside_ret" in signal_data.columns) or \
            not ("downside_ret" in signal_data.columns):
        items = ["return"]
    else:
        items = ["return", "upside_ret", "downside_ret"]
    for item in items:
        data = signal_data[["signal", item]]
        data.columns = ["signal", "return"]
        ICs[item + "_ic"] = pfm.calc_signal_ic(data).dropna()

    return ICs


def return_stats(signal_data, is_event, period):
    rets = get_rets(signal_data, is_event)
    stats = []
    for ret_type in rets.keys():
        if len(rets[ret_type]) > 0:
            ret_stats = cal_rets_stats(rets[ret_type].values.reshape((-1, 1)), period)
            ret_stats.columns = [ret_type]
            stats.append(ret_stats)
    if len(stats) > 0:
        stats = pd.concat(stats, axis=1)
    return stats


def get_rets(signal_data, is_event):
    rets = dict()
    signal_data = signal_data.copy()
    n_quantiles = signal_data['quantile'].max()

    if is_event:
        rets["long_ret"] = signal_data[signal_data['signal'] == 1]["return"].dropna()
        rets['short_ret'] = signal_data[signal_data['signal'] == -1]["return"].dropna() * -1
    else:
        rets['long_ret'] = \
            pfm.calc_period_wise_weighted_signal_return(signal_data, weight_method='long_only').dropna()
        rets['short_ret'] = \
            pfm.calc_period_wise_weighted_signal_return(signal_data, weight_method='short_only').dropna()
    rets['long_short_ret'] = \
        pfm.calc_period_wise_weighted_signal_return(signal_data, weight_method='long_short').dropna()
    # quantile return
    if not is_event:
        rets['top_quantile_ret'] = signal_data[signal_data['quantile'] == n_quantiles]["return"].dropna()
        rets['bottom_quantile_ret'] = signal_data[signal_data['quantile'] == 1]["return"].dropna()
        period_wise_quantile_ret_stats = pfm.calc_quantile_return_mean_std(signal_data, time_series=True)
        rets['tmb_ret'] = pfm.calc_return_diff_mean_std(period_wise_quantile_ret_stats[n_quantiles],
                                                        period_wise_quantile_ret_stats[1])['mean_diff'].dropna()
    rets['all_sample_ret'] = signal_data["return"].dropna()
    return rets


def weighted_signal_ret_space(signal_data):
    """
    Computes period wise period_wise_returns for portfolio weighted by signal
    values. Weights are computed by demeaning signals and dividing
    by the sum of their absolute value (achieving gross leverage of 1).

    Parameters
    ----------
    signal_data : pd.DataFrame - MultiIndex
        Index is pd.MultiIndex ['trade_date', 'symbol'], columns = ['signal', 'return', "upside_ret","downside_ret", 'quantile']

    Returns
    -------
    space : pd.DataFrame of dict
        weighted_signal_ret_space
    """

    def calc_norm_weights(ser, method):
        if method == 'long_only':
            ser = (ser + ser.abs()) / 2.0
        elif method == 'short_only':
            ser = (ser - ser.abs()) / 2.0
        else:
            raise ValueError("method can only be long_only or short_only,"
                             "but [{}] is provided".format(method))
        return ser / ser.abs().sum()

    grouper = ['trade_date']

    long_weights = signal_data.groupby(grouper)['signal'].apply(calc_norm_weights, "long_only")
    short_weights = signal_data.groupby(grouper)['signal'].apply(calc_norm_weights, "short_only")

    space = dict()
    space["long_space"] = dict()
    space["long_space"]["upside_space"] = signal_data['upside_ret'].multiply(long_weights, axis=0)
    space["long_space"]["downside_space"] = signal_data['downside_ret'].multiply(long_weights, axis=0)
    space["short_space"] = dict()
    space["short_space"]["upside_space"] = signal_data['downside_ret'].multiply(short_weights, axis=0)
    space["short_space"]["downside_space"] = signal_data['upside_ret'].multiply(short_weights, axis=0)
    space["long_short_space"] = dict()
    space["long_short_space"]["upside_space"] = space["long_space"]["upside_space"] + space["short_space"][
        "upside_space"]
    space["long_short_space"]["downside_space"] = space["long_space"]["downside_space"] + space["short_space"][
        "downside_space"]

    for dir_type in ["long_space", "short_space", "long_short_space"]:
        for space_type in ["upside_space", "downside_space"]:
            space[dir_type][space_type] = space[dir_type][space_type].groupby(level='trade_date').sum()
            space[dir_type][space_type] = pd.DataFrame(space[dir_type][space_type]).dropna()

    return space


def calc_tb_quantile_ret_space_mean_std(signal_data,
                                        space_type="upside"):
    """
    Computes mean space for signal top & bottom quantiles across
    provided upside_ret or downside_ret.

    Parameters
    ----------
    signal_data : pd.DataFrame - MultiIndex
        Index is pd.MultiIndex ['trade_date', 'symbol'], columns = ['signal', 'return', 'upside_ret', "downside_ret", 'quantile']

    Returns
    -------
    quantile_space : pd.DataFrame of dict

    """
    signal_data = signal_data.copy()
    n_quantiles = signal_data['quantile'].max()
    grouper = ['quantile']
    grouper.append('trade_date')

    group_mean_std = signal_data.groupby(grouper)[space_type + "_ret"].agg(['mean', 'std', 'count'])
    indexes = []
    quantile_daily_mean_std_dic = dict()
    for q in [1, n_quantiles]:  # loop for different quantiles
        df_q = group_mean_std.loc[pd.IndexSlice[q, :], :]  # bug
        df_q.index = df_q.index.droplevel(level='quantile')
        indexes.append(pd.Series(df_q.index))
        quantile_daily_mean_std_dic[q] = df_q
    new_index = sorted(pd.concat(indexes).unique())
    for q in [1, n_quantiles]:
        quantile_daily_mean_std_dic[q] = quantile_daily_mean_std_dic[q].reindex(new_index).fillna(0)
    return quantile_daily_mean_std_dic


def cal_spaces_stats(space):
    space_summary_table = pd.DataFrame()
    if len(space["upside_space"]) > 0:
        space["Up_sp"] = space["upside_space"].values.reshape((-1, 1))
        space["Down_sp"] = space["downside_space"].values.reshape((-1, 1))
        for space_type in ["Up_sp", "Down_sp"]:
            mean = space[space_type].mean()
            std = space[space_type].std()
            space_summary_table[space_type + " Mean"] = [mean]
            space_summary_table[space_type + " Std"] = [std]
            space_summary_table[space_type + " IR"] = [mean / std]
            for percent in [5, 25, 50, 75, 95]:
                space_summary_table[space_type + " Pct" + str(percent)] = [np.percentile(space[space_type],
                                                                                         percent)]
            space_summary_table[space_type + ' Occur'] = [len(space[space_type])]
    return space_summary_table.T


def space_stats(signal_data, is_event):
    spaces = get_spaces(signal_data, is_event)
    stats_result = []
    for dir_type in spaces.keys():
        stats = cal_spaces_stats(spaces[dir_type])
        if len(stats) > 0:
            stats.columns = [dir_type]
            stats_result.append(stats)
    if len(stats_result) > 0:
        stats_result = pd.concat(stats_result, axis=1)
    return stats_result


def get_spaces(signal_data, is_event):
    spaces = dict()
    if not ("upside_ret" in signal_data.columns) or \
            not ("downside_ret" in signal_data.columns):
        return spaces
    signal_data = signal_data.copy()
    n_quantiles = signal_data['quantile'].max()

    spaces = weighted_signal_ret_space(signal_data)
    if is_event:
        spaces["long_space"]["upside_space"] = signal_data[signal_data['signal'] == 1]["upside_ret"].dropna()
        spaces["long_space"]["downside_space"] = signal_data[signal_data['signal'] == 1]["downside_ret"].dropna()
        spaces["short_space"]["upside_space"] = signal_data[signal_data['signal'] == -1]["downside_ret"].dropna() * -1
        spaces["short_space"]["downside_space"] = signal_data[signal_data['signal'] == -1]["upside_ret"].dropna() * -1

    # quantile return space
    if not is_event:
        spaces["top_quantile_space"] = dict()
        spaces["bottom_quantile_space"] = dict()
        spaces["tmb_space"] = dict()

        spaces["top_quantile_space"]["upside_space"] = signal_data[signal_data['quantile'] == n_quantiles][
            "upside_ret"].dropna()
        spaces["top_quantile_space"]["downside_space"] = signal_data[signal_data['quantile'] == n_quantiles][
            "downside_ret"].dropna()
        spaces["bottom_quantile_space"]["upside_space"] = signal_data[signal_data['quantile'] == 1][
            "upside_ret"].dropna()
        spaces["bottom_quantile_space"]["downside_space"] = signal_data[signal_data['quantile'] == 1][
            "downside_ret"].dropna()

        tb_upside_mean_space = calc_tb_quantile_ret_space_mean_std(signal_data,
                                                                   space_type="upside")
        tb_downside_mean_space = calc_tb_quantile_ret_space_mean_std(signal_data,
                                                                     space_type="downside")
        spaces['tmb_space']["upside_space"] = pfm.calc_return_diff_mean_std(tb_upside_mean_space[n_quantiles],
                                                                            tb_downside_mean_space[1])[
            'mean_diff'].dropna()
        spaces['tmb_space']["downside_space"] = pfm.calc_return_diff_mean_std(tb_downside_mean_space[n_quantiles],
                                                                              tb_upside_mean_space[1])[
            'mean_diff'].dropna()

    spaces["all_sample_space"] = dict()
    spaces["all_sample_space"]["upside_space"] = signal_data["upside_ret"].dropna()
    spaces["all_sample_space"]["downside_space"] = signal_data["downside_ret"].dropna()
    return spaces


def analysis(signal_data, is_event, period):
    if is_event:
        return {
            "ret": return_stats(signal_data, True, period),
            "space": space_stats(signal_data, True)
        }
    else:
        return {
            "ic": ic_stats(signal_data),
            "ret": return_stats(signal_data, False, period),
            "space": space_stats(signal_data, False)
        }
