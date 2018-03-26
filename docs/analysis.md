
# analysis

## 介绍
单因子多维度分析.从因子ic,因子收益,选股潜在收益空间三个维度给出因子评价.新增模块

## ic_stats
- ` jaqs_fxdayu.research.signaldigger.analysis.ic_stats(signal_data) `

**简要描述：**

- 因子ic分析表
- 对事件因子(数值为0/1/-1的因子)无法使用该方法

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|signal_data |是|pandas.DataFrame |trade_date+symbol为MultiIndex,columns为signal(因子)、return(持有期相对/绝对收益,必须)、upside_ret(持有期潜在最大上涨收益,非必须)、downside_ret(持有期潜在最大下跌收益,非必须)、group(分组/行业分类,非必须)、quantile(按因子值分组,非必须)|

**返回:**
因子ic分析表
* 列:
  * return_ic/upside_ret_ic/downside_ret_ic
  * 持有期收益的ic/持有期最大向上空间的ic/持有期最大向下空间的ic
  
* 行:
  *  "IC Mean", "IC Std.", "t-stat(IC)", "p-value(IC)", "IC Skew", "IC Kurtosis", "Ann. IR"
  * IC均值，IC标准差，IC的t统计量，对IC做0均值假设检验的p-value，IC偏度，IC峰度，iC的年化信息比率-mean/std


**示例：**


```python
import warnings
warnings.filterwarnings('ignore')
```


```python
from jaqs_fxdayu.data import DataView
from jaqs_fxdayu.research import SignalDigger

# 加载dataview数据集
dv = DataView()
dataview_folder = './data'
dv.load_dataview(dataview_folder)

# 计算signal_data(通过jaqs.research.signaldigger.digger.SignalDigger.process_signal_before_analysis(*args, **kwargs))
sd = SignalDigger()
sd.process_signal_before_analysis(signal=dv.get_ts("pe"),
                                  price=dv.get_ts("close_adj"),
                                  high=dv.get_ts("high_adj"),
                                  low=dv.get_ts("low_adj"),
                                  group=dv.get_ts("sw1"),
                                  n_quantiles=5,
                                  period=5,
                                  benchmark_price=dv.data_benchmark,
                                  )
signal_data = sd.signal_data
signal_data.head()
```

    Dataview loaded successfully.
    Nan Data Count (should be zero) : 0;  Percentage of effective data: 99%





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
      <th></th>
      <th>signal</th>
      <th>return</th>
      <th>upside_ret</th>
      <th>downside_ret</th>
      <th>group</th>
      <th>quantile</th>
    </tr>
    <tr>
      <th>trade_date</th>
      <th>symbol</th>
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
      <th rowspan="5" valign="top">20170503</th>
      <th>000001.SZ</th>
      <td>6.7925</td>
      <td>-0.005637</td>
      <td>-0.003045</td>
      <td>-0.042326</td>
      <td>480000</td>
      <td>1</td>
    </tr>
    <tr>
      <th>000002.SZ</th>
      <td>10.0821</td>
      <td>0.011225</td>
      <td>0.016697</td>
      <td>-0.029432</td>
      <td>430000</td>
      <td>1</td>
    </tr>
    <tr>
      <th>000008.SZ</th>
      <td>42.9544</td>
      <td>-0.049408</td>
      <td>0.000463</td>
      <td>-0.092972</td>
      <td>640000</td>
      <td>4</td>
    </tr>
    <tr>
      <th>000009.SZ</th>
      <td>79.4778</td>
      <td>-0.069822</td>
      <td>0.009714</td>
      <td>-0.095426</td>
      <td>510000</td>
      <td>5</td>
    </tr>
    <tr>
      <th>000027.SZ</th>
      <td>20.4542</td>
      <td>-0.019517</td>
      <td>0.009404</td>
      <td>-0.041616</td>
      <td>410000</td>
      <td>2</td>
    </tr>
  </tbody>
</table>
</div>




