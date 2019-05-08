import numpy as np
from jaqs_fxdayu.research.signaldigger.plotting import *
from jaqs_fxdayu.research.timingdigger import performance


def plot_event_table(event_summary_table):
    print("Event Analysis")
    plot_table(event_summary_table.apply(lambda x: x.round(3)).T)


def get_entry_exit(signal_data_by_symbol,
                   price,
                   ax=None):

    def trans_t(x):
        value = str(int(x))
        format = '%Y%m%d' if len(value) == 8 else '%Y%m%d%H%M%S'
        pd.to_datetime(value, format=format)
        return pd.to_datetime(value, format=format)

    if ax is None:
        f, ax = plt.subplots(1, 1, figsize=(18, 6))

    tmp = signal_data_by_symbol.copy().reset_index()
    tmp["cum_ret"] = tmp["return"].add(1.0).cumprod()
    symbol = tmp["symbol"].values[0]
    symbol_price = price[[symbol]]
    # # 图片上下界
    # price_max, price_min = symbol_price.values.max(),symbol_price.values.min()
    # gap = price_max - price_min
    # 进出场价位(用于画图)
    tmp["entry"] = symbol_price.loc[tmp["trade_date"]].values
    tmp["exit"] = symbol_price.loc[tmp["exit_time"]].values

    # 价格和净值曲线
    symbol_price["cum_ret"] = np.nan
    symbol_price["cum_ret"].loc[tmp["exit_time"]] = tmp["cum_ret"].values
    symbol_price = symbol_price.fillna(method="ffill").fillna(1)
    symbol_price["time"] = pd.Series(symbol_price.index).apply(lambda x: trans_t(x)).values
    symbol_price = symbol_price.set_index("time")
    symbol_price.plot(secondary_y=["cum_ret"], ax=ax, alpha=0.6)
    ax.set_ylabel('Price')
    ax.right_ax.set_ylabel('Net')

    # 进出点位
    entry = tmp[["entry", "sig_type"]]
    entry["time"] = pd.Series(tmp["trade_date"]).apply(lambda x: trans_t(x)).values
    exit = tmp[["exit"]]
    exit["time"] = pd.Series(tmp["exit_time"]).apply(lambda x: trans_t(x)).values

    entry_long = entry[entry["sig_type"] == "long"]
    entry_short = entry[entry["sig_type"] == "short"]
    if entry_long.size > 0:
        ax.scatter(entry_long["time"].values, entry_long["entry"].values, label="long", c='r', marker='>', linewidths=1)
    if entry_short.size > 0:
        ax.scatter(entry_short["time"].values, entry_short["entry"].values, label="short", c='b', marker='>', linewidths=1)
    ax.scatter(exit["time"].values, exit["exit"].values, label="exit", c='y', marker='<', linewidths=1)

    # 进出场连线
    for _,row in tmp.iterrows():
        x = [trans_t(row["trade_date"]),trans_t(row["exit_time"])]
        y = [row["entry"],row["exit"]]
        if row["return"]>0:
            line_type = "r--"
        else:
            line_type = "g--"
        ax.plot(x,y,line_type,linewidth=1)

    ax.legend(loc='best')
    ax.set(title="Entry Exit Position of %s"%(symbol,),
           xlabel='Datetime')

    ax.yaxis.set_major_formatter(ScalarFormatter())

    return ax,symbol


