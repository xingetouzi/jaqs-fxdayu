from jaqs_fxdayu.data import DataView
from jaqs_fxdayu.data import RemoteDataService # 远程数据服务类

# step 1 其中，username password分别对应官网注册的账号和序列号
data_config = {
"remote.data.address": "tcp://data.tushare.org:8910",
"remote.data.username": "18566262672",
"remote.data.password": "eyJhbGciOiJIUzI1NiJ9.eyJjcmVhdGVfdGltZSI6IjE1MTI3MDI3NTAyMTIiLCJpc3MiOiJhdXRoMCIsImlkIjoiMTg1NjYyNjI2NzIifQ.O_-yR0zYagrLRvPbggnru1Rapk4kiyAzcwYt2a3vlpM"
}

# step 2
ds = RemoteDataService()
ds.init_from_config(data_config)
dv = DataView()

# step 3
props = {'start_date': 20170501, 'end_date': 20171001, 'universe':'000016.SH',
         'fields': "roe",
         'freq': 1}

dv.init_from_config(props, ds)
dv.prepare_data()
# dv.append_df(dv.get_ts("close").iloc[0:3,:],"aaa")
# print(dv.get_ts("aaa"))
# print(dv.data_q.index)
# print(dv.get_ts("close").index)
# dv.add_formula("aaa","close",is_quarterly=True,add_data=True)
# print(dv.get_ts_quarter("aaa"))
# dv.add_formula("bbb","Delay(close,-1)",is_quarterly=True,add_data=True)
# print(dv.get_ts_quarter("bbb"))
# print(dv.get_ts("close").loc[20170629:])
# print(dv.get_ts("close").shift(-1).loc[20170629:])
# print(dv.get_ts("aaa").loc[20170628:])
# print(dv.get_ts("close").loc[20170628:])
# print(dv.data_d)
dv.add_field('net_cash_flows_oper_act')
dv.add_field('net_profit')
dv.add_field('tot_assets')
ACCA = dv.add_formula('ACCA_1',
                      "(net_cash_flows_oper_act-net_profit)/tot_assets",
                      is_quarterly=True,
                      add_data=True)
# # print(dv.data_d)
print(dv.get_ts('ACCA_1'))