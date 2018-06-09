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
    entry = symbol_price.loc[tmp["trade_date"]]
    exit = symbol_price.loc[tmp["exit_time"]]
    entry["time"] = pd.Series(entry.index).apply(lambda x:trans_t(x)).values
    exit["time"] = pd.Series(exit.index).apply(lambda x:trans_t(x)).values
    symbol_price["time"] = pd.Series(symbol_price.index).apply(lambda x:trans_t(x)).values

    symbol_price["cum_ret"] = np.nan
    symbol_price["cum_ret"].loc[tmp["exit_time"]] = tmp["cum_ret"].values
    symbol_price = symbol_price.fillna(method="ffill")
    symbol_price = symbol_price.set_index("time")

    symbol_price.plot(secondary_y=["cum_ret"], ax=ax)
    ax.set_ylabel('Price')
    ax.right_ax.set_ylabel('Net')

    ax.scatter(entry["time"].values, entry[symbol].values, label="entry", c='r', marker='^', linewidths=3)
    ax.scatter(exit["time"].values, exit[symbol].values, label="exit", c='g', marker='v', linewidths=3)
    ax.legend(loc='best')
    ax.set(title="Entry Exit Position of %s"%(symbol,),
           xlabel='Datetime')

    ax.yaxis.set_major_formatter(ScalarFormatter())

    return ax,symbol