def plot_mean_ic_heatmap(mean_ic, period, format="M",ax=None):
    """
    Plots a heatmap of the information coefficient or returns by month.

    Parameters
    ----------
    mean_monthly_ic : pd.DataFrame
        The mean monthly IC for N periods forward.

    Returns
    -------
    ax : matplotlib.Axes
        The axes that were plotted on.
    """
    MONTH_MAP = {1: 'Jan',
                 2: 'Feb',
                 3: 'Mar',
                 4: 'Apr',
                 5: 'May',
                 6: 'Jun',
                 7: 'Jul',
                 8: 'Aug',
                 9: 'Sep',
                 10: 'Oct',
                 11: 'Nov',
                 12: 'Dec'}

    num_plots = 1.0

    v_spaces = ((num_plots - 1) // 3) + 1

    if ax is None:
        f, ax = plt.subplots(v_spaces, 3, figsize=(18, v_spaces * 6))
        ax = ax.flatten()

    new_index_y = []
    new_index_x = []
    if format == "D":
        for date in mean_ic.index:
            new_index_x.append(date.day)
            new_index_y.append(str(date.year)+" "+MONTH_MAP[date.month])
        names = ["month","day"]
    else:
        for date in mean_ic.index:
            new_index_y.append(date.year)
            new_index_x.append(MONTH_MAP[date.month])
        names = ["year", "month"]

    mean_ic.index = pd.MultiIndex.from_arrays(
        [new_index_y, new_index_x],
        names=names)

    ic_ = mean_ic['ic'].unstack()
    sns.heatmap(
        ic_,
        annot=True,
        alpha=1.0,
        center=0.0,
        annot_kws={"size": 7},
        linewidths=0.01,
        linecolor='white',
        cmap=cm.get_cmap('RdBu'),
        cbar=False,
        ax=ax)
    ax.set(ylabel='', xlabel='')

    ax.set_title("IC Mean HeatMap".format(period))

    return ax


def plot_quantile_returns_ts(mean_ret_by_q, ax=None):
    """
    Plots mean period wise returns for signal quantiles.

    Parameters
    ----------
    mean_ret_by_q : pd.DataFrame
        DataFrame with quantile, (group) and mean period wise return values.
    ax : matplotlib.Axes, optional
        Axes upon which to plot.

    Returns
    -------
    ax : matplotlib.Axes
        The axes that were plotted on.

    """
    if ax is None:
        f, ax = plt.subplots(1, 1, figsize=(18, 6))

    ret_wide = pd.concat({k: v['mean'] for k, v in mean_ret_by_q.items()}, axis=1)
    format = '%Y%m%d' if len(str(ret_wide.index[0])) == 8 else '%Y%m%d%H%M%S'
    ret_wide.index = pd.to_datetime(ret_wide.index, format=format)
    ret_wide = ret_wide.mul(DECIMAL_TO_PCT)

    ret_wide.plot(lw=1.2, ax=ax, cmap=COLOR_MAP)
    ax.legend(loc='upper left')
    ymin, ymax = ret_wide.min().min(), ret_wide.max().max()
    ax.set(ylabel='Return (%)',
           title="Quantile Return (equal weight within quantile)",
           xlabel='DateTime',
           ylim=(ymin, ymax))

    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.axhline(1.0, linestyle='-', color='black', lw=1)

    return ax


def plot_cumulative_returns_by_quantile(quantile_ret, ax=None):
    """
    Plots the cumulative returns of various signal quantiles.

    Parameters
    ----------
    quantile_ret : int: pd.DataFrame
        Cumulative returns by signal quantile.
    ax : matplotlib.Axes, optional
        Axes upon which to plot.

    Returns
    -------
    ax : matplotlib.Axes
    """

    if ax is None:
        f, ax = plt.subplots(1, 1, figsize=(18, 6))

    cum_ret = quantile_ret
    format = '%Y%m%d' if len(str(cum_ret.index[0])) == 8 else '%Y%m%d%H%M%S'
    cum_ret.index = pd.to_datetime(cum_ret.index, format=format)
    cum_ret = cum_ret.mul(DECIMAL_TO_PCT)

    cum_ret.plot(lw=2, ax=ax, cmap=COLOR_MAP)
    ax.axhline(0.0, linestyle='-', color='black', lw=1)

    ax.legend(loc='upper left')
    ymin, ymax = cum_ret.min().min(), cum_ret.max().max()
    ax.set(ylabel='Cumulative Returns (%)',
           title='Cumulative Return of Each Quantile (equal weight within quantile)',
           xlabel='DateTime',
           ylim=(ymin, ymax))
    perfs = ["total_ret_{:d} = {:.1f}%".format(col, performance.calc_performance_metrics(ser, cum_return=True,
                                                                                         compound=False)['total_ret'])
               for col, ser in cum_ret.iteritems()]
    ax.text(.02, .30,
            '\n'.join(perfs),
            fontsize=12,
            bbox={'facecolor': 'white', 'alpha': 1, 'pad': 5},
            transform=ax.transAxes,
            verticalalignment='top')

    ax.yaxis.set_major_formatter(ScalarFormatter())

    return ax


def plot_mean_quantile_returns_spread_time_series(mean_returns_spread,
                                                  period,
                                                  ax=None):
    """
    Plots mean period wise returns for signal quantiles.

    Parameters
    ----------
    mean_returns_spread : pd.Series
        Series with difference between quantile mean returns by period.
    std_err : pd.Series
        Series with standard error of difference between quantile
        mean returns each period.
    bandwidth : float
        Width of displayed error bands in standard deviations.
    ax : matplotlib.Axes, optional
        Axes upon which to plot.

    Returns
    -------
    ax : matplotlib.Axes
        The axes that were plotted on.
    """

    periods = period
    title = ('Top Minus Bottom Quantile Return'
             .format(periods if periods is not None else ""))

    if ax is None:
        f, ax = plt.subplots(figsize=(18, 6))
    format = '%Y%m%d' if len(str(mean_returns_spread.index[0])) == 8 else '%Y%m%d%H%M%S'
    mean_returns_spread.index = pd.to_datetime(mean_returns_spread.index, format=format)
    mean_returns_spread_bps = mean_returns_spread['mean_diff'] * DECIMAL_TO_PCT

    mean_returns_spread_bps.plot(alpha=0.4, ax=ax, lw=0.7, color='navy')
    mean_returns_spread_bps.rolling(30).mean().plot(color='green',
                                                    alpha=0.7,
                                                    ax=ax)
    ax.axhline(0.0, linestyle='-', color='black', lw=1, alpha=0.8)

    ax.legend(['mean returns spread', '30 moving avg'], loc='upper right')
    ylim = np.nanpercentile(abs(mean_returns_spread_bps.values), 95)
    ax.set(ylabel='Difference In Quantile Mean Return (%)',
           xlabel='',
           title=title,
           ylim=(-ylim, ylim))

    return ax


def plot_cumulative_return(ret, ax=None, title=None):
    """
    Plots the cumulative returns of the returns series passed in.

    Parameters
    ----------
    ret : pd.Series
        Period wise returns of dollar neutral portfolio weighted by signal
        value.
    ax : matplotlib.Axes, optional
        Axes upon which to plot.

    Returns
    -------
    ax : matplotlib.Axes
        The axes that were plotted on.
    """
    if ax is None:
        f, ax = plt.subplots(1, 1, figsize=(18, 6))

    ret = ret.copy()

    cum = ret  # pfm.daily_ret_to_cum(ret)
    format = '%Y%m%d' if len(str(cum.index[0])) == 8 else '%Y%m%d%H%M%S'
    cum.index = pd.to_datetime(cum.index, format=format)
    cum = cum.mul(DECIMAL_TO_PCT)

    cum.plot(ax=ax, lw=3, color='indianred', alpha=1.0)
    ax.axhline(0.0, linestyle='-', color='black', lw=1)

    metrics = performance.calc_performance_metrics(cum, cum_return=True, compound=False)
    ax.text(.85, .30,
            "total_ret = {:.1f}%\nmean(ret). = {:.4f}%\nstd(ret) = {:.4f}\nir = {:.4f}".format(metrics['total_ret'],
                                                                             metrics['mean(ret)'],
                                                                             metrics['std(ret)'],
                                                                             metrics['ir']),
            fontsize=12,
            bbox={'facecolor': 'white', 'alpha': 1, 'pad': 5},
            transform=ax.transAxes,
            verticalalignment='top')
    if title is None:
        title = "Cumulative Return"
    ax.set(ylabel='Cumulative Return (%)',
           title=title,
           xlabel='DateTime')

    return ax