```python
from jaqs_fxdayu.research.signaldigger.analysis import ic_stats

ic_stats(signal_data)
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
      <th>return_ic</th>
      <th>upside_ret_ic</th>
      <th>downside_ret_ic</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>IC Mean</th>
      <td>-0.022805</td>
      <td>0.031198</td>
      <td>-2.035376e-01</td>
    </tr>
    <tr>
      <th>IC Std.</th>
      <td>0.207325</td>
      <td>0.159313</td>
      <td>1.692702e-01</td>
    </tr>
    <tr>
      <th>t-stat(IC)</th>
      <td>-1.105467</td>
      <td>1.968055</td>
      <td>-1.208439e+01</td>
    </tr>
    <tr>
      <th>p-value(IC)</th>
      <td>0.271610</td>
      <td>0.051831</td>
      <td>2.894849e-21</td>
    </tr>
    <tr>
      <th>IC Skew</th>
      <td>0.009493</td>
      <td>-0.065715</td>
      <td>4.407910e-01</td>
    </tr>
    <tr>
      <th>IC Kurtosis</th>
      <td>-0.978744</td>
      <td>-0.639758</td>
      <td>-5.878823e-01</td>
    </tr>
    <tr>
      <th>Ann. IR</th>
      <td>-0.109998</td>
      <td>0.195829</td>
      <td>-1.202442e+00</td>
    </tr>
  </tbody>
</table>
</div>



### return_stats
- ` jaqs_fxdayu.research.signaldigger.analysis.return_stats(signal_data,is_event,period) `

**简要描述：**

- 因子收益分析表--根据因子构建几种投资组合，通过组合表现分析因子的收益能力

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|signal_data |是|pandas.DataFrame |trade_date+symbol为MultiIndex,columns为signal(因子)、return(持有期相对/绝对收益,必须)、upside_ret(持有期潜在最大上涨收益,非必须)、downside_ret(持有期潜在最大下跌收益,非必须)、group(分组/行业分类,非必须)、quantile(按因子值分组,非必须)|
|is_event |是|bool |是否是事件因子(数值为0/1/-1的因子)|
|period |是|int |换仓周期(天数),**注意:**必须与signal_data中收益的计算周期一致|

**返回:**

收益分析表
* 列:
  * long_ret/short_ret/long_short_ret/top_quantile_ret/bottom_quantile_ret/tmb_ret/all_sample_ret
  * 多头组合收益/空头组合收益/多空组合收益/因子值最大组合收益/因子值最小组合收益/因子值最大组（构建多头）+因子值最小组（构建空头）收益/全样本（无论信号大小和方向）-基准组合收益
  
* 行:
  * 't-stat', "p-value", "skewness", "kurtosis", "Ann. Ret", "Ann. Vol", "Ann. IR", "occurance"
  * 持有期收益的t统计量，对持有期收益做0均值假设检验的p-value，偏度，峰度，持有期收益年化值，年化波动率，年化信息比率-年化收益/年化波动率，样本数量


**示例：**


```python
from jaqs_fxdayu.research.signaldigger.analysis import return_stats

return_stats(signal_data,is_event=False,period=5)
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
      <th>long_ret</th>
      <th>long_short_ret</th>
      <th>top_quantile_ret</th>
      <th>bottom_quantile_ret</th>
      <th>tmb_ret</th>
      <th>all_sample_ret</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>t-stat</th>
      <td>-1.203846</td>
      <td>0.411628</td>
      <td>-4.728619</td>
      <td>-2.714885</td>
      <td>-0.755901</td>
      <td>-12.043624</td>
    </tr>
    <tr>
      <th>p-value</th>
      <td>0.231360</td>
      <td>0.681450</td>
      <td>0.000000</td>
      <td>0.006650</td>
      <td>0.451400</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>skewness</th>
      <td>-0.083057</td>
      <td>0.373680</td>
      <td>0.495042</td>
      <td>1.348467</td>
      <td>-0.261998</td>
      <td>0.546392</td>
    </tr>
    <tr>
      <th>kurtosis</th>
      <td>-0.555038</td>
      <td>0.042535</td>
      <td>6.187667</td>
      <td>9.207208</td>
      <td>-0.272022</td>
      <td>6.241350</td>
    </tr>
    <tr>
      <th>Ann. Ret</th>
      <td>-0.101735</td>
      <td>0.021452</td>
      <td>-0.129940</td>
      <td>-0.051046</td>
      <td>-0.078894</td>
      <td>-0.120509</td>
    </tr>
    <tr>
      <th>Ann. Vol</th>
      <td>0.124471</td>
      <td>0.076759</td>
      <td>0.330355</td>
      <td>0.226040</td>
      <td>0.153727</td>
      <td>0.268994</td>
    </tr>
    <tr>
      <th>Ann. IR</th>
      <td>-0.817333</td>
      <td>0.279469</td>
      <td>-0.393336</td>
      <td>-0.225829</td>
      <td>-0.513207</td>
      <td>-0.447998</td>
    </tr>
    <tr>
      <th>occurance</th>
      <td>106.000000</td>
      <td>106.000000</td>
      <td>6996.000000</td>
      <td>6996.000000</td>
      <td>106.000000</td>
      <td>34980.000000</td>
    </tr>
  </tbody>
