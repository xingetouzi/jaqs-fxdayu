import pandas as pd
import numpy as np
import scipy.stats as scst


def daily_ret_to_cum(df_ret, axis=0):
    cum = df_ret.add(1.0).cumprod(axis=axis)
    return cum


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


def cal_return_stats(ret):
    if isinstance(ret,pd.Series) or isinstance(ret,pd.DataFrame):
        ret = ret.values
    ret = ret.reshape(-1,1)
    summary_table = pd.DataFrame()

    t_stats, p_values = scst.ttest_1samp(ret, np.zeros(ret.shape[1]), axis=0)

    summary_table['t-stat'] = t_stats
    summary_table['p-value'] = np.round(p_values, 5)
    summary_table["mean"] = ret.mean()
    summary_table["std"] = ret.std()
    summary_table["info_ratio"] =summary_table["mean"]/summary_table["std"]
    summary_table["skewness"] = scst.skew(ret, axis=0)
    summary_table["kurtosis"] = scst.kurtosis(ret, axis=0)
    for percent in [5, 25, 50, 75, 95]:
        summary_table["pct" + str(percent)] = np.percentile(ret,percent)
    summary_table["occurance"] = len(ret)

    return summary_table

