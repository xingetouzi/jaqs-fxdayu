
# Dataview

## 介绍
dataview可视为一个基于pandas实现的的针对因子场景的数据库,方便因子的设计实现。通过dataview，可以快捷的调取数据，并在数据集上做运算以生成新的数据集。详细描述见[官方用户手册-数据视图](https://www.quantos.org/jaqs/doc.html)

## DataView做什么
将频繁使用的DataFrame操作自动化，使用者操作数据时尽量只考虑业务需求而不是技术实现：

- 1.根据字段名，自动从不同的数据api获取数据
- 2.按时间、标的整理对齐（财务数据按发布日期对齐）
- 3.在已有数据基础上，添加字段、加入自定义数据或根据公式计算新数据
- 4.数据查询
- 5.本地存储

## 数据下载
dataview目前可以通过jaqs官方提供的免费数据源直接从网络获取行情数据和参考数据

*** 步骤: ***

- 1.配置数据下载的tcp地址(data_config)--使用jaqs官方提供的免费数据源需要提前去官网注册账号,方可使用
- 2.创建DataView和DataService
- 3.配置待请求的数据参数(props)
- 4.数据下载(prepare_data)


```python
import warnings
warnings.filterwarnings('ignore')
```


```python
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
props = {'start_date': 20170501, 'end_date': 20171001, 'universe':'000300.SH',
         'fields': "pb,pe,total_oper_rev,oper_exp,sw1",
         'freq': 1}

dv.init_from_config(props, ds)
```

    
    Begin: DataApi login 18566262672@tcp://data.tushare.org:8910
        login success 
    
    Initialize config success.



```python
# stp4
dv.prepare_data()
```

    Query data...
    Query data - query...
    NOTE: price adjust method is [post adjust]
    当前请求daily...
    {'adjust_mode': None, 'fields': 'symbol,low_adj,high_adj,vwap,low,open,open_adj,trade_date,trade_status,close_adj,high,vwap_adj,close'}
    当前请求daily...
    {'adjust_mode': 'post', 'fields': 'symbol,low_adj,high_adj,vwap,low,open,open_adj,trade_date,trade_status,close_adj,high,vwap_adj,close'}
    当前请求query_lb_dailyindicator...
    {'fields': 'trade_date,pb,symbol,pe'}
    WARNING: some data is unavailable: 
        At fields 
    Query data - daily fields prepared.
    Query data - quarterly fields prepared.
    Query instrument info...
    Query adj_factor...
    Query benchmark...
    Query benchmar member info...
    Query groups (industry)...
    Field [sw1] is overwritten.
    Data has been successfully prepared.


**props参数**

|字段|缺省值|类型|说明|
|:----    |:---|:----- |-----   |
|symbol |不可缺失，symbol与universe二选一  |string |标的代码，多标的以','隔开，如'000001.SH,600300.SH'|
|universe |不可缺失，symbol与universe二选一  |string |指数代码（股票池），将该些指数的成员数据全部请求，多标的以','隔开，如沪深300成分股+上证50成分股'000300.SH,000016.SH'|
|benchmark |默认为universe中设置的第一个指数 |string |基准，可以为指数代码或个股代码，单标的|
|start_date |不可缺省 |int |开始日期|
|end_date |不可缺省 |int |结束日期|
|fields |不可缺省 |string |数据字段，多字段以','隔开，如'open,close,high,low'|
|freq |1 |int |数据类型，目前只支持1，表示日线数据|
|all_price |True |bool |是否默认下载所有日线行情相关数据。默认下载|
|adjust_mode |'post' |string |行情数据复权类型，默认后复权,目前只支持后复权|

### fields可选字段查询方式
dataview的底层数据api提供了字段的文档，可供查阅。目前,只提供了**A股财务数据**的相关字段文档。更过品种、行情相关字段文档请关注[jaqs官方数据文档](http://jaqs.readthedocs.io/zh_CN/latest/)


```python
from jaqs_fxdayu.data import DataApi

api = DataApi(data_config["remote.data.address"]) # 传入连接到的远端数据服务器的tcp地址
api.login(username=data_config["remote.data.username"],
          password=data_config["remote.data.password"])
```




    ('username: 18566262672', '0,')



### help.apiList

**简要描述：**

- 查询可选字段的类别

**示例：**


```python
df , msg = api.query(
                    view="help.apiList",
                    fields="",
                    filter="")
df
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
      <th>api</th>
      <th>comment</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>jy.balanceSheet</td>
      <td>资产负债表</td>
      <td>资产负债表</td>
    </tr>
    <tr>
      <th>1</th>
      <td>jy.cashFlow</td>
      <td>现金流量表</td>
      <td>现金流量表</td>
    </tr>
    <tr>
      <th>2</th>
      <td>jy.income</td>
      <td>利润表</td>
      <td>利润表</td>
    </tr>
    <tr>
      <th>3</th>
      <td>jz.instrumentInfo</td>
      <td>证券基本信息</td>
      <td>证券基础信息</td>
    </tr>
    <tr>
      <th>4</th>
      <td>jz.secTradeCal</td>
      <td>交易日历</td>
      <td>交易日历</td>
    </tr>
    <tr>
      <th>5</th>
      <td>lb.indexCons</td>
      <td>指数成份股</td>
      <td>指数成份股</td>
    </tr>
    <tr>
      <th>6</th>
      <td>lb.indexInfo</td>
      <td>指数基本信息</td>
      <td>指数基本信息</td>
    </tr>
    <tr>
      <th>7</th>
      <td>lb.industryType</td>
      <td>行业代码表</td>
      <td>行业代码表</td>
    </tr>
    <tr>
      <th>8</th>
      <td>lb.mfNav</td>
      <td>公募基金净值</td>
      <td>公募基金净值</td>
    </tr>
    <tr>
      <th>9</th>
      <td>lb.secAdjFactor</td>
      <td>复权因子</td>
      <td>复权因子</td>
    </tr>
    <tr>
      <th>10</th>
      <td>lb.secDividend</td>
      <td>分红送股</td>
      <td>分红送股表</td>
    </tr>
    <tr>
      <th>11</th>
      <td>lb.secIndustry</td>
      <td>行业分类信息</td>
      <td>行业分类</td>
    </tr>
    <tr>
      <th>12</th>
      <td>lb.secSusp</td>
      <td>停复牌数据</td>
      <td>停复牌</td>
    </tr>
  </tbody>
</table>
</div>



### help.apiParam

**简要描述：**

- 查询每个大类别下的可选字段及描述
- 通过filter字段可以限定查询的大类
- 返回结果中,param对应的即是dataview里的可选字段(fields)

**示例：**


```python
df ,msg = api.query(view="help.apiParam",fields="",filter="api=jy.cashFlow") # 查询现金流量表可选字段
df.head()
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
      <th>api</th>
      <th>comment</th>
      <th>dtype</th>
      <th>must</th>
      <th>param</th>
      <th>pname</th>
      <th>ptype</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>jy.cashFlow</td>
      <td></td>
      <td>String</td>
      <td>N</td>
      <td>symbol</td>
      <td>证券代码</td>
      <td>IN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>jy.cashFlow</td>
      <td></td>
      <td>String</td>
      <td>N</td>
      <td>start_date</td>
      <td>公告开始日期</td>
      <td>IN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>jy.cashFlow</td>
      <td></td>
      <td>String</td>
      <td>N</td>
      <td>end_date</td>
      <td>公告结束日期</td>
      <td>IN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>jy.cashFlow</td>
      <td></td>
      <td>String</td>
      <td>N</td>
      <td>start_reportdate</td>
      <td>报告期开始日期</td>
      <td>IN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>jy.cashFlow</td>
      <td></td>
      <td>String</td>
      <td>N</td>
      <td>start_reportdate</td>
      <td>报告期结束日期</td>
      <td>IN</td>
    </tr>
  </tbody>
</table>
</div>



## 数据查询

### fields
- ` jaqs_fxdayu.data.Dataview.fields `

**简要描述：**

- 当前dataview中的数据字段
- 说明：
  -  初始请求数据时指定universe，会自动补充index_member(是否是指数成分股)、index_weight(指数成分权重)字段；若universe为多标,取设置的第一个指数为准补充index_member和index_weight
  -  初始请求数据时指定all_price=True,会请求open、high、low、close、vwap及相应复权后的结果open_adj、high_adj、low_adj、close_adj、vwap_adj
  -  初始请求行情相关数据（如fields中包含open、high等字段,或指定all_price=True）,会自动补充trade_status(交易状态-停牌or可交易)
  -  初始请求数据字段中包含季度数据,会自动补充quarter(季度数据对应披露月份)、ann_date(季度数据)字段
  -  初始请求数据字段中包含季度数据,会自动按时间、标的整理对齐一份到日级别上
  -  初始请求数据默认会自动补充adjust_factor(复权因子)

**示例：**


```python
dv.fields
```




    ['sw1',
     'low_adj',
     'high_adj',
     'pe',
     'quarter',
     'low',
     'oper_exp',
     'open_adj',
     'trade_status',
     'close_adj',
     'index_weight',
     'pb',
     'total_oper_rev',
     'open',
     'high',
     '_limit',
     'ann_date',
     'vwap',
     'vwap_adj',
     'close',
     'adjust_factor',
     'index_member',
     '_daily_adjust_factor']



### _get_fields
- ` jaqs_fxdayu.data.Dataview._get_fields(field_type, fields) `

**简要描述：**

- 查询众多字段属于某种类型的数据
  - field_type:{'market_daily', 'ref_daily', 'income', 'balance_sheet', 'cash_flow', 'fin_indicator', 'group', 'daily', 'quarterly'
   (对应类型分别为 日行情、日参考数据、收入相关、balance_sheet相关、现金流相关、财务指标相关、行业分类相关、日级别数据、季度级别数据)
  - fields:list of str

**示例：**


```python
dv._get_fields('quarterly',dv.fields) # 查询数据集的字段里有哪些是季度级别数据
```




    ['quarter', 'total_oper_rev', 'ann_date', 'oper_exp']



###  symbol
- ` jaqs_fxdayu.data.Dataview.symbol `

**简要描述：**

- 当前dataview中的标的品种

**示例：**


```python
dv.symbol[:2] # 前两只股票
```




    ['000001.SZ', '000002.SZ']



### universe
- ` jaqs_fxdayu.data.Dataview.universe `

**简要描述：**

- 当前dataview中股票池的指数代码

**示例：**


```python
dv.universe
```




    ['000300.SH']



### benchmark
- ` jaqs_fxdayu.data.Dataview.benchmark `

**简要描述：**

- 当前dataview中的基准代码

**示例：**


```python
dv.benchmark
```




    '000300.SH'



### data_benchmark
- ` jaqs_fxdayu.data.Dataview.data_benchmark `

**简要描述：**

- 当前dataview中的基准的日行情数据

**示例：**


```python
dv.data_benchmark.head()
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
      <th>close</th>
    </tr>
    <tr>
      <th>trade_date</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>20170306</th>
      <td>3446.4840</td>
    </tr>
    <tr>
      <th>20170307</th>
      <td>3453.9565</td>
    </tr>
    <tr>
      <th>20170308</th>
      <td>3448.7313</td>
    </tr>
    <tr>
      <th>20170309</th>
      <td>3426.9438</td>
    </tr>
    <tr>
      <th>20170310</th>
      <td>3427.8916</td>
    </tr>
  </tbody>
</table>
</div>



### data_inst
- ` jaqs_fxdayu.data.Dataview.data_inst `

**简要描述：**

- 数据集中的证券基础信息

**示例：**


```python
dv.data_inst.head()
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
      <th>buylot</th>
      <th>delist_date</th>
      <th>inst_type</th>
      <th>list_date</th>
      <th>multiplier</th>
      <th>name</th>
      <th>pricetick</th>
      <th>product</th>
    </tr>
    <tr>
      <th>symbol</th>
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
      <th>600000.SH</th>
      <td>100</td>
      <td>99999999</td>
      <td>1</td>
      <td>19991110</td>
      <td>1</td>
      <td>浦发银行</td>
      <td>0.01</td>
      <td></td>
    </tr>
    <tr>
      <th>600016.SH</th>
      <td>100</td>
      <td>99999999</td>
      <td>1</td>
      <td>20001219</td>
      <td>1</td>
      <td>民生银行</td>
      <td>0.01</td>
      <td></td>
    </tr>
    <tr>
      <th>600030.SH</th>
      <td>100</td>
      <td>99999999</td>
      <td>1</td>
      <td>20030106</td>
      <td>1</td>
      <td>中信证券</td>
      <td>0.01</td>
      <td></td>
    </tr>
    <tr>
      <th>600050.SH</th>
      <td>100</td>
      <td>99999999</td>
      <td>1</td>
      <td>20021009</td>
      <td>1</td>
      <td>中国联通</td>
      <td>0.01</td>
      <td></td>
    </tr>
    <tr>
      <th>600109.SH</th>
      <td>100</td>
      <td>99999999</td>
      <td>1</td>
      <td>19970807</td>
      <td>1</td>
      <td>国金证券</td>
      <td>0.01</td>
      <td></td>
    </tr>
  </tbody>
</table>
</div>



|字段|字段中文名|
|:----    |:---|
|inst_type|	证券类型|
|symbol	|证券代码|
|name	|证券名称|
|list_date	|上市日期|
|delist_date|	退市日期|
|buylot	|最小买入单位|
|pricetick	|最小变动单位|
|product	|合约品种|
|multiplier	|合约乘数|

### dates
- ` jaqs_fxdayu.data.Dataview.dates `

**简要描述：**

- 数据的日期序列

**示例：**


```python
dv.dates[:2] #日期序列前两个
```




    array([20170306, 20170307])



### data_d
- ` jaqs_fxdayu.data.Dataview.data_d`

**简要描述：**

- 日级别数据集

**示例：**


```python
dv.data_d.head()
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
    <tr>
      <th>symbol</th>
      <th colspan="10" halign="left">000001.SZ</th>
      <th>...</th>
      <th colspan="10" halign="left">603993.SH</th>
    </tr>
    <tr>
      <th>field</th>
      <th>_daily_adjust_factor</th>
      <th>_limit</th>
      <th>adjust_factor</th>
      <th>ann_date</th>
      <th>close</th>
      <th>close_adj</th>
      <th>high</th>
      <th>high_adj</th>
      <th>index_member</th>
      <th>index_weight</th>
      <th>...</th>
      <th>open_adj</th>
      <th>oper_exp</th>
      <th>pb</th>
      <th>pe</th>
      <th>quarter</th>
      <th>sw1</th>
      <th>total_oper_rev</th>
      <th>trade_status</th>
      <th>vwap</th>
      <th>vwap_adj</th>
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
      <th>20170306</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>100.523</td>
      <td>20161021.0</td>
      <td>9.45</td>
      <td>949.94235</td>
      <td>9.46</td>
      <td>950.94758</td>
      <td>1.0</td>
      <td>0.008449</td>
      <td>...</td>
      <td>15.685408</td>
      <td>0.0</td>
      <td>4.7252</td>
      <td>110.7088</td>
      <td>9.0</td>
      <td>240000</td>
      <td>3.496036e+09</td>
      <td>交易</td>
      <td>4.97</td>
      <td>15.94</td>
    </tr>
    <tr>
      <th>20170307</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>100.523</td>
      <td>20161021.0</td>
      <td>9.45</td>
      <td>949.94235</td>
      <td>9.46</td>
      <td>950.94758</td>
      <td>1.0</td>
      <td>0.008449</td>
      <td>...</td>
      <td>15.974097</td>
      <td>0.0</td>
      <td>4.5926</td>
      <td>107.6027</td>
      <td>9.0</td>
      <td>240000</td>
      <td>3.496036e+09</td>
      <td>交易</td>
      <td>4.88</td>
      <td>15.66</td>
    </tr>
    <tr>
      <th>20170308</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>100.523</td>
      <td>20161021.0</td>
      <td>9.42</td>
      <td>946.92666</td>
      <td>9.45</td>
      <td>949.94235</td>
      <td>1.0</td>
      <td>0.008449</td>
      <td>...</td>
      <td>15.557102</td>
      <td>0.0</td>
      <td>4.6211</td>
      <td>108.2683</td>
      <td>9.0</td>
      <td>240000</td>
      <td>3.496036e+09</td>
      <td>交易</td>
      <td>4.87</td>
      <td>15.62</td>
    </tr>
    <tr>
      <th>20170309</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>100.523</td>
      <td>20161021.0</td>
      <td>9.38</td>
      <td>942.90574</td>
      <td>9.43</td>
      <td>947.93189</td>
      <td>1.0</td>
      <td>0.008449</td>
      <td>...</td>
      <td>15.781638</td>
      <td>0.0</td>
      <td>4.6495</td>
      <td>108.9339</td>
      <td>9.0</td>
      <td>240000</td>
      <td>3.496036e+09</td>
      <td>交易</td>
      <td>4.95</td>
      <td>15.89</td>
    </tr>
    <tr>
      <th>20170310</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>100.523</td>
      <td>20161021.0</td>
      <td>9.40</td>
      <td>944.91620</td>
      <td>9.41</td>
      <td>945.92143</td>
      <td>1.0</td>
      <td>0.008449</td>
      <td>...</td>
      <td>15.525026</td>
      <td>0.0</td>
      <td>4.6021</td>
      <td>107.8246</td>
      <td>9.0</td>
      <td>240000</td>
      <td>3.496036e+09</td>
      <td>交易</td>
      <td>4.87</td>
      <td>15.62</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 7590 columns</p>
</div>



###  data_q
- ` jaqs_fxdayu.data.Dataview.data_q `

**简要描述：**

- 季度级别数据集

**示例：**


```python
dv.data_q.head()
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
    <tr>
      <th>symbol</th>
      <th colspan="4" halign="left">000001.SZ</th>
      <th colspan="4" halign="left">000002.SZ</th>
      <th colspan="2" halign="left">000008.SZ</th>
      <th>...</th>
      <th colspan="2" halign="left">603858.SH</th>
      <th colspan="4" halign="left">603885.SH</th>
      <th colspan="4" halign="left">603993.SH</th>
    </tr>
    <tr>
      <th>field</th>
      <th>ann_date</th>
      <th>oper_exp</th>
      <th>quarter</th>
      <th>total_oper_rev</th>
      <th>ann_date</th>
      <th>oper_exp</th>
      <th>quarter</th>
      <th>total_oper_rev</th>
      <th>ann_date</th>
      <th>oper_exp</th>
      <th>...</th>
      <th>quarter</th>
      <th>total_oper_rev</th>
      <th>ann_date</th>
      <th>oper_exp</th>
      <th>quarter</th>
      <th>total_oper_rev</th>
      <th>ann_date</th>
      <th>oper_exp</th>
      <th>quarter</th>
      <th>total_oper_rev</th>
    </tr>
    <tr>
      <th>report_date</th>
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
      <th>20140930</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>9</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>9</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>9</td>
      <td>NaN</td>
      <td>20151031.0</td>
      <td>0.0</td>
      <td>9</td>
      <td>5.092343e+09</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>9</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>20150331</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>3</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>3</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>3</td>
      <td>NaN</td>
      <td>20160421.0</td>
      <td>0.0</td>
      <td>3</td>
      <td>1.956667e+09</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>3</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>20150630</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>6</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>6</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>6</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>6</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>6</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>20150930</th>
      <td>20151023.0</td>
      <td>4.784700e+10</td>
      <td>9</td>
      <td>7.115200e+10</td>
      <td>20151028.0</td>
      <td>0.0</td>
      <td>9</td>
      <td>7.959621e+10</td>
      <td>20151031.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>9</td>
      <td>7.774995e+09</td>
      <td>20151031.0</td>
      <td>0.0</td>
      <td>9</td>
      <td>6.262755e+09</td>
      <td>20151030.0</td>
      <td>0.0</td>
      <td>9</td>
      <td>3.174664e+09</td>
    </tr>
    <tr>
      <th>20151231</th>
      <td>20160310.0</td>
      <td>6.726800e+10</td>
      <td>12</td>
      <td>9.616300e+10</td>
      <td>20160314.0</td>
      <td>0.0</td>
      <td>12</td>
      <td>1.955491e+11</td>
      <td>20160427.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>12</td>
      <td>1.165563e+10</td>
      <td>20160415.0</td>
      <td>0.0</td>
      <td>12</td>
      <td>8.158238e+09</td>
      <td>20160325.0</td>
      <td>0.0</td>
      <td>12</td>
      <td>4.196840e+09</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 1320 columns</p>
</div>



### get
- ` jaqs_fxdayu.data.Dataview.get(symbol="", start_date=0, end_date=0, fields="") `

**简要描述：**

- 综合查询方法：按品种+字段+日期查询数据，返回日期为索引，品种+字段(MultiIndex)为columns的DataFrame

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|symbol|否 |string|标的代码，多标的以','隔开，如'000001.SH,600300.SH',默认查询数据集中所有标的|
|start_date |否 |int |开始日期，默认从数据集开始日期起|
|end_date |否 |int |结束日期，默认到数据集结束日期|
|fields |否 |string |数据字段，多字段以','隔开，如'open,close,high,low'，默认查询数据集中所有字段|

**示例：**


```python
dv.get("000001.SZ,000002.SZ",fields="open,high").head()
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
    <tr>
      <th>symbol</th>
      <th colspan="2" halign="left">000001.SZ</th>
      <th colspan="2" halign="left">000002.SZ</th>
    </tr>
    <tr>
      <th>field</th>
      <th>high</th>
      <th>open</th>
      <th>high</th>
      <th>open</th>
    </tr>
    <tr>
      <th>trade_date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>20170502</th>
      <td>8.96</td>
      <td>8.96</td>
      <td>19.37</td>
      <td>19.30</td>
    </tr>
    <tr>
      <th>20170503</th>
      <td>8.93</td>
      <td>8.92</td>
      <td>19.25</td>
      <td>19.20</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>8.89</td>
      <td>8.89</td>
      <td>19.19</td>
      <td>18.90</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>8.76</td>
      <td>8.74</td>
      <td>19.07</td>
      <td>18.95</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>8.62</td>
      <td>8.60</td>
      <td>18.96</td>
      <td>18.89</td>
    </tr>
  </tbody>
</table>
</div>



### get_snapshot
- ` jaqs_fxdayu.data.Dataview.get_snapshot(snapshot_date, symbol="", fields="") `

**简要描述：**

- 切片查询方法：指定日期，按品种+字段查询数据，返回品种为索引，字段为columns的DataFrame

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|snapshot_date |是 |int |指定查询切片的日期|
|symbol|否 |string|标的代码，多标的以','隔开，如'000001.SH,600300.SH',默认查询数据集中所有标的|
|fields |否 |string |数据字段，多字段以','隔开，如'open,close,high,low'，默认查询数据集中所有字段|

**示例：**


```python
dv.get_snapshot(20170504, fields="open,high").head()
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
      <th>field</th>
      <th>high</th>
      <th>open</th>
    </tr>
    <tr>
      <th>symbol</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>000001.SZ</th>
      <td>8.89</td>
      <td>8.89</td>
    </tr>
    <tr>
      <th>000002.SZ</th>
      <td>19.19</td>
      <td>18.90</td>
    </tr>
    <tr>
      <th>000008.SZ</th>
      <td>7.93</td>
      <td>7.93</td>
    </tr>
    <tr>
      <th>000009.SZ</th>
      <td>8.65</td>
      <td>8.51</td>
    </tr>
    <tr>
      <th>000027.SZ</th>
      <td>6.93</td>
      <td>6.84</td>
    </tr>
  </tbody>
</table>
</div>



### get_ts
- ` jaqs_fxdayu.data.Dataview.get_ts(field, symbol="", start_date=0, end_date=0) `

**简要描述：**

- 切片查询方法：指定字段，按时间+品种查询数据，返回时间为索引，品种为columns的DataFrame
- 查询的结果为日频（季度数据也会被自动扩展为日频）

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|symbol|否 |string|标的代码，多标的以','隔开，如'000001.SH,600300.SH',默认查询数据集中所有标的|
|start_date |否 |int |开始日期，默认从数据集开始日期起|
|end_date |否 |int |结束日期，默认到数据集结束日期|
|field |是 |string |数据字段,**单字段**|

**示例：**


```python
dv.get_ts("open").head()
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
      <th>symbol</th>
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
      <th>20170502</th>
      <td>8.96</td>
      <td>19.30</td>
      <td>8.09</td>
      <td>8.40</td>
      <td>6.99</td>
      <td>16.09</td>
      <td>10.33</td>
      <td>9.32</td>
      <td>17.73</td>
      <td>8.15</td>
      <td>...</td>
      <td>3.58</td>
      <td>7.05</td>
      <td>8.09</td>
      <td>15.70</td>
      <td>6.01</td>
      <td>14.90</td>
      <td>96.55</td>
      <td>80.25</td>
      <td>22.28</td>
      <td>4.41</td>
    </tr>
    <tr>
      <th>20170503</th>
      <td>8.92</td>
      <td>19.20</td>
      <td>7.99</td>
      <td>8.52</td>
      <td>6.95</td>
      <td>16.06</td>
      <td>10.24</td>
      <td>9.32</td>
      <td>17.58</td>
      <td>8.09</td>
      <td>...</td>
      <td>3.55</td>
      <td>6.96</td>
      <td>8.15</td>
      <td>15.67</td>
      <td>5.97</td>
      <td>14.90</td>
      <td>97.88</td>
      <td>80.60</td>
      <td>22.28</td>
      <td>4.44</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>8.89</td>
      <td>18.90</td>
      <td>7.93</td>
      <td>8.51</td>
      <td>6.84</td>
      <td>15.96</td>
      <td>10.13</td>
      <td>9.22</td>
      <td>17.78</td>
      <td>7.96</td>
      <td>...</td>
      <td>3.53</td>
      <td>6.85</td>
      <td>7.58</td>
      <td>15.68</td>
      <td>5.90</td>
      <td>14.80</td>
      <td>97.20</td>
      <td>80.50</td>
      <td>22.40</td>
      <td>4.44</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>8.74</td>
      <td>18.95</td>
      <td>7.90</td>
      <td>8.54</td>
      <td>6.85</td>
      <td>15.70</td>
      <td>9.91</td>
      <td>9.16</td>
      <td>17.80</td>
      <td>7.98</td>
      <td>...</td>
      <td>3.52</td>
      <td>6.74</td>
      <td>7.78</td>
      <td>15.56</td>
      <td>5.85</td>
      <td>14.35</td>
      <td>97.00</td>
      <td>79.71</td>
      <td>22.40</td>
      <td>4.30</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>8.60</td>
      <td>18.89</td>
      <td>7.52</td>
      <td>8.26</td>
      <td>6.79</td>
      <td>15.17</td>
      <td>9.89</td>
      <td>9.10</td>
      <td>17.56</td>
      <td>7.87</td>
      <td>...</td>
      <td>3.52</td>
      <td>6.59</td>
      <td>7.80</td>
      <td>15.05</td>
      <td>5.83</td>
      <td>14.11</td>
      <td>94.11</td>
      <td>78.31</td>
      <td>22.32</td>
      <td>4.23</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>



### get_ts_quarter
- ` jaqs_fxdayu.data.Dataview.get_ts_quarter(field, symbol="", start_date=0, end_date=0) `

**简要描述：**

- 切片查询方法：指定字段，按时间+品种查询季度数据，返回报告日期为索引，品种为columns的DataFrame
- 注意：参数中提供的field必须为**季度数据**，可通过Dataview._get_fields('quarterly',Dataview.fields)查询数据集的字段里有哪些是季度级别数据

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|symbol|否 |string|标的代码，多标的以','隔开，如'000001.SH,600300.SH',默认查询数据集中所有标的|
|start_date |否 |int |开始日期，默认从数据集开始日期起|
|end_date |否 |int |结束日期，默认到数据集结束日期|
|field |是 |string |季度数据字段,**单字段**|

**示例：**


```python
dv.get_ts_quarter('total_oper_rev').head()
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
      <th>symbol</th>
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
      <th>report_date</th>
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
      <th>20140930</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>5.092343e+09</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>20150331</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1.698335e+09</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1.956667e+09</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>20150630</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>3.622176e+09</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>4.815833e+08</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>20150930</th>
      <td>7.115200e+10</td>
      <td>7.959621e+10</td>
      <td>7.631092e+08</td>
      <td>3.145235e+09</td>
      <td>8.676531e+09</td>
      <td>4.527115e+10</td>
      <td>1.149957e+10</td>
      <td>1.280032e+09</td>
      <td>6.852324e+10</td>
      <td>NaN</td>
      <td>...</td>
      <td>3.567730e+11</td>
      <td>3.977208e+10</td>
      <td>2.590268e+10</td>
      <td>5.605255e+09</td>
      <td>1.074530e+11</td>
      <td>1.066451e+09</td>
      <td>7.322436e+08</td>
      <td>7.774995e+09</td>
      <td>6.262755e+09</td>
      <td>3.174664e+09</td>
    </tr>
    <tr>
      <th>20151231</th>
      <td>9.616300e+10</td>
      <td>1.955491e+11</td>
      <td>1.295076e+09</td>
      <td>4.895401e+09</td>
      <td>1.112998e+10</td>
      <td>5.868580e+10</td>
      <td>1.696571e+10</td>
      <td>1.736651e+09</td>
      <td>1.001864e+11</td>
      <td>3.223633e+10</td>
      <td>...</td>
      <td>4.743210e+11</td>
      <td>5.981080e+10</td>
      <td>4.092534e+10</td>
      <td>7.705192e+09</td>
      <td>1.451340e+11</td>
      <td>1.604762e+09</td>
      <td>1.119601e+09</td>
      <td>1.165563e+10</td>
      <td>8.158238e+09</td>
      <td>4.196840e+09</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>



## 数据添加

### data_api
- ` jaqs_fxdayu.data.Dataview.data_api `

**简要描述：**

- 数据api(DataService远程数据服务类)

**示例：**


```python
dv.data_api
```




    <jaqs.data.dataservice.RemoteDataService at 0x7fa0d418f588>



### add_comp_info
- ` jaqs_fxdayu.data.Dataview.add_comp_info(index,data_api=None) `

**简要描述：**

- 往数据集里添加两个新字段——symbol是否属于某指数成分股 & symbol在某指数中所占的比重如何
- 区别于通过设置universe初始化默认下载的index_member和index_weight字段, 通过该方法新增的字段可更灵活的查询股票标的与任意指数的关系和权重
- 新增字段名为[index]_member [index]_weight

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|index |是  |string|指数代码|
|data_api |否  |jaqs.data.dataservice.RemoteDataService|DataService远程数据服务类|

**示例：**


```python
dv.add_comp_info('000016.SH')
```


```python
dv.get_ts("000016.SH_weight").head()
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
      <th>symbol</th>
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
      <th>20170502</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>0.01881</td>
      <td>0.01607</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.00459</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>20170503</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>0.01881</td>
      <td>0.01607</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.00459</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>0.01881</td>
      <td>0.01607</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.00459</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>0.01881</td>
      <td>0.01607</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.00459</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>0.01881</td>
      <td>0.01607</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.00459</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>



### add_field
- ` jaqs_fxdayu.data.Dataview.add_field(field_name, data_api=None) `

**简要描述：**

- 通过远程数据源往数据集里新增新字段（需确保远程数据源中含有该字段的数据）

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|field_name|是  |string|待新增的字段名|
|data_api |否  |jaqs.data.dataservice.RemoteDataService|DataService远程数据服务类|

**示例：**


```python
dv.add_field("volume")
```

    Query data - query...
    NOTE: price adjust method is [post adjust]
    当前请求daily...
    {'adjust_mode': None, 'fields': 'symbol,vwap,low,open,trade_date,trade_status,high,volume,close'}
    当前请求daily...
    {'adjust_mode': 'post', 'fields': 'symbol,vwap,low,open,trade_date,trade_status,high,volume,close'}
    Query data - daily fields prepared.





    True




```python
dv.get_ts("volume").head()
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
      <th>symbol</th>
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
      <th>20170502</th>
      <td>31102610.0</td>
      <td>18442367.0</td>
      <td>9684786.0</td>
      <td>25497861.0</td>
      <td>6432105.0</td>
      <td>6327586.0</td>
      <td>8965345.0</td>
      <td>4378121.0</td>
      <td>19238235.0</td>
      <td>27143591.0</td>
      <td>...</td>
      <td>66093550.0</td>
      <td>66530694.0</td>
      <td>544839719.0</td>
      <td>10925965.0</td>
      <td>17520651.0</td>
      <td>3119911.0</td>
      <td>2091792.0</td>
      <td>818200.0</td>
      <td>926950.0</td>
      <td>88555440.0</td>
    </tr>
    <tr>
      <th>20170503</th>
      <td>28031077.0</td>
      <td>26926611.0</td>
      <td>7763618.0</td>
      <td>18416240.0</td>
      <td>10746444.0</td>
      <td>6107544.0</td>
      <td>13106532.0</td>
      <td>4834657.0</td>
      <td>34074547.0</td>
      <td>38599137.0</td>
      <td>...</td>
      <td>84611551.0</td>
      <td>86231763.0</td>
      <td>516934503.0</td>
      <td>11688295.0</td>
      <td>23738285.0</td>
      <td>5159855.0</td>
      <td>1346232.0</td>
      <td>854976.0</td>
      <td>1006828.0</td>
      <td>58089924.0</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>69651707.0</td>
      <td>17846705.0</td>
      <td>8177165.0</td>
      <td>15236008.0</td>
      <td>7574795.0</td>
      <td>7298552.0</td>
      <td>25223485.0</td>
      <td>5413535.0</td>
      <td>33992154.0</td>
      <td>17511452.0</td>
      <td>...</td>
      <td>74607306.0</td>
      <td>105007184.0</td>
      <td>606859878.0</td>
      <td>15697719.0</td>
      <td>38672243.0</td>
      <td>6574210.0</td>
      <td>823415.0</td>
      <td>1148000.0</td>
      <td>1139450.0</td>
      <td>72505821.0</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>62370085.0</td>
      <td>11655082.0</td>
      <td>17977630.0</td>
      <td>19831245.0</td>
      <td>7462745.0</td>
      <td>13769005.0</td>
      <td>14733040.0</td>
      <td>4027676.0</td>
      <td>32366194.0</td>
      <td>20326215.0</td>
      <td>...</td>
      <td>175567864.0</td>
      <td>139296698.0</td>
      <td>318657662.0</td>
      <td>15302449.0</td>
      <td>29776701.0</td>
      <td>7457617.0</td>
      <td>1135698.0</td>
      <td>1159354.0</td>
      <td>2677492.0</td>
      <td>69479848.0</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>46008989.0</td>
      <td>18399614.0</td>
      <td>8826250.0</td>
      <td>19415168.0</td>
      <td>9090216.0</td>
      <td>5051955.0</td>
      <td>14364021.0</td>
      <td>3932185.0</td>
      <td>29396110.0</td>
      <td>29515727.0</td>
      <td>...</td>
      <td>138086728.0</td>
      <td>144402061.0</td>
      <td>383459440.0</td>
      <td>14624454.0</td>
      <td>28293010.0</td>
      <td>5304703.0</td>
      <td>1563932.0</td>
      <td>1425800.0</td>
      <td>1799118.0</td>
      <td>47210293.0</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>



### add_formula

- ` jaqs_fxdayu.data.Dataview.add_formula(field_name,formula,is_quarterly,add_data=False,overwrite=True,formula_func_name_style='camel',data_api=None,register_funcs = None,within_index=True)  `


**简要描述：**

- 通过表达式定义因子

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|field_name|是  |string|自定义的因子名称|
|formula |是  |string|因子表达式|
|is_quarterly |是  |bool| (最终结果)是否是季度数据|
|add_data |否  |bool|是否将最终结果添加到dataview数据集中，默认不添加|
|overwrite |否  |bool|若因子名称(field_name)与数据集中已有的字段冲突，是否覆盖。仅在add_data=True时生效，默认覆盖|
|formula_func_name_style |否 |string {'upper', 'lower'， 'camel'}|表达式中用到的函数名大小写规则,默认为'camel'|
|data_api |否 |jaqs.data.dataservice.RemoteDataService|DataService远程数据服务类，若因子表达式中使用到的字段在当前数据集中没有，会通过该api自动从网络请求相应字段添加到当前数据集当中|
|register_funcs |否 |dict of function|因子表达式中用到的自定义方法所组成的dict,如{"name1":func1，"name2":func2}|
|with_index |否 |bool|执行因子表达式计算的时候 是否只考虑指数成分股。仅在数据集字段中含有index_member时生效, 默认为True|

**示例一：**
直接返回


```python
dv.add_formula("momentum", "Return(close_adj, 20)", is_quarterly=False).head()
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
      <th>symbol</th>
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
      <th>20170502</th>
      <td>-0.015419</td>
      <td>-0.064783</td>
      <td>-0.076389</td>
      <td>-0.057860</td>
      <td>0.007246</td>
      <td>-0.011707</td>
      <td>-0.074910</td>
      <td>-0.154265</td>
      <td>0.037647</td>
      <td>0.120332</td>
      <td>...</td>
      <td>-0.027322</td>
      <td>-0.034578</td>
      <td>0.708075</td>
      <td>-0.058859</td>
      <td>-0.099548</td>
      <td>-0.107944</td>
      <td>0.032925</td>
      <td>-0.084092</td>
      <td>-0.032118</td>
      <td>0.008929</td>
    </tr>
    <tr>
      <th>20170503</th>
      <td>-0.028353</td>
      <td>-0.083576</td>
      <td>-0.093822</td>
      <td>-0.066521</td>
      <td>-0.036517</td>
      <td>-0.006211</td>
      <td>-0.089767</td>
      <td>-0.162579</td>
      <td>0.050708</td>
      <td>0.093151</td>
      <td>...</td>
      <td>-0.045946</td>
      <td>-0.076613</td>
      <td>0.633047</td>
      <td>-0.101772</td>
      <td>-0.119225</td>
      <td>-0.105232</td>
      <td>0.030166</td>
      <td>-0.089233</td>
      <td>-0.038296</td>
      <td>-0.043550</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>-0.051031</td>
      <td>-0.075802</td>
      <td>-0.113611</td>
      <td>-0.085653</td>
      <td>-0.057613</td>
      <td>-0.043135</td>
      <td>-0.126427</td>
      <td>-0.179695</td>
      <td>0.028852</td>
      <td>0.076716</td>
      <td>...</td>
      <td>-0.040761</td>
      <td>-0.109211</td>
      <td>0.543860</td>
      <td>-0.087668</td>
      <td>-0.131657</td>
      <td>-0.146903</td>
      <td>0.001239</td>
      <td>-0.108997</td>
      <td>-0.048739</td>
      <td>-0.151733</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>-0.061957</td>
      <td>-0.091390</td>
      <td>-0.179543</td>
      <td>-0.114684</td>
      <td>-0.058172</td>
      <td>-0.095238</td>
      <td>-0.128748</td>
      <td>-0.185484</td>
      <td>0.017929</td>
      <td>0.059140</td>
      <td>...</td>
      <td>-0.032787</td>
      <td>-0.132199</td>
      <td>0.377660</td>
      <td>-0.109549</td>
      <td>-0.132244</td>
      <td>-0.162114</td>
      <td>-0.038807</td>
      <td>-0.127279</td>
      <td>-0.039676</td>
      <td>-0.162778</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>-0.068478</td>
      <td>-0.112019</td>
      <td>-0.194934</td>
      <td>-0.136120</td>
      <td>-0.075000</td>
      <td>-0.095668</td>
      <td>-0.129061</td>
      <td>-0.178796</td>
      <td>-0.013326</td>
      <td>0.042610</td>
      <td>...</td>
      <td>-0.019231</td>
      <td>-0.161880</td>
      <td>0.133871</td>
      <td>-0.127647</td>
      <td>-0.130370</td>
      <td>-0.175264</td>
      <td>-0.002776</td>
      <td>-0.132699</td>
      <td>-0.058723</td>
      <td>-0.152260</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>



**示例二：**
添加到数据集里，则计算结果之后可以反复调用


```python
dv.add_formula("momentum", "Return(close_adj, 20)", is_quarterly=False, add_data=True).head()
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
      <th>symbol</th>
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
      <th>20170502</th>
      <td>-0.015419</td>
      <td>-0.064783</td>
      <td>-0.076389</td>
      <td>-0.057860</td>
      <td>0.007246</td>
      <td>-0.011707</td>
      <td>-0.074910</td>
      <td>-0.154265</td>
      <td>0.037647</td>
      <td>0.120332</td>
      <td>...</td>
      <td>-0.027322</td>
      <td>-0.034578</td>
      <td>0.708075</td>
      <td>-0.058859</td>
      <td>-0.099548</td>
      <td>-0.107944</td>
      <td>0.032925</td>
      <td>-0.084092</td>
      <td>-0.032118</td>
      <td>0.008929</td>
    </tr>
    <tr>
      <th>20170503</th>
      <td>-0.028353</td>
      <td>-0.083576</td>
      <td>-0.093822</td>
      <td>-0.066521</td>
      <td>-0.036517</td>
      <td>-0.006211</td>
      <td>-0.089767</td>
      <td>-0.162579</td>
      <td>0.050708</td>
      <td>0.093151</td>
      <td>...</td>
      <td>-0.045946</td>
      <td>-0.076613</td>
      <td>0.633047</td>
      <td>-0.101772</td>
      <td>-0.119225</td>
      <td>-0.105232</td>
      <td>0.030166</td>
      <td>-0.089233</td>
      <td>-0.038296</td>
      <td>-0.043550</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>-0.051031</td>
      <td>-0.075802</td>
      <td>-0.113611</td>
      <td>-0.085653</td>
      <td>-0.057613</td>
      <td>-0.043135</td>
      <td>-0.126427</td>
      <td>-0.179695</td>
      <td>0.028852</td>
      <td>0.076716</td>
      <td>...</td>
      <td>-0.040761</td>
      <td>-0.109211</td>
      <td>0.543860</td>
      <td>-0.087668</td>
      <td>-0.131657</td>
      <td>-0.146903</td>
      <td>0.001239</td>
      <td>-0.108997</td>
      <td>-0.048739</td>
      <td>-0.151733</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>-0.061957</td>
      <td>-0.091390</td>
      <td>-0.179543</td>
      <td>-0.114684</td>
      <td>-0.058172</td>
      <td>-0.095238</td>
      <td>-0.128748</td>
      <td>-0.185484</td>
      <td>0.017929</td>
      <td>0.059140</td>
      <td>...</td>
      <td>-0.032787</td>
      <td>-0.132199</td>
      <td>0.377660</td>
      <td>-0.109549</td>
      <td>-0.132244</td>
      <td>-0.162114</td>
      <td>-0.038807</td>
      <td>-0.127279</td>
      <td>-0.039676</td>
      <td>-0.162778</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>-0.068478</td>
      <td>-0.112019</td>
      <td>-0.194934</td>
      <td>-0.136120</td>
      <td>-0.075000</td>
      <td>-0.095668</td>
      <td>-0.129061</td>
      <td>-0.178796</td>
      <td>-0.013326</td>
      <td>0.042610</td>
      <td>...</td>
      <td>-0.019231</td>
      <td>-0.161880</td>
      <td>0.133871</td>
      <td>-0.127647</td>
      <td>-0.130370</td>
      <td>-0.175264</td>
      <td>-0.002776</td>
      <td>-0.132699</td>
      <td>-0.058723</td>
      <td>-0.152260</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>



**示例三：**
通过事先定义并注册一些因子计算中需要的函数方法，完成更高自由度的因子计算


```python
# 定义指数平均计算函数-传入一个时间为索引,股票为columns的Dataframe,计算其指数平均序列
# SMAtoday=m/n * Pricetoday + ( n-m )/n * SMAyesterday;
def sma(df, n, m):
    a = n / m - 1
    r = df.ewm(com=a, axis=0, adjust=False)
    return r.mean()

dv.add_formula("double_SMA","SMA(SMA(close_adj,3,1),3,1)",
               is_quarterly=False,
               add_data=True,
               register_funcs={"SMA":sma}).head()
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
      <th>symbol</th>
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
      <th>20170502</th>
      <td>902.763220</td>
      <td>2486.337268</td>
      <td>222.702230</td>
      <td>86.694747</td>
      <td>96.210407</td>
      <td>384.093500</td>
      <td>243.687558</td>
      <td>213.240494</td>
      <td>298.533382</td>
      <td>321.033510</td>
      <td>...</td>
      <td>5.618304</td>
      <td>12.228624</td>
      <td>16.337667</td>
      <td>15.853791</td>
      <td>8.049842</td>
      <td>61.962369</td>
      <td>90.623181</td>
      <td>81.381230</td>
      <td>45.732059</td>
      <td>14.250433</td>
    </tr>
    <tr>
      <th>20170503</th>
      <td>901.693012</td>
      <td>2458.607759</td>
      <td>220.011542</td>
      <td>86.274281</td>
      <td>95.764841</td>
      <td>382.711958</td>
      <td>242.819760</td>
      <td>209.993794</td>
      <td>299.424894</td>
      <td>320.170244</td>
      <td>...</td>
      <td>5.610843</td>
      <td>12.093762</td>
      <td>16.388825</td>
      <td>15.822053</td>
      <td>7.996918</td>
      <td>61.652794</td>
      <td>92.037297</td>
      <td>81.146152</td>
      <td>45.665220</td>
      <td>14.262870</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>898.648253</td>
      <td>2434.327687</td>
      <td>217.509487</td>
      <td>85.953173</td>
      <td>95.348827</td>
      <td>380.921464</td>
      <td>241.525309</td>
      <td>207.048611</td>
      <td>300.227209</td>
      <td>319.209255</td>
      <td>...</td>
      <td>5.600827</td>
      <td>11.952804</td>
      <td>16.444759</td>
      <td>15.784386</td>
      <td>7.943142</td>
      <td>61.251215</td>
      <td>93.216093</td>
      <td>80.872100</td>
      <td>45.594402</td>
      <td>14.249688</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>893.835609</td>
      <td>2412.493048</td>
      <td>214.370868</td>
      <td>85.402007</td>
      <td>94.885973</td>
      <td>377.704290</td>
      <td>240.001648</td>
      <td>204.469036</td>
      <td>300.466335</td>
      <td>317.786651</td>
      <td>...</td>
      <td>5.592535</td>
      <td>11.798688</td>
      <td>16.461484</td>
      <td>15.702713</td>
      <td>7.890575</td>
      <td>60.693946</td>
      <td>93.950437</td>
      <td>80.487844</td>
      <td>45.588495</td>
      <td>14.194258</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>888.101823</td>
      <td>2388.403014</td>
      <td>210.622674</td>
      <td>84.588481</td>
      <td>94.241335</td>
      <td>373.764215</td>
      <td>238.650220</td>
      <td>202.458126</td>
      <td>299.352026</td>
      <td>316.098221</td>
      <td>...</td>
      <td>5.591171</td>
      <td>11.616677</td>
      <td>16.285680</td>
      <td>15.569446</td>
      <td>7.848774</td>
      <td>60.111181</td>
      <td>94.615652</td>
      <td>79.885080</td>
      <td>45.523878</td>
      <td>14.133393</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>



### func_doc
- ` jaqs_fxdayu.data.Dataview.func_doc `

**简要描述：**

- add_formula 支持的内置公式查询方法
- 查询方法包括：
  - func_doc.doc # 完整文档
  - func_doc.funcs # 函数一览
  - func_doc.types # 函数类型
  - func_doc.descriptions # 函数描述
  - func_doc.search_by_type(type) # 根据函数类型查询该类型下所有的函数 type-函数类型(string) 
  - func_doc.search_by_description(description) # 根据函数描述查询可能符合该描述的所有的函数 description-函数描述(string) 
  - dv.func_doc.search_by_func(func,precise) # 根据函数名查询该函数 func-函数方法(string) precise-是否模糊查询(bool) 
  

**示例：**


```python
# 完整文档-前5条
dv.func_doc.doc.head()
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
      <th>分类</th>
      <th>说明</th>
      <th>公式</th>
      <th>示例</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>四则运算</td>
      <td>加法运算</td>
      <td>+</td>
      <td>close + open</td>
    </tr>
    <tr>
      <th>1</th>
      <td>四则运算</td>
      <td>减法运算</td>
      <td>-</td>
      <td>close - open</td>
    </tr>
    <tr>
      <th>2</th>
      <td>四则运算</td>
      <td>乘法运算</td>
      <td>*</td>
      <td>vwap * volume</td>
    </tr>
    <tr>
      <th>3</th>
      <td>四则运算</td>
      <td>除法运算</td>
      <td>/</td>
      <td>close / open</td>
    </tr>
    <tr>
      <th>4</th>
      <td>基本数学函数</td>
      <td>符号函数，返回值为{-1, 0, 1}</td>
      <td>Sign(x)</td>
      <td>Sign(close-open)</td>
    </tr>
  </tbody>
</table>
</div>




```python
# 函数一览-前两个
dv.func_doc.funcs[:2]
```




    array(['+', '-'], dtype=object)




```python
# 函数类型-前两个
dv.func_doc.types[:2]
```




    array(['四则运算', '基本数学函数'], dtype=object)




```python
# 函数描述-前两个
dv.func_doc.descriptions[:2]
```




    array(['加法运算', '减法运算'], dtype=object)




```python
# 根据函数类型查询该类型下所有的函数
dv.func_doc.search_by_type("数学函数")
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
      <th>分类</th>
      <th>说明</th>
      <th>公式</th>
      <th>示例</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>4</th>
      <td>基本数学函数</td>
      <td>符号函数，返回值为{-1, 0, 1}</td>
      <td>Sign(x)</td>
      <td>Sign(close-open)</td>
    </tr>
    <tr>
      <th>5</th>
      <td>基本数学函数</td>
      <td>绝对值函数</td>
      <td>Abs(x)</td>
      <td>Abs(close-open)</td>
    </tr>
    <tr>
      <th>6</th>
      <td>基本数学函数</td>
      <td>自然对数</td>
      <td>Log(x)</td>
      <td>Log(close/open)</td>
    </tr>
    <tr>
      <th>7</th>
      <td>基本数学函数</td>
      <td>对x取负</td>
      <td>-x</td>
      <td>-close</td>
    </tr>
    <tr>
      <th>8</th>
      <td>基本数学函数</td>
      <td>幂函数</td>
      <td>^</td>
      <td>close ^ 2</td>
    </tr>
    <tr>
      <th>9</th>
      <td>基本数学函数</td>
      <td>幂函数x^y</td>
      <td>Pow(x,y)</td>
      <td>Pow(close,2)</td>
    </tr>
    <tr>
      <th>10</th>
      <td>基本数学函数</td>
      <td>保持符号的幂函数，等价于Sign(x) * (Abs(x)^e)</td>
      <td>SignedPower(x,e)</td>
      <td>SignedPower(close-open, 0.5)</td>
    </tr>
    <tr>
      <th>11</th>
      <td>基本数学函数</td>
      <td>取余函数</td>
      <td>%</td>
      <td>oi % 10</td>
    </tr>
  </tbody>
</table>
</div>




```python
# 根据函数描述查询可能符合该描述的所有的函数
dv.func_doc.search_by_description("绝对值")
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
      <th>分类</th>
      <th>说明</th>
      <th>公式</th>
      <th>示例</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>5</th>
      <td>基本数学函数</td>
      <td>绝对值函数</td>
      <td>Abs(x)</td>
      <td>Abs(close-open)</td>
    </tr>
  </tbody>
</table>
</div>




```python
# 根据函数名查询该函数
dv.func_doc.search_by_func("Tan",precise=True)
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
      <th>分类</th>
      <th>说明</th>
      <th>公式</th>
      <th>示例</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>24</th>
      <td>三角函数</td>
      <td>正切函数</td>
      <td>Tan(x)</td>
      <td>Tan(close/open)</td>
    </tr>
  </tbody>
</table>
</div>




```python
# 根据函数名查询该函数 -模糊查询
dv.func_doc.search_by_func("Tan",precise=False)
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
      <th>分类</th>
      <th>说明</th>
      <th>公式</th>
      <th>示例</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>24</th>
      <td>三角函数</td>
      <td>正切函数</td>
      <td>Tan(x)</td>
      <td>Tan(close/open)</td>
    </tr>
    <tr>
      <th>56</th>
      <td>横截面函数 - 数据处理</td>
      <td>将指标标准化，即在横截面上减去平均值后再除以标准差</td>
      <td>Standardize(x)</td>
      <td>Standardize(close/Delay(close,1)-1) 表示日收益率的标准化</td>
    </tr>
  </tbody>
</table>
</div>



### append_df

- ` jaqs_fxdayu.data.Dataview.append_df(df, field_name, is_quarterly=False, overwrite=True) `

**简要描述：**

- 外部构造一个pandas.DataFrame,作为新增字段通过此方法添加到数据集中(更灵活的定义因子的方式)
- 注：该方法通常只用于添加**日度**数据（设置is_qurterly=False），若通过该方法添加季度数据（is_qurterly=True）,则添加的数据无法自动对齐到日级别，也无法通过get_ts方法访问到。
- 如需添加季度数据并将其自动对齐到日级别，请使用append_df_quarter方法

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|df |是  |pandas.DataFrame，日期为索引，品种为columns|待添加的数据|
|field_name|是  |string|待新增的数据的字段名|
|is_quarterly|否  |bool|是否是季度数据,默认False|
|overwrite |否  |bool|若待新增的数据的字段名(field_name)与数据集中已有的字段冲突，是否覆盖。默认覆盖|

**示例：**


```python
df = dv.get_ts('close') - dv.get_ts("high")
dv.append_df(df,"close-high",is_quarterly=False)
dv.get_ts("close-high").head()
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
      <th>symbol</th>
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
      <th>20170502</th>
      <td>-0.02</td>
      <td>-0.17</td>
      <td>-0.15</td>
      <td>-0.04</td>
      <td>-0.04</td>
      <td>-0.25</td>
      <td>-0.10</td>
      <td>-0.17</td>
      <td>-0.15</td>
      <td>-0.13</td>
      <td>...</td>
      <td>-0.02</td>
      <td>-0.07</td>
      <td>-0.09</td>
      <td>-0.12</td>
      <td>-0.06</td>
      <td>-0.19</td>
      <td>-2.00</td>
      <td>-0.49</td>
      <td>-0.10</td>
      <td>-0.15</td>
    </tr>
    <tr>
      <th>20170503</th>
      <td>-0.02</td>
      <td>-0.39</td>
      <td>-0.12</td>
      <td>-0.08</td>
      <td>-0.09</td>
      <td>-0.16</td>
      <td>-0.21</td>
      <td>-0.15</td>
      <td>-0.23</td>
      <td>-0.17</td>
      <td>...</td>
      <td>-0.03</td>
      <td>-0.10</td>
      <td>-0.54</td>
      <td>-0.09</td>
      <td>-0.06</td>
      <td>-0.16</td>
      <td>-0.58</td>
      <td>-0.43</td>
      <td>-0.03</td>
      <td>-0.14</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>-0.15</td>
      <td>-0.17</td>
      <td>-0.05</td>
      <td>-0.11</td>
      <td>-0.06</td>
      <td>-0.30</td>
      <td>-0.18</td>
      <td>-0.10</td>
      <td>-0.25</td>
      <td>-0.04</td>
      <td>...</td>
      <td>-0.01</td>
      <td>-0.08</td>
      <td>-0.42</td>
      <td>-0.15</td>
      <td>-0.04</td>
      <td>-0.38</td>
      <td>-1.68</td>
      <td>-0.96</td>
      <td>-0.18</td>
      <td>-0.11</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>-0.13</td>
      <td>-0.18</td>
      <td>-0.36</td>
      <td>-0.32</td>
      <td>-0.09</td>
      <td>-0.62</td>
      <td>-0.12</td>
      <td>-0.07</td>
      <td>-0.29</td>
      <td>-0.18</td>
      <td>...</td>
      <td>-0.02</td>
      <td>-0.18</td>
      <td>-0.21</td>
      <td>-0.47</td>
      <td>-0.02</td>
      <td>-0.34</td>
      <td>-3.63</td>
      <td>-1.41</td>
      <td>-0.15</td>
      <td>-0.03</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>-0.05</td>
      <td>-0.49</td>
      <td>-0.21</td>
      <td>-0.26</td>
      <td>-0.14</td>
      <td>-0.30</td>
      <td>-0.17</td>
      <td>-0.09</td>
      <td>-0.64</td>
      <td>-0.19</td>
      <td>...</td>
      <td>0.00</td>
      <td>-0.17</td>
      <td>-0.82</td>
      <td>-0.37</td>
      <td>-0.02</td>
      <td>-0.38</td>
      <td>-2.49</td>
      <td>-1.71</td>
      <td>-0.39</td>
      <td>-0.02</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>



### append_df_quarter

- ` jaqs_fxdayu.data.Dataview.append_df_quarter(df, field_name, overwrite=True) `

**简要描述：**

- 外部构造一个pandas.DataFrame,且DataFrame中为**季度数据**,作为新增字段通过此方法添加到数据集中(更灵活的定义因子的方式)
> 与jaqs_fxdayu.data.Dataview.append_df(df, field_name, is_quarterly=True)不同之处在于:该方法为自动将所添加的季度也增加到日度数据中，相当于将数据对齐到日线为新数据df_daily后，再调用一次jaqs_fxdayu.data.Dataview.append_df(df_daily, field_name, is_quarterly=False)。这样可以方便加入季度，然后统一在日线周期下获取数据进行研究。

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|df |是  |pandas.DataFrame，日期为索引，品种为columns|待添加的数据|
|field_name|是  |string|待新增的数据的字段名|
|overwrite |否  |bool|若待新增的数据的字段名(field_name)与数据集中已有的字段冲突，是否覆盖。默认覆盖|

**示例：**


```python
dv.add_field("roe")
roe = dv.get_ts_quarter('roe')
df = roe.diff()
dv.append_df_quarter(df, "d-roe")
dv.get_ts_quarter("d-roe").dropna().head() # 查询季度数据
```

    Query data - query...
    Query data - quarterly fields prepared.





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
      <th>symbol</th>
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
      <th>report_date</th>
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
      <th>20160331</th>
      <td>-11.4660</td>
      <td>-18.4105</td>
      <td>-10.4000</td>
      <td>-18.7879</td>
      <td>-8.1359</td>
      <td>-6.3414</td>
      <td>-3.7253</td>
      <td>-0.3387</td>
      <td>-7.6121</td>
      <td>-12.4472</td>
      <td>...</td>
      <td>-10.4562</td>
      <td>4.8409</td>
      <td>-5.4368</td>
      <td>-20.6642</td>
      <td>-10.7903</td>
      <td>-9.0602</td>
      <td>-30.5938</td>
      <td>-58.5293</td>
      <td>-26.3598</td>
      <td>-3.9513</td>
    </tr>
    <tr>
      <th>20160630</th>
      <td>3.4734</td>
      <td>4.5853</td>
      <td>0.7098</td>
      <td>0.9384</td>
      <td>3.0494</td>
      <td>-2.7715</td>
      <td>1.3095</td>
      <td>0.5910</td>
      <td>2.0323</td>
      <td>2.5554</td>
      <td>...</td>
      <td>3.4989</td>
      <td>0.9899</td>
      <td>4.2848</td>
      <td>4.8958</td>
      <td>3.8221</td>
      <td>-0.2508</td>
      <td>17.8033</td>
      <td>5.4220</td>
      <td>0.5424</td>
      <td>2.1448</td>
    </tr>
    <tr>
      <th>20170331</th>
      <td>-9.3964</td>
      <td>-19.0699</td>
      <td>-11.4174</td>
      <td>-4.4972</td>
      <td>-5.7008</td>
      <td>-0.1440</td>
      <td>-1.5022</td>
      <td>-1.7294</td>
      <td>9.6676</td>
      <td>-15.1272</td>
      <td>...</td>
      <td>-8.8577</td>
      <td>-0.7407</td>
      <td>-5.5384</td>
      <td>-16.3442</td>
      <td>-8.9765</td>
      <td>-5.5680</td>
      <td>-37.6522</td>
      <td>-16.1615</td>
      <td>-17.3611</td>
      <td>-2.3932</td>
    </tr>
    <tr>
      <th>20170630</th>
      <td>3.0383</td>
      <td>5.8485</td>
      <td>0.7553</td>
      <td>1.0343</td>
      <td>1.3482</td>
      <td>0.9739</td>
      <td>3.5654</td>
      <td>0.1076</td>
      <td>2.8533</td>
      <td>2.1882</td>
      <td>...</td>
      <td>3.9847</td>
      <td>0.5797</td>
      <td>3.1304</td>
      <td>4.2815</td>
      <td>3.2946</td>
      <td>0.6141</td>
      <td>10.4661</td>
      <td>3.7218</td>
      <td>2.6678</td>
      <td>1.3230</td>
    </tr>
  </tbody>
</table>
<p>4 rows × 330 columns</p>
</div>




```python
# 对应的日度数据
dv.get_ts("d-roe").dropna().head()
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
      <th>symbol</th>
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
      <th>20170502</th>
      <td>-9.3964</td>
      <td>-19.0699</td>
      <td>-11.4174</td>
      <td>-4.4972</td>
      <td>-5.7008</td>
      <td>-0.144</td>
      <td>-1.5022</td>
      <td>-1.7294</td>
      <td>9.6676</td>
      <td>-15.1272</td>
      <td>...</td>
      <td>-8.8577</td>
      <td>-0.7407</td>
      <td>-5.5384</td>
      <td>-16.3442</td>
      <td>-8.9765</td>
      <td>-5.568</td>
      <td>-37.6522</td>
      <td>-16.1615</td>
      <td>-17.3611</td>
      <td>-2.3932</td>
    </tr>
    <tr>
      <th>20170503</th>
      <td>-9.3964</td>
      <td>-19.0699</td>
      <td>-11.4174</td>
      <td>-4.4972</td>
      <td>-5.7008</td>
      <td>-0.144</td>
      <td>-1.5022</td>
      <td>-1.7294</td>
      <td>9.6676</td>
      <td>-15.1272</td>
      <td>...</td>
      <td>-8.8577</td>
      <td>-0.7407</td>
      <td>-5.5384</td>
      <td>-16.3442</td>
      <td>-8.9765</td>
      <td>-5.568</td>
      <td>-37.6522</td>
      <td>-16.1615</td>
      <td>-17.3611</td>
      <td>-2.3932</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>-9.3964</td>
      <td>-19.0699</td>
      <td>-11.4174</td>
      <td>-4.4972</td>
      <td>-5.7008</td>
      <td>-0.144</td>
      <td>-1.5022</td>
      <td>-1.7294</td>
      <td>9.6676</td>
      <td>-15.1272</td>
      <td>...</td>
      <td>-8.8577</td>
      <td>-0.7407</td>
      <td>-5.5384</td>
      <td>-16.3442</td>
      <td>-8.9765</td>
      <td>-5.568</td>
      <td>-37.6522</td>
      <td>-16.1615</td>
      <td>-17.3611</td>
      <td>-2.3932</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>-9.3964</td>
      <td>-19.0699</td>
      <td>-11.4174</td>
      <td>-4.4972</td>
      <td>-5.7008</td>
      <td>-0.144</td>
      <td>-1.5022</td>
      <td>-1.7294</td>
      <td>9.6676</td>
      <td>-15.1272</td>
      <td>...</td>
      <td>-8.8577</td>
      <td>-0.7407</td>
      <td>-5.5384</td>
      <td>-16.3442</td>
      <td>-8.9765</td>
      <td>-5.568</td>
      <td>-37.6522</td>
      <td>-16.1615</td>
      <td>-17.3611</td>
      <td>-2.3932</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>-9.3964</td>
      <td>-19.0699</td>
      <td>-11.4174</td>
      <td>-4.4972</td>
      <td>-5.7008</td>
      <td>-0.144</td>
      <td>-1.5022</td>
      <td>-1.7294</td>
      <td>9.6676</td>
      <td>-15.1272</td>
      <td>...</td>
      <td>-8.8577</td>
      <td>-0.7407</td>
      <td>-5.5384</td>
      <td>-16.3442</td>
      <td>-8.9765</td>
      <td>-5.568</td>
      <td>-37.6522</td>
      <td>-16.1615</td>
      <td>-17.3611</td>
      <td>-2.3932</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>



###  append_df_symbol

- ` jaqs_fxdayu.data.Dataview.append_df(df, symbol_name, overwrite=False) `

**简要描述：**

- 外部构造一个pandas.DataFrame（含某个新品种的各个字段的信息）,作为新增品种通过此方法添加到数据集中
- 目前，该方法只支持添加日线数据的信息，无法添加季度数据

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|df |是  |pandas.DataFrame，日期为索引，字段名为columns|待添加的数据|
|symbol_name|是  |string|待新增的数据的品种名|
|overwrite |否  |bool|若待新增的品种(symbol_name)与数据集中已有的品种冲突，是否覆盖。默认不覆盖|

**示例：**


```python
df = dv.get("000001.SZ")
df.columns = df.columns.droplevel("symbol")
dv.append_df_symbol(df=df,symbol_name="000001.SZ",overwrite=True)
```

    Symbol [000001.SZ] is overwritten.


## 删除数据

### remove_field

- ` jaqs_fxdayu.data.Dataview.remove_field(field_names) `

**简要描述：**

- 将指定字段从dataview中删除

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|field_names|是  |string|待删除的字段，用","隔开|


**示例：**


```python
print("open" in dv.fields)
dv.remove_field("open")
print("open" in dv.fields)
```

    True
    False


### remove_symbol

- ` jaqs_fxdayu.data.Dataview.remove_symbol(symbols) `

**简要描述：**

- 将指定品种从dataview中删除

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|symbols|是  |string|待删除的品种，用","隔开|


**示例：**


```python
print("000001.SZ" in dv.symbol)
dv.remove_symbol("000001.SZ")
print("000001.SZ" in dv.symbol)
```

    True
    False


## 数据落地

### save_dataview

- ` jaqs_fxdayu.data.Dataview.save_dataview(folder_path) `

**简要描述：**

- 将dataview中的数据保存到本地指定目录(folder_path)下

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|folder_path |是  |string|保存路径|


**示例：**


```python
import os
dataview_folder = './data'

if not (os.path.isdir(dataview_folder)):
    os.makedirs(dataview_folder)
```


```python
dv.save_dataview(dataview_folder)
```

    
    Store data...
    Dataview has been successfully saved to:
    /home/xinger/Desktop/jaqs_plus/jaqs-fxdayu/docs/_source/data
    
    You can load it with load_dataview('/home/xinger/Desktop/jaqs_plus/jaqs-fxdayu/docs/_source/data')


### load_dataview

- ` jaqs_fxdayu.data.Dataview.load_dataview(folder_path) `

**简要描述：**

- 将数据从本地指定目录(folder_path)下加载到dataview中
- 目前仅支持全部加载

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|folder_path |是  |string|加载路径|


**示例：**


```python
dv.load_dataview(dataview_folder)
```

    Dataview loaded successfully.

