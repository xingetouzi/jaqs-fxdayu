
# 介绍
针对A股因子研究和交易分析场景，提供了常用的小工具，如查询历史的交易日，历史的行业分类表等


```python
import warnings
warnings.filterwarnings('ignore')
```


```python
data_config = {
"remote.data.address": "tcp://data.tushare.org:8910",
"remote.data.username": "18566262672",
"remote.data.password": "eyJhbGciOiJIUzI1NiJ9.eyJjcmVhdGVfdGltZSI6IjE1MTI3MDI3NTAyMTIiLCJpc3MiOiJhdXRoMCIsImlkIjoiMTg1NjYyNjI2NzIifQ.O_-yR0zYagrLRvPbggnru1Rapk4kiyAzcwYt2a3vlpM"
}

from jaqs_fxdayu.data import DataApi

api = DataApi(data_config["remote.data.address"]) # 传入连接到的远端数据服务器的tcp地址
api.login(username=data_config["remote.data.username"],
          password=data_config["remote.data.password"])
```




    ('username: 18566262672', '0,')



## trade_days
- ` jaqs_fxdayu.utils.dp.trade_days(api, start, end) `

**简要描述：**

- 返回起止日期间的交易日

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|api |是| jaqs.data.DataApi |jaqs.data.DataApi|
|start |是|int |开始日期|
|end |是|int |结束日期|

**返回:**

起止日期间的交易日

**示例：**


```python
from jaqs_fxdayu.utils.dp import trade_days
trade_days(api, 20170101, 20180101)
```




    Int64Index([20170103, 20170104, 20170105, 20170106, 20170109, 20170110,
                20170111, 20170112, 20170113, 20170116,
                ...
                20171218, 20171219, 20171220, 20171221, 20171222, 20171225,
                20171226, 20171227, 20171228, 20171229],
               dtype='int64', name='trade_date', length=244)



## index_cons
- ` jaqs_fxdayu.utils.dp.index_cons(api, index_code, start, end) `

**简要描述：**

- 获得某个指数起止时间段的历史成分股信息

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|api |是| jaqs.data.DataApi |jaqs.data.DataApi|
|index_code |是| str |指数代码|
|start |是|int |开始日期|
|end |是|int |结束日期|

**返回:**

某个指数起止时间段的历史成分股信息

- 其中 in_date:纳入该指数的时间；out_date:从该指数移除的时间

**示例：**


```python
from jaqs_fxdayu.utils.dp import index_cons
index_cons(api, "000300.SH", 20170101, 20170501).head()
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>in_date</th>
      <th>index_code</th>
      <th>out_date</th>
      <th>symbol</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>20050408</td>
      <td>000300.SH</td>
      <td>99999999</td>
      <td>000001.SZ</td>
    </tr>
    <tr>
      <th>1</th>
      <td>20050408</td>
      <td>000300.SH</td>
      <td>99999999</td>
      <td>000002.SZ</td>
    </tr>
    <tr>
      <th>2</th>
      <td>20161212</td>
      <td>000300.SH</td>
      <td>99999999</td>
      <td>000008.SZ</td>
    </tr>
    <tr>
      <th>3</th>
      <td>20050408</td>
      <td>000300.SH</td>
      <td>20171208</td>
      <td>000009.SZ</td>
    </tr>
    <tr>
      <th>4</th>
      <td>20140616</td>
      <td>000300.SH</td>
      <td>20170609</td>
      <td>000027.SZ</td>
    </tr>
  </tbody>
</table>
</div>



## daily_index_cons
- ` jaqs_fxdayu.utils.dp.daily_index_cons(api, index_code, start, end) `

**简要描述：**

- 指定起止时间段，成分股是否还在某指数当中

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|api |是| jaqs.data.DataApi |jaqs.data.DataApi|
|index_code |是| str |指数代码|
|start |是|int |开始日期|
|end |是|int |结束日期|

**示例：**


```python
from jaqs_fxdayu.utils.dp import daily_index_cons
daily_index_cons(api, "000300.SH", 20170101, 20170501).head()
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>000001.SZ</th>
      <th>000002.SZ</th>
      <th>000008.SZ</th>
      <th>000009.SZ</th>
      <th>000027.SZ</th>
      <th>000039.SZ</th>
      <th>000060.SZ</th>
      <th>000061.SZ</th>
      <th>000063.SZ</th>
      <th>000069.SZ</th>
      <th>...</th>
      <th>601933.SH</th>
      <th>601939.SH</th>
      <th>601958.SH</th>
      <th>601985.SH</th>
      <th>601988.SH</th>
      <th>601989.SH</th>
      <th>601998.SH</th>
      <th>603000.SH</th>
      <th>603885.SH</th>
      <th>603993.SH</th>
    </tr>
    <tr>
      <th>trade_date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>20170103</th>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
    </tr>
    <tr>
      <th>20170104</th>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
    </tr>
    <tr>
      <th>20170105</th>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
    </tr>
    <tr>
      <th>20170106</th>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
    </tr>
    <tr>
      <th>20170109</th>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 301 columns</p>
</div>



## daily_sec_industry
- ` jaqs_fxdayu.utils.dp.daily_sec_industry(api, symbol, start, end, source="sw", value="industry1_code") `

**简要描述：**

