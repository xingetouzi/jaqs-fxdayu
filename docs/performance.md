# performance

## 介绍
因子选股研究中常用的绩效计算方法


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

# 计算signal_data
sd = SignalDigger()
sd.process_signal_before_analysis(signal=dv.get_ts("pe"),
                                   price=dv.get_ts("close_adj"),
                                   group=dv.get_ts("sw1"),
                                   n_quantiles=5,
                                   period=15,
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
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">20170503</th>
      <th>000001.SZ</th>
      <td>6.7925</td>
      <td>-0.015258</td>
      <td>480000</td>
      <td>1</td>
    </tr>
    <tr>
      <th>000002.SZ</th>
      <td>10.0821</td>
      <td>0.013463</td>
      <td>430000</td>
      <td>1</td>
    </tr>
    <tr>
      <th>000008.SZ</th>
      <td>42.9544</td>
      <td>-0.122721</td>
      <td>640000</td>
      <td>4</td>
    </tr>
    <tr>
      <th>000009.SZ</th>
      <td>79.4778</td>
      <td>-0.155903</td>
      <td>510000</td>
      <td>5</td>
    </tr>
    <tr>
      <th>000027.SZ</th>
      <td>20.4542</td>
      <td>-0.041935</td>
      <td>410000</td>
      <td>2</td>
    </tr>
  </tbody>
</table>
</div>



## calc_signal_ic
- ` jaqs_fxdayu.research.signaldigger.performance.calc_signal_ic(signal_data, by_group=False) `

**简要描述：**

- 计算每日ic

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|signal_data |是| pandas.DataFrame |trade_date+symbol为MultiIndex,columns至少包含signal(因子)、return(持有期相对/绝对收益)、group(分组/行业分类)--仅在by_group=True时必须|
|by_group |否|bool|是否分组进行计算，默认为False|

**返回:**

每日ic

**示例：**


```python
from jaqs_fxdayu.research.signaldigger.performance import calc_signal_ic

ic_data = calc_signal_ic(signal_data,by_group=False)
ic_data.head()
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
      <th>ic</th>
    </tr>
    <tr>
      <th>trade_date</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>20170503</th>
      <td>-0.288577</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>-0.341181</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>-0.350174</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>-0.380677</td>
    </tr>
    <tr>
      <th>20170509</th>
      <td>-0.427141</td>
    </tr>
  </tbody>
</table>
</div>




```python
group_ic_data = calc_signal_ic(signal_data,by_group=True)
group_ic_data.head()
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
      <th></th>
      <th>ic</th>
    </tr>
    <tr>
      <th>trade_date</th>
      <th>group</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">20170503</th>
      <th>110000</th>
      <td>-0.142857</td>
    </tr>
    <tr>
      <th>210000</th>
      <td>-0.452381</td>
    </tr>
    <tr>
      <th>220000</th>
      <td>-0.285714</td>
    </tr>
    <tr>
      <th>230000</th>
      <td>0.100000</td>
    </tr>
    <tr>
      <th>240000</th>
      <td>0.013986</td>
    </tr>
  </tbody>
</table>
</div>



## calc_ic_stats_table
- ` jaqs_fxdayu.research.signaldigger.performance.calc_ic_stats_table(ic_data) `

**简要描述：**

- 根据每日ic计算总体ic统计结果

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|ic_data |是| pandas.DataFrame |trade_date为index,ic为columns。可通过calc_signal_ic计算得到|

**返回:**

总体ic统计结果

**示例：**


```python
from jaqs_fxdayu.research.signaldigger.performance import calc_ic_stats_table

calc_ic_stats_table(ic_data)
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
      <th>IC Mean</th>
      <th>IC Std.</th>
      <th>t-stat(IC)</th>
      <th>p-value(IC)</th>
      <th>IC Skew</th>
      <th>IC Kurtosis</th>
      <th>Ann. IR</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>ic</th>
      <td>-0.030303</td>
      <td>0.207642</td>
      <td>-1.392159</td>
      <td>0.167305</td>
      <td>0.189897</td>
      <td>-0.601332</td>
      <td>-0.145938</td>
    </tr>
  </tbody>
</table>
</div>



## mean_information_coefficient
- ` jaqs_fxdayu.research.signaldigger.performance.mean_information_coefficient(ic, by_time=None, by_group=False) `

**简要描述：**

- 输入ic,计算平均ic

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|ic |是| pandas.DataFrame |trade_date为index,ic为columns。可通过calc_signal_ic计算得到。注意：当by_group=True时，index需要为trade_date+group的MultiIndex（可以通过calc_signal_ic计算得到（设置by_group=True））|
|by_time |否| str |支持pandas.TimeGrouper中的日期划分，如"M"（按月）,"A"（全部时段）,"Q"（按季度），"W"（按周）。默认求每日ic的所有样本的平均值|
|by_group |否|bool|是否分组进行平均计算，默认为False|

**返回:**

平均ic

**示例：**

#### 示例一：按每3周求平均ic


```python
from jaqs_fxdayu.research.signaldigger.performance import mean_information_coefficient

mean_information_coefficient(ic_data, by_time='3w')
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
      <th>ic</th>
    </tr>
    <tr>
      <th>trade_date</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2017-05-07</th>
      <td>-0.326644</td>
    </tr>
    <tr>
      <th>2017-05-28</th>
      <td>-0.225651</td>
    </tr>
    <tr>
      <th>2017-06-18</th>
      <td>0.062981</td>
    </tr>
    <tr>
      <th>2017-07-09</th>
      <td>-0.193377</td>
    </tr>
    <tr>
      <th>2017-07-30</th>
      <td>0.217053</td>
    </tr>
    <tr>
      <th>2017-08-20</th>
      <td>0.034492</td>
    </tr>
    <tr>
      <th>2017-09-10</th>
      <td>-0.005609</td>
    </tr>
    <tr>
      <th>2017-10-01</th>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



#### 示例一：分组求每组的月平均ic


```python
mean_information_coefficient(group_ic_data, by_group=True, by_time="M")
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
      <th></th>
      <th>ic</th>
    </tr>
    <tr>
      <th>trade_date</th>
      <th>group</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="28" valign="top">2017-05-31</th>
      <th>110000</th>
      <td>-0.323308</td>
    </tr>
    <tr>
      <th>210000</th>
      <td>-0.464912</td>
    </tr>
    <tr>
      <th>220000</th>
      <td>-0.221515</td>
    </tr>
    <tr>
      <th>230000</th>
      <td>-0.142105</td>
    </tr>
    <tr>
      <th>240000</th>
      <td>-0.158263</td>
    </tr>
    <tr>
      <th>270000</th>
      <td>-0.236225</td>
    </tr>
    <tr>
      <th>280000</th>
      <td>-0.210836</td>
    </tr>
    <tr>
      <th>330000</th>
      <td>-0.253759</td>
    </tr>
    <tr>
      <th>340000</th>
      <td>0.245614</td>
    </tr>
    <tr>
      <th>350000</th>
      <td>-0.473684</td>
    </tr>
    <tr>
      <th>360000</th>
      <td>NaN</td>
    </tr>
    <tr>
      <th>370000</th>
      <td>-0.318267</td>
    </tr>
    <tr>
      <th>410000</th>
      <td>-0.339234</td>
    </tr>
    <tr>
      <th>420000</th>
      <td>-0.127752</td>
    </tr>
    <tr>
      <th>430000</th>
      <td>-0.269569</td>
    </tr>
    <tr>
      <th>450000</th>
      <td>-0.091479</td>
    </tr>
    <tr>
      <th>460000</th>
      <td>-0.589474</td>
    </tr>
    <tr>
      <th>480000</th>
      <td>-0.147984</td>
    </tr>
    <tr>
      <th>490000</th>
      <td>-0.337726</td>
    </tr>
    <tr>
      <th>510000</th>
      <td>0.684211</td>
    </tr>
    <tr>
      <th>610000</th>
      <td>-0.684211</td>
    </tr>
    <tr>
      <th>620000</th>
      <td>-0.454309</td>
    </tr>
    <tr>
      <th>630000</th>
      <td>-0.120301</td>
    </tr>
    <tr>
      <th>640000</th>
      <td>0.262448</td>
    </tr>
    <tr>
      <th>650000</th>
      <td>-0.197368</td>
    </tr>
    <tr>
      <th>710000</th>
      <td>-0.105139</td>
    </tr>
    <tr>
      <th>720000</th>
      <td>0.064058</td>
    </tr>
    <tr>
      <th>730000</th>
      <td>-0.492196</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">2017-06-30</th>
      <th>110000</th>
      <td>-0.179221</td>
    </tr>
    <tr>
      <th>210000</th>
      <td>0.496605</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">2017-08-31</th>
      <th>720000</th>
      <td>-0.215646</td>
    </tr>
    <tr>
      <th>730000</th>
      <td>-0.297784</td>
    </tr>
    <tr>
      <th rowspan="28" valign="top">2017-09-30</th>
      <th>110000</th>
      <td>0.172619</td>
    </tr>
    <tr>
      <th>210000</th>
      <td>-0.214286</td>
    </tr>
    <tr>
      <th>220000</th>
      <td>0.240909</td>
    </tr>
    <tr>
      <th>230000</th>
      <td>0.950000</td>
    </tr>
    <tr>
      <th>240000</th>
      <td>0.009324</td>
    </tr>
    <tr>
      <th>270000</th>
      <td>0.019069</td>
    </tr>
    <tr>
      <th>280000</th>
      <td>-0.104762</td>
    </tr>
    <tr>
      <th>330000</th>
      <td>-0.238095</td>
    </tr>
    <tr>
      <th>340000</th>
      <td>-0.333333</td>
    </tr>
    <tr>
      <th>350000</th>
      <td>-1.000000</td>
    </tr>
    <tr>
      <th>360000</th>
      <td>NaN</td>
    </tr>
    <tr>
      <th>370000</th>
      <td>0.231336</td>
    </tr>
    <tr>
      <th>410000</th>
      <td>-0.348485</td>
    </tr>
    <tr>
      <th>420000</th>
      <td>0.331269</td>
    </tr>
    <tr>
      <th>430000</th>
      <td>0.110680</td>
    </tr>
    <tr>
      <th>450000</th>
      <td>0.476190</td>
    </tr>
    <tr>
      <th>460000</th>
      <td>0.500000</td>
    </tr>
    <tr>
      <th>480000</th>
      <td>-0.642677</td>
    </tr>
    <tr>
      <th>490000</th>
      <td>-0.125032</td>
    </tr>
    <tr>
      <th>510000</th>
      <td>-0.233333</td>
    </tr>
    <tr>
      <th>610000</th>
      <td>NaN</td>
    </tr>
    <tr>
      <th>620000</th>
      <td>-0.076007</td>
    </tr>
    <tr>
      <th>630000</th>
      <td>0.013217</td>
    </tr>
    <tr>
      <th>640000</th>
      <td>-0.277610</td>
    </tr>
    <tr>
      <th>650000</th>
      <td>0.063889</td>
    </tr>
    <tr>
      <th>710000</th>
      <td>0.164695</td>
    </tr>
    <tr>
      <th>720000</th>
      <td>-0.143014</td>
    </tr>
    <tr>
      <th>730000</th>
      <td>-0.444444</td>
    </tr>
  </tbody>
</table>
<p>140 rows × 1 columns</p>
</div>



## calc_period_wise_weighted_signal_return
- ` jaqs_fxdayu.research.signaldigger.performance.calc_period_wise_weighted_signal_return(signal_data, weight_method) `

**简要描述：**

- 根据signal_data构建投资组合，计算投资组合的每日调仓收益

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|signal_data |是| pandas.DataFrame |trade_date+symbol为MultiIndex,columns至少包含signal(因子)、return(持有期相对/绝对收益)|
|weight_method |是| str |支持四种投资组合构建方式：'equal_weight'(对signal_data中的每一只股票等资金买入), 'long_only'（只做多signal值为正的股票，并按signal的大小加权构建多头组合）, 'short_only'（只做空signal值为负的股票，并按signal的大小加权构建空头组合）,'long_short'（做多signal为正，做空signal为负的股票，按signal的大小加权）|

**返回:**

投资组合的每日调仓收益

**示例：**


```python
from jaqs_fxdayu.research.signaldigger.performance import calc_period_wise_weighted_signal_return

daily_return = calc_period_wise_weighted_signal_return(signal_data, weight_method="long_only")
daily_return.head()
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
      <th>return</th>
    </tr>
    <tr>
      <th>trade_date</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>20170503</th>
      <td>-0.066372</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>-0.070300</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>-0.065394</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>-0.064365</td>
    </tr>
    <tr>
      <th>20170509</th>
      <td>-0.078423</td>
    </tr>
  </tbody>
</table>
</div>



## regress_period_wise_signal_return
- ` jaqs_fxdayu.research.signaldigger.performance.regress_period_wise_signal_return(signal_data) `

**简要描述：**

- 对signal_data中的signal和return进行横截面回归（OLS）,计算每期的因子收益（回归系数）

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|signal_data |是| pandas.DataFrame |trade_date+symbol为MultiIndex,columns至少包含signal(因子)、return(持有期相对/绝对收益)|

**返回:**

每期的因子收益（回归系数）

**示例：**


```python
from jaqs_fxdayu.research.signaldigger.performance import regress_period_wise_signal_return

regress_period_wise_signal_return(signal_data).head()
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
      <th>0</th>
    </tr>
    <tr>
      <th>trade_date</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>20170503</th>
      <td>-0.000093</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>-0.000091</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>-0.000090</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>-0.000095</td>
    </tr>
    <tr>
      <th>20170509</th>
      <td>-0.000104</td>
    </tr>
  </tbody>
</table>
</div>



## calc_quantile_return_mean_std
- ` jaqs_fxdayu.research.signaldigger.performance.calc_quantile_return_mean_std(signal_data, time_series=False) `

**简要描述：**

- 将股票按quantile分组分别等权买入持有，计算每组的平均持有收益（每日）和持有收益的标准差

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|signal_data |是| pandas.DataFrame |trade_date+symbol为MultiIndex,columns至少包含signal(因子)、return(持有期相对/绝对收益)、quantile(按因子值分组)|
|time_series |否| bool |是否展示每组每天的收益，默认为False|

**返回:**

每组（quantile）的平均持有收益（每日）和持有收益的标准差

**示例：**

#### 示例一：展示每组的平均持有收益（每日）和持有收益的标准差（time_series=False）
返回pandas.DataFrame


```python
from jaqs_fxdayu.research.signaldigger.performance import calc_quantile_return_mean_std

calc_quantile_return_mean_std(signal_data, time_series=False)
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
      <th>mean</th>
      <th>std</th>
      <th>count</th>
    </tr>
    <tr>
      <th>quantile</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>-0.000813</td>
      <td>0.051852</td>
      <td>6996</td>
    </tr>
    <tr>
      <th>2</th>
      <td>-0.000514</td>
      <td>0.051664</td>
      <td>6996</td>
    </tr>
    <tr>
      <th>3</th>
      <td>-0.005477</td>
      <td>0.057944</td>
      <td>6996</td>
    </tr>
    <tr>
      <th>4</th>
      <td>-0.010762</td>
      <td>0.063931</td>
      <td>6996</td>
    </tr>
    <tr>
      <th>5</th>
      <td>-0.000114</td>
      <td>0.079470</td>
      <td>6996</td>
    </tr>
  </tbody>
</table>
</div>



#### 示例二：展示每组每日的持有收益和持有收益的标准差（time_series=True）
返回dict


```python
result = calc_quantile_return_mean_std(signal_data, time_series=True)
print(result.keys())
result[1].head()
```

    dict_keys([1, 2, 3, 4, 5])





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
      <th>mean</th>
      <th>std</th>
      <th>count</th>
    </tr>
    <tr>
      <th>trade_date</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>20170503</th>
      <td>-0.005253</td>
      <td>0.068051</td>
      <td>66</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>-0.004897</td>
      <td>0.076375</td>
      <td>66</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>-0.003048</td>
      <td>0.074683</td>
      <td>66</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>-0.001248</td>
      <td>0.063775</td>
      <td>66</td>
    </tr>
    <tr>
      <th>20170509</th>
      <td>-0.002070</td>
      <td>0.072706</td>
      <td>66</td>
    </tr>
  </tbody>
</table>
</div>



## price2ret
- ` jaqs_fxdayu.research.signaldigger.performance.price2ret(prices, period=5, axis=None, compound=True) `

**简要描述：**

- 将价格序列转化为定期调仓收益序列

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|price |是| pandas.DataFrame/pandas.Series |时间为索引的价格表|
|period |否| int |调仓周期，默认为5|
|axis |否| int |{0, 1, None}，将表格按某个维度进行收益计算（横向/纵向）,默认纵向计算|
|compound |否| bool |收益计算是否为复利。单利：（相对表格第一行的收益）；复利（相对上一期的收益），默认为True 复利模式|

**返回:**

收益序列

**示例：**


```python
prices = dv.get_ts("close_adj")
prices.head()
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
      <td>898.67562</td>
      <td>2373.25440</td>
      <td>210.898632</td>
      <td>85.962653</td>
      <td>94.89530</td>
      <td>378.975476</td>
      <td>241.71550</td>
      <td>200.562672</td>
      <td>299.850012</td>
      <td>318.911580</td>
      <td>...</td>
      <td>5.597708</td>
      <td>11.717117</td>
      <td>17.382915</td>
      <td>15.67</td>
      <td>7.856221</td>
      <td>60.301733</td>
      <td>97.88</td>
      <td>80.49</td>
      <td>45.397002</td>
      <td>14.498578</td>
    </tr>
    <tr>
      <th>20170503</th>
      <td>895.65993</td>
      <td>2331.22802</td>
      <td>209.312928</td>
      <td>85.265390</td>
      <td>93.66644</td>
      <td>378.030400</td>
      <td>239.12148</td>
      <td>198.410712</td>
      <td>302.909706</td>
      <td>314.186964</td>
      <td>...</td>
      <td>5.550537</td>
      <td>11.532463</td>
      <td>16.034422</td>
      <td>15.71</td>
      <td>7.777265</td>
      <td>60.998626</td>
      <td>97.67</td>
      <td>80.53</td>
      <td>45.498789</td>
      <td>14.450080</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>878.57102</td>
      <td>2351.00514</td>
      <td>208.255792</td>
      <td>85.066171</td>
      <td>93.80298</td>
      <td>372.123675</td>
      <td>234.64090</td>
      <td>196.473948</td>
      <td>303.079689</td>
      <td>314.974400</td>
      <td>...</td>
      <td>5.550537</td>
      <td>11.364596</td>
      <td>16.687598</td>
      <td>15.61</td>
      <td>7.724627</td>
      <td>59.276890</td>
      <td>96.99</td>
      <td>79.62</td>
      <td>45.295215</td>
      <td>14.094485</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>867.51349</td>
      <td>2334.93623</td>
      <td>199.270136</td>
      <td>82.277117</td>
      <td>92.84720</td>
      <td>359.128880</td>
      <td>232.99016</td>
      <td>195.613164</td>
      <td>299.170080</td>
      <td>310.249784</td>
      <td>...</td>
      <td>5.566261</td>
      <td>11.129582</td>
      <td>16.371545</td>
      <td>15.20</td>
      <td>7.685148</td>
      <td>57.842111</td>
      <td>95.11</td>
      <td>78.51</td>
      <td>45.824507</td>
      <td>13.803544</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>861.48211</td>
      <td>2283.02129</td>
      <td>193.191604</td>
      <td>80.284935</td>
      <td>90.93564</td>
      <td>355.112307</td>
      <td>233.93344</td>
      <td>196.689144</td>
      <td>289.481049</td>
      <td>308.281194</td>
      <td>...</td>
      <td>5.613432</td>
      <td>10.777061</td>
      <td>14.812351</td>
      <td>14.83</td>
      <td>7.724627</td>
      <td>57.678136</td>
      <td>97.00</td>
      <td>76.60</td>
      <td>45.030569</td>
      <td>13.868197</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>




```python
from jaqs_fxdayu.research.signaldigger.performance import price2ret

ret = price2ret(prices, period=5, compound=True)
ret.dropna().head()
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
      <th>20170509</th>
      <td>-0.033557</td>
      <td>-0.030208</td>
      <td>-0.081454</td>
      <td>-0.063731</td>
      <td>-0.035971</td>
      <td>-0.053616</td>
      <td>-0.015610</td>
      <td>-0.020386</td>
      <td>-0.027211</td>
      <td>-0.032099</td>
      <td>...</td>
      <td>0.002809</td>
      <td>-0.070201</td>
      <td>-0.134545</td>
      <td>-0.019145</td>
      <td>-0.013400</td>
      <td>-0.037390</td>
      <td>-0.007662</td>
      <td>-0.040253</td>
      <td>-0.033632</td>
      <td>-0.043479</td>
    </tr>
    <tr>
      <th>20170510</th>
      <td>-0.026936</td>
      <td>-0.010074</td>
      <td>-0.070707</td>
      <td>-0.091121</td>
      <td>-0.040816</td>
      <td>-0.078750</td>
      <td>-0.038462</td>
      <td>-0.034707</td>
      <td>-0.056678</td>
      <td>-0.016291</td>
      <td>...</td>
      <td>0.014164</td>
      <td>-0.082969</td>
      <td>-0.137976</td>
      <td>0.004456</td>
      <td>-0.003384</td>
      <td>-0.061828</td>
      <td>-0.058360</td>
      <td>-0.066559</td>
      <td>-0.052349</td>
      <td>-0.073826</td>
    </tr>
    <tr>
      <th>20170511</th>
      <td>-0.004577</td>
      <td>0.011567</td>
      <td>-0.058376</td>
      <td>-0.093677</td>
      <td>-0.061135</td>
      <td>-0.060952</td>
      <td>-0.026149</td>
      <td>-0.059146</td>
      <td>-0.029725</td>
      <td>-0.012500</td>
      <td>...</td>
      <td>0.025496</td>
      <td>-0.063516</td>
      <td>-0.140152</td>
      <td>0.016015</td>
      <td>0.017036</td>
      <td>-0.063624</td>
      <td>-0.044334</td>
      <td>-0.075232</td>
      <td>-0.069213</td>
      <td>-0.043578</td>
    </tr>
    <tr>
      <th>20170512</th>
      <td>0.031286</td>
      <td>0.026998</td>
      <td>-0.025199</td>
      <td>-0.069007</td>
      <td>-0.051471</td>
      <td>-0.002632</td>
      <td>-0.026356</td>
      <td>-0.051705</td>
      <td>-0.020455</td>
      <td>0.019036</td>
      <td>...</td>
      <td>0.036723</td>
      <td>-0.051282</td>
      <td>-0.120978</td>
      <td>0.063816</td>
      <td>0.051370</td>
      <td>-0.046775</td>
      <td>-0.016823</td>
      <td>-0.068654</td>
      <td>-0.084851</td>
      <td>-0.035129</td>
    </tr>
    <tr>
      <th>20170515</th>
      <td>0.033839</td>
      <td>0.047103</td>
      <td>0.006840</td>
      <td>-0.042184</td>
      <td>-0.027027</td>
      <td>0.005323</td>
      <td>-0.026237</td>
      <td>-0.054705</td>
      <td>0.024075</td>
      <td>0.040868</td>
      <td>...</td>
      <td>0.025210</td>
      <td>-0.031153</td>
      <td>-0.036984</td>
      <td>0.078220</td>
      <td>0.034072</td>
      <td>-0.039090</td>
      <td>-0.035258</td>
      <td>-0.041775</td>
      <td>-0.064647</td>
      <td>-0.025641</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>



## ret2cum
- ` jaqs_fxdayu.research.signaldigger.performance.ret2cum(ret, compound=True, axis=None) `

**简要描述：**

- 将收益序列转化为累积收益序列

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|ret |是| pandas.DataFrame/pandas.Series |时间为索引的收益表|
|compound |否| bool |收益计算是否为复利。单利：（每期累加的收益）；复利（每期累乘的收益），默认为True 复利模式|
|axis |否| int |{0, 1, None}，将表格按某个维度进行收益计算（横向/纵向）,默认纵向计算|

**返回:**

累积收益序列

**示例：**


```python
from jaqs_fxdayu.research.signaldigger.performance import ret2cum

cum = ret2cum(ret, compound=True)
cum.dropna().head()
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
      <th>20170509</th>
      <td>-0.033557</td>
      <td>-0.030208</td>
      <td>-0.081454</td>
      <td>-0.063731</td>
      <td>-0.035971</td>
      <td>-0.053616</td>
      <td>-0.015610</td>
      <td>-0.020386</td>
      <td>-0.027211</td>
      <td>-0.032099</td>
      <td>...</td>
      <td>0.002809</td>
      <td>-0.070201</td>
      <td>-0.134545</td>
      <td>-0.019145</td>
      <td>-0.013400</td>
      <td>-0.037390</td>
      <td>-0.007662</td>
      <td>-0.040253</td>
      <td>-0.033632</td>
      <td>-0.043479</td>
    </tr>
    <tr>
      <th>20170510</th>
      <td>-0.059589</td>
      <td>-0.039978</td>
      <td>-0.146401</td>
      <td>-0.149045</td>
      <td>-0.075319</td>
      <td>-0.128144</td>
      <td>-0.053471</td>
      <td>-0.054386</td>
      <td>-0.082347</td>
      <td>-0.047867</td>
      <td>...</td>
      <td>0.017013</td>
      <td>-0.147346</td>
      <td>-0.253958</td>
      <td>-0.014774</td>
      <td>-0.016739</td>
      <td>-0.096906</td>
      <td>-0.065575</td>
      <td>-0.104133</td>
      <td>-0.084221</td>
      <td>-0.114094</td>
    </tr>
    <tr>
      <th>20170511</th>
      <td>-0.063893</td>
      <td>-0.028874</td>
      <td>-0.196231</td>
      <td>-0.228760</td>
      <td>-0.131850</td>
      <td>-0.181285</td>
      <td>-0.078221</td>
      <td>-0.110315</td>
      <td>-0.109624</td>
      <td>-0.059768</td>
      <td>...</td>
      <td>0.042943</td>
      <td>-0.201502</td>
      <td>-0.358517</td>
      <td>0.001004</td>
      <td>0.000012</td>
      <td>-0.154364</td>
      <td>-0.107002</td>
      <td>-0.171531</td>
      <td>-0.147605</td>
      <td>-0.152700</td>
    </tr>
    <tr>
      <th>20170512</th>
      <td>-0.034606</td>
      <td>-0.002655</td>
      <td>-0.216485</td>
      <td>-0.281981</td>
      <td>-0.176534</td>
      <td>-0.183440</td>
      <td>-0.102515</td>
      <td>-0.156316</td>
      <td>-0.127836</td>
      <td>-0.041870</td>
      <td>...</td>
      <td>0.081243</td>
      <td>-0.242451</td>
      <td>-0.436122</td>
      <td>0.064884</td>
      <td>0.051382</td>
      <td>-0.193919</td>
      <td>-0.122025</td>
      <td>-0.228409</td>
      <td>-0.219932</td>
      <td>-0.182465</td>
    </tr>
    <tr>
      <th>20170515</th>
      <td>-0.001938</td>
      <td>0.044323</td>
      <td>-0.211126</td>
      <td>-0.312270</td>
      <td>-0.198790</td>
      <td>-0.179094</td>
      <td>-0.126063</td>
      <td>-0.202470</td>
      <td>-0.106839</td>
      <td>-0.002713</td>
      <td>...</td>
      <td>0.108501</td>
      <td>-0.266051</td>
      <td>-0.456977</td>
      <td>0.148179</td>
      <td>0.087204</td>
      <td>-0.225429</td>
      <td>-0.152980</td>
      <td>-0.260642</td>
      <td>-0.270361</td>
      <td>-0.203427</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>



## cum2ret
- ` jaqs_fxdayu.research.signaldigger.performance.cum2ret(cum, period=1, axis=None, compound=True) `

**简要描述：**

- 将累积收益序列转化为收益序列

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|cum |是| pandas.DataFrame/pandas.Series |时间为索引的累积收益表|
|period |否| int |通常为1。累积收益的累积间隔周期。默认为1|
|compound |否| bool |收益计算是否为复利。单利：（每期累加的收益）；复利（每期累乘的收益），默认为True 复利模式|
|axis |否| int |{0, 1, None}，将表格按某个维度进行收益计算（横向/纵向）,默认纵向计算|

**返回:**

收益序列

**示例：**


```python
from jaqs_fxdayu.research.signaldigger.performance import cum2ret

cum2ret(cum, period=1,compound=True).dropna().head()
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
      <th>20170510</th>
      <td>-0.026936</td>
      <td>-0.010074</td>
      <td>-0.070707</td>
      <td>-0.091121</td>
      <td>-0.040816</td>
      <td>-0.078750</td>
      <td>-0.038462</td>
      <td>-0.034707</td>
      <td>-0.056678</td>
      <td>-0.016291</td>
      <td>...</td>
      <td>0.014164</td>
      <td>-0.082969</td>
      <td>-0.137976</td>
      <td>0.004456</td>
      <td>-0.003384</td>
      <td>-0.061828</td>
      <td>-0.058360</td>
      <td>-0.066559</td>
      <td>-0.052349</td>
      <td>-0.073826</td>
    </tr>
    <tr>
      <th>20170511</th>
      <td>-0.004577</td>
      <td>0.011567</td>
      <td>-0.058376</td>
      <td>-0.093677</td>
      <td>-0.061135</td>
      <td>-0.060952</td>
      <td>-0.026149</td>
      <td>-0.059146</td>
      <td>-0.029725</td>
      <td>-0.012500</td>
      <td>...</td>
      <td>0.025496</td>
      <td>-0.063516</td>
      <td>-0.140152</td>
      <td>0.016015</td>
      <td>0.017036</td>
      <td>-0.063624</td>
      <td>-0.044334</td>
      <td>-0.075232</td>
      <td>-0.069213</td>
      <td>-0.043578</td>
    </tr>
    <tr>
      <th>20170512</th>
      <td>0.031286</td>
      <td>0.026998</td>
      <td>-0.025199</td>
      <td>-0.069007</td>
      <td>-0.051471</td>
      <td>-0.002632</td>
      <td>-0.026356</td>
      <td>-0.051705</td>
      <td>-0.020455</td>
      <td>0.019036</td>
      <td>...</td>
      <td>0.036723</td>
      <td>-0.051282</td>
      <td>-0.120978</td>
      <td>0.063816</td>
      <td>0.051370</td>
      <td>-0.046775</td>
      <td>-0.016823</td>
      <td>-0.068654</td>
      <td>-0.084851</td>
      <td>-0.035129</td>
    </tr>
    <tr>
      <th>20170515</th>
      <td>0.033839</td>
      <td>0.047103</td>
      <td>0.006840</td>
      <td>-0.042184</td>
      <td>-0.027027</td>
      <td>0.005323</td>
      <td>-0.026237</td>
      <td>-0.054705</td>
      <td>0.024075</td>
      <td>0.040868</td>
      <td>...</td>
      <td>0.025210</td>
      <td>-0.031153</td>
      <td>-0.036984</td>
      <td>0.078220</td>
      <td>0.034072</td>
      <td>-0.039090</td>
      <td>-0.035258</td>
      <td>-0.041775</td>
      <td>-0.064647</td>
      <td>-0.025641</td>
    </tr>
    <tr>
      <th>20170516</th>
      <td>0.023148</td>
      <td>0.032760</td>
      <td>0.006821</td>
      <td>-0.024752</td>
      <td>-0.008955</td>
      <td>0.012516</td>
      <td>-0.022761</td>
      <td>-0.037240</td>
      <td>0.103730</td>
      <td>0.040816</td>
      <td>...</td>
      <td>0.016807</td>
      <td>-0.030817</td>
      <td>0.029412</td>
      <td>0.036435</td>
      <td>0.028862</td>
      <td>-0.027542</td>
      <td>0.018429</td>
      <td>-0.035728</td>
      <td>-0.028770</td>
      <td>0.020979</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>



## calc_performance_metrics
- ` jaqs_fxdayu.research.signaldigger.performance.calc_performance_metrics(ser, cum_return=False, compound=True) `

**简要描述：**

- 根据收益计算常见绩效——annualized return, volatility and sharpe

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|ser |是| pandas.DataFrame/pandas.Series |时间为索引的收益/累积收益表。注意：只能有一列值，不支持多列收益的计算|
|cum_return |否| bool |收益是否为累积收益，默认为否（False）|
|compound |否| bool |收益计算是否为复利。单利：（每期累加的收益）；复利（每期累乘的收益），默认为True 复利模式|

**返回:**

绩效表

**示例：**


```python
from jaqs_fxdayu.research.signaldigger.performance import calc_performance_metrics

# 多头组合的每日收益
daily_return = calc_period_wise_weighted_signal_return(signal_data, weight_method="long_only")
# 该收益的绩效表现
calc_performance_metrics(daily_return, cum_return=False, compound=True)
```




    {'ann_ret': 0.055395156268065238,
     'ann_vol': 0.4356857810045196,
     'sharpe': 0.12714474211287285}



## period_wise_ret_to_cum
- ` jaqs_fxdayu.research.signaldigger.performance.period_wise_ret_to_cum(ret, period, compound=True) `

**简要描述：**

- 从按period周期调仓的选股方案的每日收益中计算累积收益。计算方式如下：
- 以某个调仓周期为n天的选股方案为例：将资金等分为n分，每天取其中一份买入当天的选股并持有到5天后卖出，最后的组合累积收益。

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|ret |是| pandas.DataFrame/pandas.Series |时间为索引的收益表。|
|period |是| int |调仓周期 |
|compound |否| bool |收益计算是否为复利。单利：（每期累加的收益）；复利（每期累乘的收益），默认为True 复利模式|

**返回:**

累积收益

**示例：**


```python
daily_return.head() # 每一天对应的收益代表买入股票15天后卖出的收益。如20170503的return表示20170503买入股票并在20170518卖出的收益
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
      <th>return</th>
    </tr>
    <tr>
      <th>trade_date</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>20170503</th>
      <td>-0.066372</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>-0.070300</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>-0.065394</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>-0.064365</td>
    </tr>
    <tr>
      <th>20170509</th>
      <td>-0.078423</td>
    </tr>
  </tbody>
</table>
</div>




```python
from jaqs_fxdayu.research.signaldigger.performance import period_wise_ret_to_cum

period_wise_ret_to_cum(daily_return, period=15, compound=True).head()
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
      <th>return</th>
    </tr>
    <tr>
      <th>trade_date</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>20170503</th>
      <td>-0.004425</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>-0.009111</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>-0.013471</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>-0.017762</td>
    </tr>
    <tr>
      <th>20170509</th>
      <td>-0.022990</td>
    </tr>
  </tbody>
</table>
</div>


