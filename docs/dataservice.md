
# RemoteDataService

## 介绍
RemoteDataService是对jaqs底层dataapi的一个高级封装，提供了一些常用数据的快捷查询方法——如K线、交易日历、指数成分信息、行业分类信息等。
RemoteDataService可以通过jaqs官方提供的免费数据源直接从网络获取行情数据和参考数据，需要提前去官网注册账号,方可使用。

* 如需注册账号-[官方网站](https://www.quantos.org/)
* 如需直接使用底层dataapi访问数据-
[jaqs底层dataapi文档-官方](http://jaqs.readthedocs.io/zh_CN/latest/user_guide.html#api)

## 准备工作


*** 步骤: ***

- 1.配置数据下载的tcp地址(data_config)--使用jaqs官方提供的免费数据源需要提前去官网注册账号,方可使用
- 2.引入模块并实例化、初始化RemoteDataService


```python
from jaqs_fxdayu.data import RemoteDataService # 远程数据服务类

# step 1 其中，username password分别对应官网注册的账号和序列号
data_config = {
"remote.data.address": "tcp://data.quantos.org:8910", # 数据服务tcp地址
"remote.data.username": "18566262672",# 账号
"remote.data.password": "eyJhbGciOiJIUzI1NiJ9.eyJjcmVhdGVfdGltZSI6IjE1MTI3MDI3NTAyMTIiLCJpc3MiOiJhdXRoMCIsImlkIjoiMTg1NjYyNjI2NzIifQ.O_-yR0zYagrLRvPbggnru1Rapk4kiyAzcwYt2a3vlpM",
"timeout":180 #超时设置(秒),请求超时会报错
}

# step 2
ds = RemoteDataService()
ds.init_from_config(data_config)
```

    
    Begin: DataApi login 18566262672@tcp://data.quantos.org:8910
        login success 
    





    '0,'



## daily
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.daily(symbol, start_date, end_date, fields="", adjust_mode=None) `

**简要描述：**

- 获取日线行情

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|symbol|是 |string|标的代码，多标的以','隔开，如'000001.SH,600300.SH'|
|start_date |是 |int/str |开始时间 YYYMMDD or 'YYYY-MM-DD'|
|end_date |是 |int/str |结束时间 YYYMMDD or 'YYYY-MM-DD'|
|fields |否 | str |字段 以 ','隔开, 默认 "" (包含所有字段)|
|adjust_mode |否 | str or None |复权方式 None:不复权; 'post':后复权,默认不复权|


** 返回：**

df : pd.DataFrame
   
   columns:
        
        symbol, code, trade_date, open, high, low, close, volume, turnover, vwap, oi, suspended
   
   具体字段含义见quote()方法-返回字段说明

err_msg : str
    error code and error message joined by comma
    
    
**示例：**


```python
df,msg = ds.daily("000001.SH",start_date="2014-01-01",end_date=20150101, adjust_mode="post")
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
      <th>close</th>
      <th>code</th>
      <th>freq</th>
      <th>high</th>
      <th>low</th>
      <th>oi</th>
      <th>open</th>
      <th>presettle</th>
      <th>settle</th>
      <th>symbol</th>
      <th>trade_date</th>
      <th>trade_status</th>
      <th>turnover</th>
      <th>volume</th>
      <th>vwap</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2109.387</td>
      <td>000001</td>
      <td>1d</td>
      <td>2113.110</td>
      <td>2101.016</td>
      <td>NaN</td>
      <td>2112.126</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>000001.SH</td>
      <td>20140102</td>
      <td>交易</td>
      <td>6.192135e+10</td>
      <td>6.848549e+09</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2083.136</td>
      <td>000001</td>
      <td>1d</td>
      <td>2102.167</td>
      <td>2075.899</td>
      <td>NaN</td>
      <td>2101.542</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>000001.SH</td>
      <td>20140103</td>
      <td>交易</td>
      <td>7.237223e+10</td>
      <td>8.449724e+09</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2045.709</td>
      <td>000001</td>
      <td>1d</td>
      <td>2078.684</td>
      <td>2034.006</td>
      <td>NaN</td>
      <td>2078.684</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>000001.SH</td>
      <td>20140106</td>
      <td>交易</td>
      <td>7.289539e+10</td>
      <td>8.958761e+09</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2047.317</td>
      <td>000001</td>
      <td>1d</td>
      <td>2052.279</td>
      <td>2029.246</td>
      <td>NaN</td>
      <td>2034.224</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>000001.SH</td>
      <td>20140107</td>
      <td>交易</td>
      <td>5.463864e+10</td>
      <td>6.340294e+09</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2044.340</td>
      <td>000001</td>
      <td>1d</td>
      <td>2062.952</td>
      <td>2037.110</td>
      <td>NaN</td>
      <td>2047.256</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>000001.SH</td>
      <td>20140108</td>
      <td>交易</td>
      <td>6.294143e+10</td>
      <td>7.164736e+09</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
</div>



## bar
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.bar(*args, **kwargs) `

**简要描述：**

- 获取分钟线行情（不含ask，bid信息）

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|symbol|是 |string|标的代码，多标的以','隔开，如'000001.SH,600300.SH'|
|start_time |否 |int (HHMMSS) or str ('HH:MM:SS') |开始时间 默认开盘时间按|
|end_time |否 int (HHMMSS) or str ('HH:MM:SS') |结束时间 默认收盘时间|
|trade_date|是 | int (YYYMMDD) or str ('YYYY-MM-DD') |交易日|
|fields |否 | str |字段 以 ','隔开, 默认 "" (包含所有字段)|
|freq |否 | str（'1M', '5M', '15M'） |分钟bar类型，默认1M(1分钟)|


** 返回：**

df : pd.DataFrame
   
   columns:
        
        symbol, code, date, time, trade_date, freq, open, high, low, close, volume, turnover, vwap, oi
        
   具体字段含义见quote()方法-返回字段说明

err_msg : str
    error code and error message joined by comma
    
    
**示例：**


```python
df,msg = ds.bar("000001.SZ,000002.SZ", trade_date =20180328,  freq="1M")
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
      <th>close</th>
      <th>code</th>
      <th>date</th>
      <th>freq</th>
      <th>high</th>
      <th>low</th>
      <th>oi</th>
      <th>open</th>
      <th>settle</th>
      <th>symbol</th>
      <th>time</th>
      <th>trade_date</th>
      <th>turnover</th>
      <th>volume</th>
      <th>vwap</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>10.86</td>
      <td>000001</td>
      <td>20180328</td>
      <td>1M</td>
      <td>10.86</td>
      <td>10.84</td>
      <td>NaN</td>
      <td>10.85</td>
      <td>NaN</td>
      <td>000001.SZ</td>
      <td>93100</td>
      <td>20180328</td>
      <td>17128195.0</td>
      <td>1579138.0</td>
      <td>10.846547</td>
    </tr>
    <tr>
      <th>1</th>
      <td>10.89</td>
      <td>000001</td>
      <td>20180328</td>
      <td>1M</td>
      <td>10.89</td>
      <td>10.86</td>
      <td>NaN</td>
      <td>10.86</td>
      <td>NaN</td>
      <td>000001.SZ</td>
      <td>93200</td>
      <td>20180328</td>
      <td>10527285.0</td>
      <td>968044.0</td>
      <td>10.874800</td>
    </tr>
    <tr>
      <th>2</th>
      <td>10.88</td>
      <td>000001</td>
      <td>20180328</td>
      <td>1M</td>
      <td>10.89</td>
      <td>10.87</td>
      <td>NaN</td>
      <td>10.88</td>
      <td>NaN</td>
      <td>000001.SZ</td>
      <td>93300</td>
      <td>20180328</td>
      <td>9965762.0</td>
      <td>916456.0</td>
      <td>10.874239</td>
    </tr>
    <tr>
      <th>3</th>
      <td>10.86</td>
      <td>000001</td>
      <td>20180328</td>
      <td>1M</td>
      <td>10.89</td>
      <td>10.86</td>
      <td>NaN</td>
      <td>10.87</td>
      <td>NaN</td>
      <td>000001.SZ</td>
      <td>93400</td>
      <td>20180328</td>
      <td>7912778.0</td>
      <td>728400.0</td>
      <td>10.863232</td>
    </tr>
    <tr>
      <th>4</th>
      <td>10.86</td>
      <td>000001</td>
      <td>20180328</td>
      <td>1M</td>
      <td>10.87</td>
      <td>10.86</td>
      <td>NaN</td>
      <td>10.86</td>
      <td>NaN</td>
      <td>000001.SZ</td>
      <td>93500</td>
      <td>20180328</td>
      <td>3930566.0</td>
      <td>361800.0</td>
      <td>10.863919</td>
    </tr>
  </tbody>
</table>
</div>



## quote
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.quote(symbol, fields="") `

**简要描述：**

- 查询最新市场行情

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|symbol|是 |string|标的代码，多标的以','隔开，如'000001.SH,600300.SH'|
|fields |否 | str |需要返回字段，多字段以','隔开；为""时返回所有字段|

** 返回：**

df : pd.DataFrame

err_msg : str
    error code and error message joined by comma
    
** 返回字段说明：**

|字段|类型|说明|
|:----    |:---|----- |
|symbol	|string	|标的代码|
|code|tring	|交易所原始代码|
|date	|int	|自然日,YYYYMMDD格式，如20170823|
|time	|int	|时间，精确到毫秒，如14:21:05.330记为142105330|
|trade_date|	int|	YYYYMMDD格式，如20170823|
|open	|double	|开盘价|
|high	|double|	最高价|
|low	|double|	最低价|
|last	|double|	最新价|
|close	|double	|收盘价|
|volume|	double	|成交量（总）|
|turnover	|double|	成交金额（总）|
|vwap	|double	|截止到行情时间的日内成交均价|
|oi	|double	|持仓总量|
|settle	|double	|今结算价|
|iopv	|double|	净值估值|
|limit_up	|double|	涨停价|
|limit_down|	double|	跌停价|
|preclose	|double	|昨收盘价|
|presettle	|double	|昨结算价|
|preoi	|double	|昨持仓|
|askprice1	|double|	申卖价1|
|askprice2	|double|	申卖价2|
|askprice3	|double	|申卖价3|
|askprice4	|double|	申卖价4|
|askprice5	|double	|申卖价5|
|bidprice1	|double	|申买价1|
|bidprice2	|double	|申买价2|
|bidprice3	|double	|申买价3|
|bidprice4	|double|	申买价4|
|bidprice5	|double	|申买价5|
|askvolume1	|double	|申卖量1|
|askvolume2	|double	|申卖量2|
|askvolume3|	double	|申卖量3|
|askvolume4	|double	|申卖量4|
|askvolume5	|double	|申卖量5|
|bidvolume1|double	|申买量1|
|bidvolume2|	double|	申买量2|
|bidvolume3|	double|	申买量3|
|bidvolume4|	double|	申买量4|
|bidvolume5|	double|	申买量5|
    
    
**示例：**


```python
df,msg = ds.quote("000001.SZ,000002.SZ")
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
      <th>ask1_premium</th>
      <th>askprice1</th>
      <th>askprice10</th>
      <th>askprice2</th>
      <th>askprice3</th>
      <th>askprice4</th>
      <th>askprice5</th>
      <th>askprice6</th>
      <th>askprice7</th>
      <th>askprice8</th>
      <th>...</th>
      <th>preclose</th>
      <th>preoi</th>
      <th>presettle</th>
      <th>settle</th>
      <th>symbol</th>
      <th>time</th>
      <th>trade_date</th>
      <th>turnover</th>
      <th>volume</th>
      <th>vwap</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>000001.SZ</th>
      <td>NaN</td>
      <td>11.05</td>
      <td>0.0</td>
      <td>11.06</td>
      <td>11.07</td>
      <td>11.08</td>
      <td>11.09</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>10.89</td>
      <td>0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>000001.SZ</td>
      <td>150003000</td>
      <td>20180329</td>
      <td>1.445282e+09</td>
      <td>133060238</td>
      <td>10.861861</td>
    </tr>
    <tr>
      <th>000002.SZ</th>
      <td>NaN</td>
      <td>34.16</td>
      <td>0.0</td>
      <td>34.17</td>
      <td>34.18</td>
      <td>34.19</td>
      <td>34.20</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>31.33</td>
      <td>0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>000002.SZ</td>
      <td>150003000</td>
      <td>20180329</td>
      <td>3.311803e+09</td>
      <td>99970072</td>
      <td>33.127942</td>
    </tr>
  </tbody>
</table>
<p>2 rows × 62 columns</p>
</div>



## bar_quote
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.bar_quote(*args, **kwargs) `

**简要描述：**

- 获取分钟线行情（含最近的quote信息）

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|symbol|是 |string|标的代码，多标的以','隔开，如'000001.SH,600300.SH'|
|start_time |否 |int (HHMMSS) or str ('HH:MM:SS') |开始时间 默认开盘时间按|
|end_time |否 int (HHMMSS) or str ('HH:MM:SS') |结束时间 默认收盘时间|
|trade_date|是 | int (YYYMMDD) or str ('YYYY-MM-DD') |交易日|
|fields |否 | str |字段 以 ','隔开, 默认 "" (包含所有字段)|
|freq |否 | str（'1M', '5M', '15M'） |分钟bar类型，默认1M(1分钟)|


** 返回：**

df : pd.DataFrame
    
    具体字段含义见quote()方法-返回字段说明

err_msg : str
    error code and error message joined by comma
    
    
**示例：**


```python
df,msg = ds.bar_quote("000001.SZ,000002.SZ", trade_date =20180328,  freq="1M")
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
      <th>askprice1</th>
      <th>askprice2</th>
      <th>askprice3</th>
      <th>askprice4</th>
      <th>askprice5</th>
      <th>askvolume1</th>
      <th>askvolume2</th>
      <th>askvolume3</th>
      <th>askvolume4</th>
      <th>askvolume5</th>
      <th>...</th>
      <th>low</th>
      <th>oi</th>
      <th>open</th>
      <th>settle</th>
      <th>symbol</th>
      <th>time</th>
      <th>trade_date</th>
      <th>turnover</th>
      <th>volume</th>
      <th>vwap</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>10.87</td>
      <td>10.88</td>
      <td>10.89</td>
      <td>10.90</td>
      <td>10.91</td>
      <td>64900.0</td>
      <td>259144.0</td>
      <td>14800.0</td>
      <td>47100.0</td>
      <td>2400.0</td>
      <td>...</td>
      <td>10.84</td>
      <td>NaN</td>
      <td>10.85</td>
      <td>NaN</td>
      <td>000001.SZ</td>
      <td>93100</td>
      <td>20180328</td>
      <td>17128195.0</td>
      <td>1579138.0</td>
      <td>10.846547</td>
    </tr>
    <tr>
      <th>1</th>
      <td>10.90</td>
      <td>10.91</td>
      <td>10.92</td>
      <td>10.93</td>
      <td>10.94</td>
      <td>58900.0</td>
      <td>16800.0</td>
      <td>194100.0</td>
      <td>10020.0</td>
      <td>80600.0</td>
      <td>...</td>
      <td>10.86</td>
      <td>NaN</td>
      <td>10.86</td>
      <td>NaN</td>
      <td>000001.SZ</td>
      <td>93200</td>
      <td>20180328</td>
      <td>10527285.0</td>
      <td>968044.0</td>
      <td>10.874800</td>
    </tr>
    <tr>
      <th>2</th>
      <td>10.88</td>
      <td>10.89</td>
      <td>10.90</td>
      <td>10.91</td>
      <td>10.92</td>
      <td>13300.0</td>
      <td>46374.0</td>
      <td>70500.0</td>
      <td>134600.0</td>
      <td>195200.0</td>
      <td>...</td>
      <td>10.87</td>
      <td>NaN</td>
      <td>10.88</td>
      <td>NaN</td>
      <td>000001.SZ</td>
      <td>93300</td>
      <td>20180328</td>
      <td>9965762.0</td>
      <td>916456.0</td>
      <td>10.874239</td>
    </tr>
    <tr>
      <th>3</th>
      <td>10.86</td>
      <td>10.87</td>
      <td>10.88</td>
      <td>10.89</td>
      <td>10.90</td>
      <td>27600.0</td>
      <td>24200.0</td>
      <td>211300.0</td>
      <td>86074.0</td>
      <td>95500.0</td>
      <td>...</td>
      <td>10.86</td>
      <td>NaN</td>
      <td>10.87</td>
      <td>NaN</td>
      <td>000001.SZ</td>
      <td>93400</td>
      <td>20180328</td>
      <td>7912778.0</td>
      <td>728400.0</td>
      <td>10.863232</td>
    </tr>
    <tr>
      <th>4</th>
      <td>10.87</td>
      <td>10.88</td>
      <td>10.89</td>
      <td>10.90</td>
      <td>10.91</td>
      <td>140600.0</td>
      <td>167900.0</td>
      <td>85974.0</td>
      <td>83300.0</td>
      <td>128700.0</td>
      <td>...</td>
      <td>10.86</td>
      <td>NaN</td>
      <td>10.86</td>
      <td>NaN</td>
      <td>000001.SZ</td>
      <td>93500</td>
      <td>20180328</td>
      <td>3930566.0</td>
      <td>361800.0</td>
      <td>10.863919</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 35 columns</p>
</div>



## query
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.query(view, filter="", fields="", **kwargs) `

**简要描述：**

- 获取各种参考数据，直接继承自底层dataapi.query 
- 使用方法详见[基础数据获取方法](http://jaqs.readthedocs.io/zh_CN/latest/user_guide.html#id10)

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|view|是 |string|参考数据的api名称,如"jz.instrumentInfo"(证券基础信息),"help.apiList"(帮助列表)|
|filter|否 |string|过滤条件|
|fields |否 | str |字段 以 ','隔开, 默认 ""|



** 返回：**

df : pd.DataFrame

err_msg : str
    error code and error message joined by comma
    
    
**示例：**

## 查询帮助文档

- 目前，可查询到的帮助文档并不完整，常用的参考数据api如'lb.finIndicator'(金融指标),"lb.profitExpress"（业绩快报）,"lb.secDailyIndicator"(日行情估值)等api无法查询字段细节


```python
df , msg = ds.query(
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



## 查询帮助文档细节-可选字段


```python
df ,msg = ds.query(view="help.apiParam",fields="",filter="api=jy.cashFlow") # 查询现金流量表可选字段
df.tail()
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
      <th>62</th>
      <td>jy.cashFlow</td>
      <td></td>
      <td>Double</td>
      <td>N</td>
      <td>others</td>
      <td>其他</td>
      <td>OUT</td>
    </tr>
    <tr>
      <th>63</th>
      <td>jy.cashFlow</td>
      <td></td>
      <td>Double</td>
      <td>N</td>
      <td>conv_debt_into_cap</td>
      <td>债务转为资本</td>
      <td>OUT</td>
    </tr>
    <tr>
      <th>64</th>
      <td>jy.cashFlow</td>
      <td></td>
      <td>Double</td>
      <td>N</td>
      <td>conv_corp_bonds_due_within_1y</td>
      <td>一年内到期的可转换公司债券</td>
      <td>OUT</td>
    </tr>
    <tr>
      <th>65</th>
      <td>jy.cashFlow</td>
      <td></td>
      <td>Double</td>
      <td>N</td>
      <td>fa_fnc_leases</td>
      <td>融资租入固定资产</td>
      <td>OUT</td>
    </tr>
    <tr>
      <th>66</th>
      <td>jy.cashFlow</td>
      <td></td>
      <td>Double</td>
      <td>N</td>
      <td>end_bal_cash</td>
      <td>现金的期末余额</td>
      <td>OUT</td>
    </tr>
  </tbody>
</table>
</div>



## query_lb_fin_stat
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.query_lb_fin_stat(*args, **kwargs) `

**简要描述：**

- 获取基本面财务数据

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|type_|是 |string|财务指标类型 'income', 'balance_sheet', 'cash_flow'，'fin_indicator'|
|symbol|是 |string|标的代码，多标的以','隔开，如'000001.SH,600300.SH'|
|start_date |是 |int |开始时间 YYYMMDD|
|end_date |是 |int |结束时间 YYYMMDD|
|fields |否 | str |字段 以 ','隔开, 默认 "" |
|drop_dup_cols |否 | list or tuple |是否删除重复的输入|

** 返回：**

df : pd.DataFrame

err_msg : str
    error code and error message joined by comma
    
    
**示例：**


```python
df,msg = ds.query_lb_fin_stat(type_='cash_flow', 
                              symbol="000001.SZ,000002.SZ",
                              start_date=20100101,
                              end_date=20120101, 
                              fields="conv_corp_bonds_due_within_1y")
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
      <th>ann_date</th>
      <th>cash_recp_prem_orig_inco</th>
      <th>cash_recp_return_invest</th>
      <th>cash_recp_sg_and_rs</th>
      <th>conv_corp_bonds_due_within_1y</th>
      <th>incl_dvd_profit_paid_sc_ms</th>
      <th>net_cash_flows_inv_act</th>
      <th>net_cash_received_reinsu_bus</th>
      <th>net_incr_dep_cob</th>
      <th>net_incr_disp_tfa</th>
      <th>...</th>
      <th>net_incr_int_handling_chrg</th>
      <th>net_incr_loans_central_bank</th>
      <th>other_cash_recp_ral_fnc_act</th>
      <th>other_cash_recp_ral_oper_act</th>
      <th>recp_tax_rends</th>
      <th>report_date</th>
      <th>report_type</th>
      <th>stot_cash_inflows_oper_act</th>
      <th>stot_cash_outflows_oper_act</th>
      <th>symbol</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>20100312</td>
      <td>0.0</td>
      <td>2.490274e+09</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>-1.564121e+10</td>
      <td>0.0</td>
      <td>1.321978e+11</td>
      <td>0.0</td>
      <td>...</td>
      <td>2.071380e+10</td>
      <td>0.000000e+00</td>
      <td>0.0</td>
      <td>1.459726e+09</td>
      <td>0.0</td>
      <td>20091231</td>
      <td>408001000</td>
      <td>1.577535e+11</td>
      <td>1.255598e+11</td>
      <td>000001.SZ</td>
    </tr>
    <tr>
      <th>1</th>
      <td>20100825</td>
      <td>0.0</td>
      <td>1.426558e+09</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>-1.838394e+09</td>
      <td>0.0</td>
      <td>2.535334e+10</td>
      <td>0.0</td>
      <td>...</td>
      <td>1.146239e+10</td>
      <td>1.203900e+09</td>
      <td>0.0</td>
      <td>1.991992e+09</td>
      <td>0.0</td>
      <td>20100630</td>
      <td>408001000</td>
      <td>4.052371e+10</td>
      <td>4.355715e+10</td>
      <td>000001.SZ</td>
    </tr>
    <tr>
      <th>2</th>
      <td>20110225</td>
      <td>0.0</td>
      <td>3.275000e+09</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>-1.466054e+10</td>
      <td>0.0</td>
      <td>1.165075e+11</td>
      <td>0.0</td>
      <td>...</td>
      <td>2.120694e+10</td>
      <td>2.218199e+09</td>
      <td>0.0</td>
      <td>3.069659e+09</td>
      <td>0.0</td>
      <td>20101231</td>
      <td>408001000</td>
      <td>1.486299e+11</td>
      <td>1.268836e+11</td>
      <td>000001.SZ</td>
    </tr>
    <tr>
      <th>3</th>
      <td>20111026</td>
      <td>0.0</td>
      <td>3.411571e+09</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>-3.427133e+10</td>
      <td>0.0</td>
      <td>1.152976e+11</td>
      <td>0.0</td>
      <td>...</td>
      <td>2.676739e+10</td>
      <td>0.000000e+00</td>
      <td>0.0</td>
      <td>1.981977e+09</td>
      <td>0.0</td>
      <td>20110930</td>
      <td>408001000</td>
      <td>2.234589e+11</td>
      <td>2.055972e+11</td>
      <td>000001.SZ</td>
    </tr>
    <tr>
      <th>4</th>
      <td>20100429</td>
      <td>0.0</td>
      <td>3.056250e+08</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>-6.750866e+09</td>
      <td>0.0</td>
      <td>2.956215e+10</td>
      <td>0.0</td>
      <td>...</td>
      <td>5.525798e+09</td>
      <td>0.000000e+00</td>
      <td>0.0</td>
      <td>1.514769e+09</td>
      <td>0.0</td>
      <td>20100331</td>
      <td>408001000</td>
      <td>3.956118e+10</td>
      <td>3.095155e+10</td>
      <td>000001.SZ</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 22 columns</p>
</div>



## query_lb_dailyindicator
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.query_lb_dailyindicator(symbol, start_date, end_date, fields="") `

**简要描述：**

- 获取日行情估值数据

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|symbol|是 |string|标的代码，多标的以','隔开，如'000001.SH,600300.SH'|
|start_date |是 |int |开始时间 YYYMMDD|
|end_date |是 |int |结束时间 YYYMMDD|
|fields |是| str |字段 以 ','隔开|


- fields为必须参数,可选字段包括："total_mv", "float_mv", "pe", "pb", "pe_ttm", "pcf_ocf", "pcf_ocfttm", "pcf_ncf","pcf_ncfttm", "ps", "ps_ttm", "turnover_ratio", "free_turnover_ratio", "total_share","float_share", "price_div_dps", "free_share", "np_parent_comp_ttm","np_parent_comp_lyr", "net_assets", "ncf_oper_ttm", "ncf_oper_lyr", "oper_rev_ttm", "oper_rev_lyr", "limit_status" 暂无详细释义

** 返回：**

df : pd.DataFrame

err_msg : str
    error code and error message joined by comma
    
    
**示例：**


```python
df,msg = ds.query_lb_dailyindicator(
                              symbol="000001.SZ,000002.SZ",
                              start_date=20100101,
                              end_date=20120101, 
                              fields="pb,pe,ps,pcf_ocf,float_mv,total_mv,net_assets,price_div_dps,limit_status")
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
      <th>float_mv</th>
      <th>limit_status</th>
      <th>net_assets</th>
      <th>pb</th>
      <th>pcf_ocf</th>
      <th>pe</th>
      <th>price_div_dps</th>
      <th>ps</th>
      <th>symbol</th>
      <th>total_mv</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>7.126066e+06</td>
      <td>0</td>
      <td>1.908844e+10</td>
      <td>3.9647</td>
      <td>3.1089</td>
      <td>123.2494</td>
      <td>0.0</td>
      <td>5.2146</td>
      <td>000001.SZ</td>
      <td>7.567942e+06</td>
    </tr>
    <tr>
      <th>1</th>
      <td>7.126066e+06</td>
      <td>0</td>
      <td>1.908844e+10</td>
      <td>3.9647</td>
      <td>3.1089</td>
      <td>123.2494</td>
      <td>0.0</td>
      <td>5.2146</td>
      <td>000001.SZ</td>
      <td>7.567942e+06</td>
    </tr>
    <tr>
      <th>2</th>
      <td>7.126066e+06</td>
      <td>0</td>
      <td>1.908844e+10</td>
      <td>3.9647</td>
      <td>3.1089</td>
      <td>123.2494</td>
      <td>0.0</td>
      <td>5.2146</td>
      <td>000001.SZ</td>
      <td>7.567942e+06</td>
    </tr>
    <tr>
      <th>3</th>
      <td>6.933075e+06</td>
      <td>0</td>
      <td>1.908844e+10</td>
      <td>3.8573</td>
      <td>3.0247</td>
      <td>119.9115</td>
      <td>0.0</td>
      <td>5.0733</td>
      <td>000001.SZ</td>
      <td>7.362983e+06</td>
    </tr>
    <tr>
      <th>4</th>
      <td>6.813186e+06</td>
      <td>0</td>
      <td>1.908844e+10</td>
      <td>3.7906</td>
      <td>2.9724</td>
      <td>117.8379</td>
      <td>0.0</td>
      <td>4.9856</td>
      <td>000001.SZ</td>
      <td>7.235661e+06</td>
    </tr>
  </tbody>
</table>
</div>



## query_index_weights_raw
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.query_index_weights_raw(index, trade_date) `

**简要描述：**

- 获取指数某一天的成分股和对应权重

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|index|是 |string|指数代码,只支持单标的|
|trade_date |是 |int |交易日|



** 返回：**

df : pd.DataFrame
    
**示例：**


```python
df = ds.query_index_weights_raw('000300.SH',trade_date = 20180328)
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
      <th>index_code</th>
      <th>trade_date</th>
      <th>weight</th>
    </tr>
    <tr>
      <th>symbol</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>000001.SZ</th>
      <td>399300.SZ</td>
      <td>20180301</td>
      <td>0.008772</td>
    </tr>
    <tr>
      <th>000002.SZ</th>
      <td>399300.SZ</td>
      <td>20180301</td>
      <td>0.013372</td>
    </tr>
    <tr>
      <th>000008.SZ</th>
      <td>399300.SZ</td>
      <td>20180301</td>
      <td>0.001079</td>
    </tr>
    <tr>
      <th>000060.SZ</th>
      <td>399300.SZ</td>
      <td>20180301</td>
      <td>0.001433</td>
    </tr>
    <tr>
      <th>000063.SZ</th>
      <td>399300.SZ</td>
      <td>20180301</td>
      <td>0.006531</td>
    </tr>
  </tbody>
</table>
</div>



## query_index_weights_daily
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.query_index_weights_daily(index, start_date, end_date) `

**简要描述：**

- 获取指数某段时期内左右的成分股权重

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|index|是 |string|指数代码,只支持单标的|
|start_date |是 |int |开始时间 YYMMDD|
|end_date |是 |int |结束时间 YYMMDD|



** 返回：**

df : pd.DataFrame
    
**示例：**


```python
df = ds.query_index_weights_daily('000300.SH',start_date=20171231,end_date= 20180328)
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
      <th>symbol</th>
      <th>000001.SZ</th>
      <th>000002.SZ</th>
      <th>000008.SZ</th>
      <th>000060.SZ</th>
      <th>000063.SZ</th>
      <th>000069.SZ</th>
      <th>000100.SZ</th>
      <th>000157.SZ</th>
      <th>000166.SZ</th>
      <th>000333.SZ</th>
      <th>...</th>
      <th>601989.SH</th>
      <th>601991.SH</th>
      <th>601992.SH</th>
      <th>601997.SH</th>
      <th>601998.SH</th>
      <th>603160.SH</th>
      <th>603799.SH</th>
      <th>603833.SH</th>
      <th>603858.SH</th>
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
      <th>20180102</th>
      <td>0.009884</td>
      <td>0.013303</td>
      <td>0.001246</td>
      <td>0.001579</td>
      <td>0.007143</td>
      <td>0.002455</td>
      <td>0.002664</td>
      <td>0.001669</td>
      <td>0.00272</td>
      <td>0.021523</td>
      <td>...</td>
      <td>0.004842</td>
      <td>0.001056</td>
      <td>0.001567</td>
      <td>0.001581</td>
      <td>0.001628</td>
      <td>0.000375</td>
      <td>0.002016</td>
      <td>0.000429</td>
      <td>0.000323</td>
      <td>0.001545</td>
    </tr>
    <tr>
      <th>20180103</th>
      <td>0.009884</td>
      <td>0.013303</td>
      <td>0.001246</td>
      <td>0.001579</td>
      <td>0.007143</td>
      <td>0.002455</td>
      <td>0.002664</td>
      <td>0.001669</td>
      <td>0.00272</td>
      <td>0.021523</td>
      <td>...</td>
      <td>0.004842</td>
      <td>0.001056</td>
      <td>0.001567</td>
      <td>0.001581</td>
      <td>0.001628</td>
      <td>0.000375</td>
      <td>0.002016</td>
      <td>0.000429</td>
      <td>0.000323</td>
      <td>0.001545</td>
    </tr>
    <tr>
      <th>20180104</th>
      <td>0.009884</td>
      <td>0.013303</td>
      <td>0.001246</td>
      <td>0.001579</td>
      <td>0.007143</td>
      <td>0.002455</td>
      <td>0.002664</td>
      <td>0.001669</td>
      <td>0.00272</td>
      <td>0.021523</td>
      <td>...</td>
      <td>0.004842</td>
      <td>0.001056</td>
      <td>0.001567</td>
      <td>0.001581</td>
      <td>0.001628</td>
      <td>0.000375</td>
      <td>0.002016</td>
      <td>0.000429</td>
      <td>0.000323</td>
      <td>0.001545</td>
    </tr>
    <tr>
      <th>20180105</th>
      <td>0.009884</td>
      <td>0.013303</td>
      <td>0.001246</td>
      <td>0.001579</td>
      <td>0.007143</td>
      <td>0.002455</td>
      <td>0.002664</td>
      <td>0.001669</td>
      <td>0.00272</td>
      <td>0.021523</td>
      <td>...</td>
      <td>0.004842</td>
      <td>0.001056</td>
      <td>0.001567</td>
      <td>0.001581</td>
      <td>0.001628</td>
      <td>0.000375</td>
      <td>0.002016</td>
      <td>0.000429</td>
      <td>0.000323</td>
      <td>0.001545</td>
    </tr>
    <tr>
      <th>20180108</th>
      <td>0.009884</td>
      <td>0.013303</td>
      <td>0.001246</td>
      <td>0.001579</td>
      <td>0.007143</td>
      <td>0.002455</td>
      <td>0.002664</td>
      <td>0.001669</td>
      <td>0.00272</td>
      <td>0.021523</td>
      <td>...</td>
      <td>0.004842</td>
      <td>0.001056</td>
      <td>0.001567</td>
      <td>0.001581</td>
      <td>0.001628</td>
      <td>0.000375</td>
      <td>0.002016</td>
      <td>0.000429</td>
      <td>0.000323</td>
      <td>0.001545</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 300 columns</p>
</div>



## query_index_member
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.query_index_member(index, start_date, end_date) `

**简要描述：**

- 获取指数某段时间内的成分股代码

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|index|是 |string|指数代码,只支持单标的|
|start_date |是 |int |开始时间 YYMMDD|
|end_date |是 |int |结束时间 YYMMDD|


** 返回：**

list
    
**示例：**


```python
df = ds.query_index_member('000300.SH',start_date=20171231,end_date= 20180328)
df[:5]
```




    ['000001.SZ', '000002.SZ', '000008.SZ', '000060.SZ', '000063.SZ']



## query_index_member_daily
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.query_index_member_daily(index, start_date, end_date) `

**简要描述：**

- 获取指数某段时间内的成分股及具体某天该成分股是否在其中

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|index|是 |string|指数代码,只支持单标的|
|start_date |是 |int |开始时间 YYMMDD|
|end_date |是 |int |结束时间 YYMMDD|


** 返回：**

 df : pd.DataFrame
    
        index dates, columns all securities that have ever been components,
        values are 0 (not in) or 1 (in)
    
**示例：**


```python
df = ds.query_index_member_daily('000300.SH',start_date=20171231,end_date= 20180328)
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
      <th>000001.SZ</th>
      <th>000002.SZ</th>
      <th>000008.SZ</th>
      <th>000060.SZ</th>
      <th>000063.SZ</th>
      <th>000069.SZ</th>
      <th>000100.SZ</th>
      <th>000157.SZ</th>
      <th>000166.SZ</th>
      <th>000333.SZ</th>
      <th>...</th>
      <th>601989.SH</th>
      <th>601991.SH</th>
      <th>601992.SH</th>
      <th>601997.SH</th>
      <th>601998.SH</th>
      <th>603160.SH</th>
      <th>603799.SH</th>
      <th>603833.SH</th>
      <th>603858.SH</th>
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
      <th>20180102</th>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>...</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>20180103</th>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>...</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>20180104</th>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>...</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>20180105</th>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>...</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>20180108</th>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>...</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 300 columns</p>
</div>



## query_industry_daily
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.query_industry_daily(symbol, start_date, end_date, type_='SW', level=1) `

**简要描述：**

- 指定一系列股票，获取它们在某段时间的行业分类代码

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|symbol|是 |string|标的代码，多标的以','隔开，如'000001.SZ,000002.SZ'|
|start_date |是 |int |开始时间 YYYMMDD|
|end_date |是 |int |结束时间 YYYMMDD|
|type_ |否|string| 行业分类标准 目前支持"SW"（申万）,"ZZ"（中证）,"ZJH"（证监会），默认"SW"|
|level |否|int| 行业等级 默认1|


** 返回：**

 df : pd.DataFrame
    
        index dates, columns symbols
        values are industry code
    
**示例：**


```python
df = ds.query_industry_daily('000001.SZ,000002.SZ',start_date=20171231,end_date= 20180328,
                            type_="ZJH",level=2)
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
      <th>000001.SZ</th>
      <th>000002.SZ</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>20180102</th>
      <td>J66</td>
      <td>K70</td>
    </tr>
    <tr>
      <th>20180103</th>
      <td>J66</td>
      <td>K70</td>
    </tr>
    <tr>
      <th>20180104</th>
      <td>J66</td>
      <td>K70</td>
    </tr>
    <tr>
      <th>20180105</th>
      <td>J66</td>
      <td>K70</td>
    </tr>
    <tr>
      <th>20180108</th>
      <td>J66</td>
      <td>K70</td>
    </tr>
  </tbody>
</table>
</div>



## query_industry_raw
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.query_industry_raw(symbol, type_='SW', level=1) `

**简要描述：**

- 指定一系列股票，获取它们的行业分类代码

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|symbol|是 |string|标的代码，多标的以','隔开，如'000001.SZ,000002.SZ'|
|type_ |否|string| 行业分类标准 目前支持"SW"（申万）,"ZZ"（中证）,"ZJH"（证监会），默认"SW"|
|level |否|int| 行业等级 默认1|


** 返回：**

 df : pd.DataFrame
    
    
**示例：**


```python
df = ds.query_industry_raw('000001.SZ,000002.SZ',
                            type_="ZJH",level=2)
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
      <th>in_date</th>
      <th>industry1_code</th>
      <th>industry1_name</th>
      <th>industry2_code</th>
      <th>industry2_name</th>
      <th>industry3_code</th>
      <th>industry3_name</th>
      <th>industry4_code</th>
      <th>industry4_name</th>
      <th>industry_src</th>
      <th>out_date</th>
      <th>symbol</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>20121231</td>
      <td>J</td>
      <td>金融业</td>
      <td>J66</td>
      <td>货币金融服务</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>zjh</td>
      <td></td>
      <td>000001.SZ</td>
    </tr>
    <tr>
      <th>1</th>
      <td>20121231</td>
      <td>K</td>
      <td>房地产业</td>
      <td>K70</td>
      <td>房地产业</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>zjh</td>
      <td></td>
      <td>000002.SZ</td>
    </tr>
  </tbody>
</table>
</div>



## query_adj_factor_daily
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.query_adj_factor_daily(symbol, start_date, end_date, div=False) `

**简要描述：**

- 查询股票复权因子

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|symbol|是 |string|标的代码，多标的以','隔开，如'000001.SZ,000002.SZ'|
|start_date |是 |int |开始时间 YYYMMDD|
|end_date |是 |int |结束时间 YYYMMDD|
|div|否|bool|是否返回相对前一日复权因子的比值，默认False(原复权因子)|



** 返回：**

 df : pd.DataFrame



```python
df = ds.query_adj_factor_daily('000001.SZ,000002.SZ',
                               start_date=20150101,end_date=20160101,
                               div=False)
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
      <th>000001.SZ</th>
      <th>000002.SZ</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>20150105</th>
      <td>68.1803</td>
      <td>114.776</td>
    </tr>
    <tr>
      <th>20150106</th>
      <td>68.1803</td>
      <td>114.776</td>
    </tr>
    <tr>
      <th>20150107</th>
      <td>68.1803</td>
      <td>114.776</td>
    </tr>
    <tr>
      <th>20150108</th>
      <td>68.1803</td>
      <td>114.776</td>
    </tr>
    <tr>
      <th>20150109</th>
      <td>68.1803</td>
      <td>114.776</td>
    </tr>
  </tbody>
</table>
</div>



## query_dividend
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.query_dividend(symbol, start_date, end_date) `

**简要描述：**

- 查询分红送股信息

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|symbol|是 |string|标的代码，多标的以','隔开，如'000001.SZ,000002.SZ'|
|start_date |是 |int |开始时间 YYYMMDD|
|end_date |是 |int |结束时间 YYYMMDD|


** 返回：**

df : pd.DataFrame

err_msg : str
    error code and error message joined by comma



```python
df,msg = ds.query_dividend('000001.SZ,000002.SZ',
                           start_date=20150101,end_date=20160101)
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
      <th>ann_date</th>
      <th>bonus_list_date</th>
      <th>cash</th>
      <th>cash_tax</th>
      <th>cashpay_date</th>
      <th>div_enddate</th>
      <th>exdiv_date</th>
      <th>publish_date</th>
      <th>record_date</th>
      <th>share_ratio</th>
      <th>share_trans_ratio</th>
      <th>symbol</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>20150313</td>
      <td>20150413</td>
      <td>0.174</td>
      <td>0.1653</td>
      <td>20150413</td>
      <td>20141231</td>
      <td>20150413</td>
      <td>20150407</td>
      <td>20150410</td>
      <td>0.0</td>
      <td>0.2</td>
      <td>000001.SZ</td>
    </tr>
    <tr>
      <th>1</th>
      <td>20150331</td>
      <td></td>
      <td>0.500</td>
      <td>0.4750</td>
      <td>20150721</td>
      <td>20141231</td>
      <td>20150721</td>
      <td>20150714</td>
      <td>20150720</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>000002.SZ</td>
    </tr>
  </tbody>
</table>
</div>



## query_inst_info
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.query_inst_info(symbol, inst_type="", fields="") `

**简要描述：**

- 查询证券基本信息

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|symbol|是 |string|标的代码，多标的以','隔开，如'000001.SZ,000002.SZ'|
|inst_type |否 |string |证券类型 "1,2,3,4,5,100,101,102,103,104",默认全部|
|fields |是| str |字段 以 ','隔开，默认""|


** 返回：**

df : pd.DataFrame

err_msg : str
    error code and error message joined by comma



```python
fields = "buylot,delist_date,inst_type,list_date,multiplier,name,pricetick,product,market"
df = ds.query_inst_info('000001.SZ,000002.SZ,000001.SH', inst_type="", fields=fields)
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
      <th>buylot</th>
      <th>delist_date</th>
      <th>inst_type</th>
      <th>list_date</th>
      <th>market</th>
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
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>000001.SH</th>
      <td>100</td>
      <td>99999999</td>
      <td>100</td>
      <td>0</td>
      <td>SH</td>
      <td>1</td>
      <td>上证指数</td>
      <td>0.01</td>
      <td></td>
    </tr>
    <tr>
      <th>000001.SZ</th>
      <td>100</td>
      <td>99999999</td>
      <td>1</td>
      <td>19910403</td>
      <td>SZ</td>
      <td>1</td>
      <td>平安银行</td>
      <td>0.01</td>
      <td></td>
    </tr>
    <tr>
      <th>000002.SZ</th>
      <td>100</td>
      <td>99999999</td>
      <td>1</td>
      <td>19910129</td>
      <td>SZ</td>
      <td>1</td>
      <td>万  科Ａ</td>
      <td>0.01</td>
      <td></td>
    </tr>
  </tbody>
</table>
</div>



## query_trade_dates
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.query_trade_dates(start_date, end_date) `

**简要描述：**

- 某段时间范围内的交易日

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|start_date |是 |int |开始时间 YYYMMDD|
|end_date |是 |int |结束时间 YYYMMDD|


** 返回：**

trade_dates_arr : np.ndarray
           
           dtype = int



```python
ds.query_trade_dates(20170101,20170501)
```




    array([20170103, 20170104, 20170105, 20170106, 20170109, 20170110,
           20170111, 20170112, 20170113, 20170116, 20170117, 20170118,
           20170119, 20170120, 20170123, 20170124, 20170125, 20170126,
           20170203, 20170206, 20170207, 20170208, 20170209, 20170210,
           20170213, 20170214, 20170215, 20170216, 20170217, 20170220,
           20170221, 20170222, 20170223, 20170224, 20170227, 20170228,
           20170301, 20170302, 20170303, 20170306, 20170307, 20170308,
           20170309, 20170310, 20170313, 20170314, 20170315, 20170316,
           20170317, 20170320, 20170321, 20170322, 20170323, 20170324,
           20170327, 20170328, 20170329, 20170330, 20170331, 20170405,
           20170406, 20170407, 20170410, 20170411, 20170412, 20170413,
           20170414, 20170417, 20170418, 20170419, 20170420, 20170421,
           20170424, 20170425, 20170426, 20170427, 20170428])



## query_last_trade_date
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.query_last_trade_date(date) `

**简要描述：**

- 离某天最近的上一个交易日

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|date |是 |int | |


** 返回：**

int 最近的上一个交易日



```python
ds.query_last_trade_date(20170508)
```




    20170505



## query_next_trade_date
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.query_next_trade_date(date, n=1) `

**简要描述：**

- 离某天最近的下n个交易日

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|date |是 |int | |
|n |否 |int |下n个交易日 默认为1|


** 返回：**

int 最近的下n个交易日



```python
ds.query_next_trade_date(20170508,n=1)
```




    20170509



## is_trade_date
- ` jaqs_fxdayu.data.dataservice.RemoteDataService.is_trade_date(date) `

**简要描述：**

- 某天是否是交易日

**参数：**

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|date |是 |int | |


** 返回：**

bool



```python
ds.is_trade_date(20170508)
```




    True


