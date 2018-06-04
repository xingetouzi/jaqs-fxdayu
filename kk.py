import pickle
from jaqs_fxdayu.data import DataView
from jaqs_fxdayu.research import EventDigger

data = pickle.load(open('5', "rb"))[1][2]

data = data.groupby(level=0,group_keys=False).nlargest(10)
data = data.unstack()
columns = [col.replace("XSHG","SH").replace("XSHE","SZ") for col in data.columns]
data.columns = columns
data.index.name = "trade_date"
data = data.loc[20160101:]
data[data>0] = 2

dv = DataView()
dataview_folder = './Factor'
dv.load_dataview(dataview_folder)

# 定义简单出场条件
dv.add_formula("MA5","Ts_Mean(close_adj,5)",is_quarterly=False,add_data=True)
dv.add_formula("MA10","Ts_Mean(close_adj,10)",is_quarterly=False,add_data=True)
dv.add_formula("close_long","If((MA5<=MA10)&&(Delay(MA5>MA10, 1)),1,0)",is_quarterly=False,add_data=True)

ed = EventDigger()
best = 0
param = None
result = []
for stoploss in [None,-0.02,-0.03,-0.04]:
    for stopprofit in [None,0.02,0.03,0.04,0.05]:
        ed.process_signal(
            enter_signal=data, # -2（开空）　2(开多)
            exit_signal=[dv.get_ts("close_long"),], #  -1（平空）　1(平多)
            sig_type="long", # 信号类型 long/short
            price = dv.get_ts("close_adj").reindex_like(data),
            max_holding_period=5, # 最大持有天数 可为空
            stoploss=stoploss, # 止损百分比 负数 可为空
            stopprofit=stopprofit, # 止盈百分比 正数 可为空
            mask=None,
            can_enter=None,
            can_exit=None,
            commission=0.0008
        )
        ed.create_event_report("long")
        result.append(ed.perf["long"])
        if ed.perf["long"].loc["all","win_ratio"]*ed.perf["long"].loc["all","win_mean/loss_mean"]>best:
            best = ed.perf["long"].loc["all","win_ratio"]*ed.perf["long"].loc["all","win_mean/loss_mean"]
            param = "stoploss=%s stopprofit=%s"%(stoploss,stopprofit)
            print(best)
            print(param)
            print(ed.perf["long"])

print(result)