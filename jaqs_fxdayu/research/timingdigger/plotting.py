import numpy as np
from jaqs_fxdayu.research.signaldigger.plotting import *


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
