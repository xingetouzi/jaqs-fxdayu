from jaqs_fxdayu.research import EventDigger
import warnings
import os
warnings.filterwarnings('ignore')
from jaqs_fxdayu.data import DataView
from jaqs_fxdayu.data import RemoteDataService # 远程数据服务类

##################################################################
data_config = {
"remote.data.address": "tcp://192.168.0.101:23000",
"remote.data.username": "18566262672",
"remote.data.password": "eyJhbGciOiJIUzI1NiJ9.eyJjcmVhdGVfdGltZSI6IjE1MTI3MDI3NTAyMTIiLCJpc3MiOiJhdXRoMCIsImlkIjoiMTg1NjYyNjI2NzIifQ.O_-yR0zYagrLRvPbggnru1Rapk4kiyAzcwYt2a3vlpM"
}

# step 2
ds = RemoteDataService()
ds.init_from_config(data_config)
dv = DataView()
dataview_folder = './Factor'
if not (os.path.isdir(dataview_folder)):
    os.makedirs(dataview_folder)

# step 3
props = {'start_date': 20170101, 'end_date': 20171010, 'universe':'000300.SH',
         'fields': "close,open",
         "all_price":False,
         'freq': 1}

dv.init_from_config(props, ds)
dv.prepare_data()
dv.save_dataview(dataview_folder)  # 保存数据文件到指定路径，方便下次直接加载

#########################################################################
dv.load_dataview(dataview_folder)

dv.add_formula("MA3","Ts_Mean(close_adj,3)",is_quarterly=False,add_data=True)
dv.add_formula("MA5","Ts_Mean(close_adj,5)",is_quarterly=False,add_data=True)
dv.add_formula("long","If((MA3>=MA5)&&(Delay(MA3<MA5, 1)),2,0)",is_quarterly=False, add_data=True)
dv.add_formula("short","If((MA3<=MA5)&&(Delay(MA3>MA5, 1)),-2,0)",is_quarterly=False, add_data=True)
dv.add_formula("close_long","If(short==-2,1,0)",is_quarterly=False,add_data=True)
dv.add_formula("close_short","If(long==2,-1,0)",is_quarterly=False,add_data=True)

ed = EventDigger()
ed.process_signal(
    enter_signal=dv.get_ts("long"),  # -2（开空）　2(开多)
    exit_signal=[dv.get_ts("close_long"), ],  # -1（平空）　1(平多)
    sig_type="long",  # 信号类型 long/short
    price=dv.get_ts("close_adj"),
    max_holding_period=5,  # 最大持有天数 可为空
    stoploss=-0.01,  # 止损百分比 负数 可为空
    stopprofit=0.02,  # 止盈百分比 正数 可为空
    ###########
    # 以下参数和signalDigger一样
    mask=None,
    can_enter=None,
    can_exit=None,
    commission=0.0008
)
print(ed.signal_data["long"])
ed.create_full_report()
print(ed.perf["long"])