</table>
</div>



## space_stats
- ` jaqs_fxdayu.research.signaldigger.analysis.space_stats(signal_data,is_event) `

**简要描述：**

- 因子潜在收益空间分析表--根据因子构建几种投资组合，通过组合在换仓周期内可能达到潜在最大上涨空间、潜在最大下跌空间来分析该因子选股收益的提升潜力，用于进一步辅助设计择时方案

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|signal_data |是|pandas.DataFrame |trade_date+symbol为MultiIndex,columns为signal(因子)、return(持有期相对/绝对收益,必须)、upside_ret(持有期潜在最大上涨收益,非必须)、downside_ret(持有期潜在最大下跌收益,非必须)、group(分组/行业分类,非必须)、quantile(按因子值分组,非必须)|
|is_event |是|bool |是否是事件因子(数值为0/1/-1的因子)|

**返回:**

因子潜在收益空间分析表
* 列:
  * long_space/short_space/long_short_space/top_quantile_space/bottom_quantile_space/tmb_space/all_sample_space
  * 多头组合空间/空头组合空间/多空组合空间/因子值最大组合空间/因子值最小组合空间/因子值最大组（构建多头）+因子值最小组（构建空头）空间/全样本（无论信号大小和方向）-基准组合空间
  
* 行:
  * 'Up_sp Mean','Up_sp Std','Up_sp IR','Up_sp Pct5', 'Up_sp Pct25 ','Up_sp Pct50 ', 'Up_sp Pct75','Up_sp Pct95','Up_sp Occur','Down_sp Mean','Down_sp Std', 'Down_sp IR', 'Down_sp Pct5','Down_sp Pct25 ','Down_sp Pct50 ','Down_sp Pct75', 'Down_sp Pct95','Down_sp Occur'
  * 组合持有个股的上行空间均值，上行空间标准差，上行空间信息比率-均值/标准差，上行空间5%分位数,..25%分位数，..中位数，..75%分位数,..95%分位数，上行空间样本数，下行空间...(同上行空间)


**示例：**