- 指定起始时间段，查询某一系列股票在该时间段下的行业分类信息

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|api |是| jaqs.data.DataApi |jaqs.data.DataApi|
|symbol |是| str |股票代码，用","隔开。如"600000.SH,000001.SZ"|
|start |是|int |开始日期|
|end |是|int |结束日期|
|source |否|str |行业分类标准，目前仅支持"sw"(申万),"zz"(中证),"zjh"（证监会）,默认"sw"|
|value |否|str |行业等级，形式可为"industry?_code"(行业编码)/"industry?_name"(行业名称)。其中"?"可为1,2,3,4,分别代表1-4个行业等级。申万支持1-4,中证支持1-2。默认为industry1_code|

**示例：**


```python
from jaqs_fxdayu.utils.dp import daily_sec_industry
symbol_id = index_cons(api, "000300.SH", 20170501, 20171001,)["symbol"].dropna()
symbols = ",".join(symbol_id)
group = daily_sec_industry(api, symbols, 20170501, 20171001, source='zjh', value="industry1_name")
group.tail()
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>000001.SZ</th>
      <th>000002.SZ</th>
      <th>000008.SZ</th>
      <th>000009.SZ</th>
      <th>000027.SZ</th>
      <th>000039.SZ</th>
      <th>000060.SZ</th>
      <th>000061.SZ</th>
      <th>000063.SZ</th>
      <th>000069.SZ</th>
      <th>...</th>
      <th>601988.SH</th>
      <th>601989.SH</th>
      <th>601992.SH</th>
      <th>601997.SH</th>
      <th>601998.SH</th>
      <th>603000.SH</th>
      <th>603160.SH</th>
      <th>603858.SH</th>
      <th>603885.SH</th>
      <th>603993.SH</th>
    </tr>
    <tr>
      <th>trade_date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>20170925</th>
      <td>金融业</td>
      <td>房地产业</td>
      <td>制造业</td>
      <td>综合</td>
      <td>电力、热力、燃气及水生产和供应业</td>
      <td>制造业</td>
      <td>制造业</td>
      <td>租赁和商务服务业</td>
      <td>制造业</td>
      <td>水利、环境和公共设施管理业</td>
      <td>...</td>
      <td>金融业</td>
      <td>制造业</td>
      <td>制造业</td>
      <td>金融业</td>
      <td>金融业</td>
      <td>信息传输、软件和信息技术服务业</td>
      <td>制造业</td>
      <td>制造业</td>
      <td>交通运输、仓储和邮政业</td>
      <td>采矿业</td>
    </tr>
    <tr>
      <th>20170926</th>
      <td>金融业</td>
      <td>房地产业</td>
      <td>制造业</td>
      <td>综合</td>
      <td>电力、热力、燃气及水生产和供应业</td>
      <td>制造业</td>
      <td>制造业</td>
      <td>租赁和商务服务业</td>
      <td>制造业</td>
      <td>水利、环境和公共设施管理业</td>
      <td>...</td>
      <td>金融业</td>
      <td>制造业</td>
      <td>制造业</td>
      <td>金融业</td>
      <td>金融业</td>
      <td>信息传输、软件和信息技术服务业</td>
      <td>制造业</td>
      <td>制造业</td>
      <td>交通运输、仓储和邮政业</td>
      <td>采矿业</td>
    </tr>
    <tr>
      <th>20170927</th>
      <td>金融业</td>
      <td>房地产业</td>
      <td>制造业</td>
      <td>综合</td>
      <td>电力、热力、燃气及水生产和供应业</td>
      <td>制造业</td>
      <td>制造业</td>
      <td>租赁和商务服务业</td>
      <td>制造业</td>
      <td>水利、环境和公共设施管理业</td>
      <td>...</td>
      <td>金融业</td>
      <td>制造业</td>
      <td>制造业</td>
      <td>金融业</td>
      <td>金融业</td>
      <td>信息传输、软件和信息技术服务业</td>
      <td>制造业</td>
      <td>制造业</td>
      <td>交通运输、仓储和邮政业</td>
      <td>采矿业</td>
    </tr>
    <tr>
      <th>20170928</th>
      <td>金融业</td>
      <td>房地产业</td>
      <td>制造业</td>
      <td>综合</td>
      <td>电力、热力、燃气及水生产和供应业</td>
      <td>制造业</td>
      <td>制造业</td>
      <td>租赁和商务服务业</td>
      <td>制造业</td>
      <td>水利、环境和公共设施管理业</td>
      <td>...</td>
      <td>金融业</td>
      <td>制造业</td>
      <td>制造业</td>
      <td>金融业</td>
      <td>金融业</td>
      <td>信息传输、软件和信息技术服务业</td>
      <td>制造业</td>
      <td>制造业</td>
      <td>交通运输、仓储和邮政业</td>
      <td>采矿业</td>
    </tr>
    <tr>
      <th>20170929</th>
      <td>金融业</td>
      <td>房地产业</td>
      <td>制造业</td>
      <td>综合</td>
      <td>电力、热力、燃气及水生产和供应业</td>
      <td>制造业</td>
      <td>制造业</td>
      <td>租赁和商务服务业</td>
      <td>制造业</td>
      <td>水利、环境和公共设施管理业</td>
      <td>...</td>
      <td>金融业</td>
      <td>制造业</td>
      <td>制造业</td>
      <td>金融业</td>
      <td>金融业</td>
      <td>信息传输、软件和信息技术服务业</td>
      <td>制造业</td>
      <td>制造业</td>
      <td>交通运输、仓储和邮政业</td>
      <td>采矿业</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>


