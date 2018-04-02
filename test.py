from jaqs_fxdayu.data import DataView
from jaqs_fxdayu.data import RemoteDataService # 远程数据服务类

data_config = {
"remote.data.address": "tcp://192.168.0.102:23000",
# "remote.data.address": "tcp://data.tushare.org:8910",
"remote.data.username": "18566262672",
"remote.data.password": "eyJhbGciOiJIUzI1NiJ9.eyJjcmVhdGVfdGltZSI6IjE1MTI3MDI3NTAyMTIiLCJpc3MiOiJhdXRoMCIsImlkIjoiMTg1NjYyNjI2NzIifQ.O_-yR0zYagrLRvPbggnru1Rapk4kiyAzcwYt2a3vlpM",
"timeout":1800,
}
# step 2
ds = RemoteDataService()
ds.init_from_config(data_config)
dv = DataView()

# step 3
props = {'start_date': 20170501, 'end_date': 20171001, 'universe':'000300.SH',
         "all_price":False,
         "adjust_mode":None,
         'fields': "pb,pe,total_oper_rev,oper_exp,close",
         'freq': 1}

dv.init_from_config(props, ds)
dv.prepare_data()
print(dv.fields)
print(dv.get_ts("close").head())
print(dv.get_ts("close_adj").head())