```python
from jaqs_fxdayu.research.signaldigger.analysis import space_stats

space_stats(signal_data,is_event=False)
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
      <th>long_space</th>
      <th>top_quantile_space</th>
      <th>bottom_quantile_space</th>
      <th>tmb_space</th>
      <th>all_sample_space</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Up_sp Mean</th>
      <td>-0.091582</td>
      <td>-0.089756</td>
      <td>-0.016239</td>
      <td>-0.013714</td>
      <td>-0.026786</td>
    </tr>
    <tr>
      <th>Up_sp Std</th>
      <td>0.033321</td>
      <td>0.343245</td>
      <td>0.212997</td>
      <td>0.017699</td>
      <td>0.240319</td>
    </tr>
    <tr>
      <th>Up_sp IR</th>
      <td>-2.748454</td>
      <td>-0.261492</td>
      <td>-0.076242</td>
      <td>-0.774819</td>
      <td>-0.111460</td>
    </tr>
    <tr>
      <th>Up_sp Pct5</th>
      <td>-0.127152</td>
      <td>-1.000800</td>
      <td>-0.005893</td>
      <td>-0.040333</td>
      <td>-1.000800</td>
    </tr>
    <tr>
      <th>Up_sp Pct25</th>
      <td>-0.117286</td>
      <td>0.002457</td>
      <td>0.004533</td>
      <td>-0.028591</td>
      <td>0.005062</td>
    </tr>
    <tr>
      <th>Up_sp Pct50</th>
      <td>-0.101419</td>
      <td>0.020756</td>
      <td>0.017939</td>
      <td>-0.013746</td>
      <td>0.019105</td>
    </tr>
    <tr>
      <th>Up_sp Pct75</th>
      <td>-0.076478</td>
      <td>0.047980</td>
      <td>0.039831</td>
      <td>-0.000051</td>
      <td>0.041935</td>
    </tr>
    <tr>
      <th>Up_sp Pct95</th>
      <td>-0.031515</td>
      <td>0.111557</td>
      <td>0.090402</td>
      <td>0.013496</td>
      <td>0.098799</td>
    </tr>
    <tr>
      <th>Up_sp Occur</th>
      <td>106.000000</td>
      <td>6996.000000</td>
      <td>6996.000000</td>
      <td>106.000000</td>
      <td>34980.000000</td>
    </tr>
    <tr>
      <th>Down_sp Mean</th>
      <td>-0.167327</td>
      <td>-0.171114</td>
      <td>-0.076042</td>
      <td>-0.154875</td>
      <td>-0.092512</td>
    </tr>
    <tr>
      <th>Down_sp Std</th>
      <td>0.046346</td>
      <td>0.340002</td>
      <td>0.224699</td>
      <td>0.045501</td>
      <td>0.245442</td>
    </tr>
    <tr>
      <th>Down_sp IR</th>
      <td>-3.610429</td>
      <td>-0.503275</td>
      <td>-0.338419</td>
      <td>-3.403795</td>
      <td>-0.376919</td>
    </tr>
    <tr>
      <th>Down_sp Pct5</th>
      <td>-0.220840</td>
      <td>-1.000800</td>
      <td>-1.000800</td>
      <td>-0.208216</td>
      <td>-1.000800</td>
    </tr>
    <tr>
      <th>Down_sp Pct25</th>
      <td>-0.190647</td>
      <td>-0.067406</td>
      <td>-0.034329</td>
      <td>-0.183180</td>
      <td>-0.042842</td>
    </tr>
    <tr>
      <th>Down_sp Pct50</th>
      <td>-0.176590</td>
      <td>-0.029282</td>
      <td>-0.017467</td>
      <td>-0.162556</td>
      <td>-0.021792</td>
    </tr>
    <tr>
      <th>Down_sp Pct75</th>
      <td>-0.152016</td>
      <td>-0.012810</td>
      <td>-0.007824</td>
      <td>-0.139399</td>
      <td>-0.009769</td>
    </tr>
    <tr>
      <th>Down_sp Pct95</th>
      <td>-0.111972</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>-0.086766</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>Down_sp Occur</th>
      <td>106.000000</td>
      <td>6996.000000</td>
      <td>6996.000000</td>
      <td>106.000000</td>
      <td>34980.000000</td>
    </tr>
  </tbody>
</table>
</div>



## analysis
- ` jaqs_fxdayu.research.signaldigger.analysis.analysis(signal_data,is_event,period) `

**简要描述：**

- 同时获得因子ic分析表、收益分析表、潜在收益空间分析表——单独计算三张表的方法见上述api

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|signal_data |是|pandas.DataFrame |trade_date+symbol为MultiIndex,columns为signal(因子)、return(持有期相对/绝对收益,必须)、upside_ret(持有期潜在最大上涨收益,非必须)、downside_ret(持有期潜在最大下跌收益,非必须)、group(分组/行业分类,非必须)、quantile(按因子值分组,非必须)|
|is_event |是|bool |是否是事件因子(数值为0/1/-1的因子)|
|period |是|int |换仓周期(天数),**注意:**必须与signal_data中收益的计算周期一致|

**返回:**

由因子ic分析表、收益分析表、潜在收益空间分析表组成的字典(dict)

**示例：**


```python
from jaqs_fxdayu.research.signaldigger.analysis import analysis

result = analysis(signal_data,is_event=False,period=5)
print(result.keys())
result["ic"]
```

    dict_keys(['ic', 'ret', 'space'])





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
      <th>return_ic</th>
      <th>upside_ret_ic</th>
      <th>downside_ret_ic</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>IC Mean</th>
      <td>-0.022805</td>
      <td>0.031198</td>
      <td>-2.035376e-01</td>
    </tr>
    <tr>
      <th>IC Std.</th>
      <td>0.207325</td>
      <td>0.159313</td>
      <td>1.692702e-01</td>
    </tr>
    <tr>
      <th>t-stat(IC)</th>
      <td>-1.105467</td>
      <td>1.968055</td>
      <td>-1.208439e+01</td>
    </tr>
    <tr>
      <th>p-value(IC)</th>
      <td>0.271610</td>
      <td>0.051831</td>
      <td>2.894849e-21</td>
    </tr>
    <tr>
      <th>IC Skew</th>
      <td>0.009493</td>
      <td>-0.065715</td>
      <td>4.407910e-01</td>
    </tr>
    <tr>
      <th>IC Kurtosis</th>
      <td>-0.978744</td>
      <td>-0.639758</td>
      <td>-5.878823e-01</td>
    </tr>
    <tr>
      <th>Ann. IR</th>
      <td>-0.109998</td>
      <td>0.195829</td>
      <td>-1.202442e+00</td>
    </tr>
  </tbody>
</table>
</div>


