from jaqs_fxdayu.research.signaldigger.performance import *


def cal_return_stats(ret):
    if isinstance(ret,pd.Series) or isinstance(ret,pd.DataFrame):
        ret = ret.values
    ret = ret.reshape(-1,1)
    summary_table = pd.DataFrame()
    if len(ret)==0:
        return pd.DataFrame(data=np.nan,
                            columns=['t-stat','p-value',"mean","std","info_ratio",
                                     "skewness","kurtosis","pct5","pct25","pct50",
                                     "pct75","pct95","occurance"],
                            index=[0])
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


def calc_performance_metrics(ser, cum_return=False, compound=False):
    """
    Calculate annualized return, volatility and sharpe.
    We assumed data frequency to be day.

    Parameters
    ----------
    ser : pd.DataFrame or pd.Series
        Index is int date, values are floats.
        ser should start from 0.
    cum_return : bool
        Whether ser is cumulative or daily return.
    compound
        Whether calculation of return is compound.

    Returns
    -------
    res : dict

    """
    if isinstance(ser, pd.DataFrame):
        ser = ser.iloc[:, 0]
    if cum_return:
        cum_ret = ser
        ret = cum2ret(cum_ret, period=1, compound=compound)
    else:
        ret = ser
        cum_ret = ret2cum(ret, compound=compound)

    total_ret = cum_ret.iat[-1]
    std = np.std(ret)
    mean = np.mean(ret)
    res = {'total_ret': total_ret,
           'std(ret)': std,
           'mean(ret)':mean,
           'ir': mean/std}
    return res

