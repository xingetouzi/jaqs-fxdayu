
# multi_factor

## 介绍
提供多因子处理和组合功能

## orthogonalize
- ` jaqs_fxdayu.research.signaldigger.multi_factor.orthogonalize(factors_dict=None,standardize_type="z_score",winsorization=False,index_member=None) `

**简要描述：**

- 因子间存在较强同质性时，使用施密特正交化方法对因子做正交化处理，用得到的正交化残差作为因子

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|factors_dict|是|dict of pandas.DataFrame | 若干因子组成的字典(dict),形式为:{"factor_name_1":factor_1,"factor_name_2":factor_2}。每个因子值格式为一个pd.DataFrame，索引(index)为date,column为asset|
|standardize_type|否|string| 标准化方法，有"rank"（排序标准化）,"z_score"(z-score标准化)两种（"rank"/"z_score"），默认为"z_score"|
|winsorization|否|bool| 是否对因子执行去极值操作。默认不执行（False）|
|index_member |否|pandas.DataFrame of bool |是否是指数成分股。日期为索引,证券品种为columns的二维bool值表格,True代表该品种在该日期下属于指数成分股。传入该参数,则在对因子进行标准化/去极值操作时所纳入的样本只有每期横截面上属于对应指数成分股的股票，默认为空|


**返回:**

正交化处理后所得的一系列新因子。dict of pandas.DataFrame

**示例：**


```python
import warnings
warnings.filterwarnings('ignore')
```


```python
from jaqs_fxdayu.data import DataView
from jaqs_fxdayu.research.signaldigger.multi_factor import orthogonalize

# 加载dataview数据集
dv = DataView()
dataview_folder = './data'
dv.load_dataview(dataview_folder)

# 正交化
factors_dict = {signal:dv.get_ts(signal) for signal in ["pb","pe"]}
new_factors = orthogonalize(factors_dict=factors_dict,
                            standardize_type="z_score",
                            winsorization=False,
                            index_member=None)
```

    Dataview loaded successfully.



```python
print(new_factors.keys())
new_factors["pe"].head()
```

    dict_keys(['pb', 'pe'])





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
      <td>-0.661167</td>
      <td>-0.321008</td>
      <td>0.137600</td>
      <td>0.117712</td>
      <td>-0.570730</td>
      <td>-0.776328</td>
      <td>-0.262312</td>
      <td>-0.630645</td>
      <td>-0.220092</td>
      <td>-0.444949</td>
      <td>...</td>
      <td>-0.673545</td>
      <td>-0.996365</td>
      <td>-0.388348</td>
      <td>-0.395778</td>
      <td>-0.658705</td>
      <td>0.429739</td>
      <td>3.959548</td>
      <td>0.406094</td>
      <td>0.197670</td>
      <td>0.081429</td>
    </tr>
    <tr>
      <th>20170503</th>
      <td>-0.657938</td>
      <td>-0.326229</td>
      <td>0.134788</td>
      <td>0.112238</td>
      <td>-0.571492</td>
      <td>-0.777890</td>
      <td>-0.267336</td>
      <td>-0.639522</td>
      <td>-0.206775</td>
      <td>-0.447106</td>
      <td>...</td>
      <td>-0.671494</td>
      <td>-1.002554</td>
      <td>-0.425115</td>
      <td>-0.389544</td>
      <td>-0.657170</td>
      <td>0.444861</td>
      <td>3.968815</td>
      <td>0.413581</td>
      <td>0.206661</td>
      <td>0.160738</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>-0.662247</td>
      <td>-0.319974</td>
      <td>0.132233</td>
      <td>0.112591</td>
      <td>-0.570338</td>
      <td>-0.779594</td>
      <td>-0.277660</td>
      <td>-0.641221</td>
      <td>-0.204759</td>
      <td>-0.444954</td>
      <td>...</td>
      <td>-0.671135</td>
      <td>-1.001230</td>
      <td>-0.404384</td>
      <td>-0.391661</td>
      <td>-0.658434</td>
      <td>0.410504</td>
      <td>3.948198</td>
      <td>0.402080</td>
      <td>0.204508</td>
      <td>0.137293</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>-0.664870</td>
      <td>-0.319372</td>
      <td>0.097919</td>
      <td>0.090680</td>
      <td>-0.571798</td>
      <td>-0.782509</td>
      <td>-0.275168</td>
      <td>-0.636404</td>
      <td>-0.208189</td>
      <td>-0.448794</td>
      <td>...</td>
      <td>-0.670085</td>
      <td>-0.997497</td>
      <td>-0.409683</td>
      <td>-0.401536</td>
      <td>-0.659185</td>
      <td>0.395936</td>
      <td>3.909582</td>
      <td>0.397496</td>
      <td>0.228932</td>
      <td>0.127569</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>-0.665537</td>
      <td>-0.328892</td>
      <td>0.075998</td>
      <td>0.078145</td>
      <td>-0.576013</td>
      <td>-0.777366</td>
      <td>-0.263822</td>
      <td>-0.619676</td>
      <td>-0.227388</td>
      <td>-0.448982</td>
      <td>...</td>
      <td>-0.667077</td>
      <td>-0.982399</td>
      <td>-0.452894</td>
      <td>-0.410854</td>
      <td>-0.656776</td>
      <td>0.412096</td>
      <td>4.041803</td>
      <td>0.375715</td>
      <td>0.217575</td>
      <td>0.144361</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>



## get_factors_ic_df
- ` jaqs_fxdayu.research.signaldigger.multi_factor.get_factors_ic_df(*args, **kwargs) `

**简要描述：**

-  获取多个因子ic值序列矩阵

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|factors_dict|是|dict of pandas.DataFrame | 若干因子组成的字典(dict),形式为:{"factor_name_1":factor_1,"factor_name_2":factor_2}。每个因子值格式为一个pd.DataFrame，索引(index)为date,column为asset|
|price |是|pandas.DataFrame|因子涉及到的股票的价格数据，用于作为进出场价用于计算收益,日期为索引，股票品种为columns|
|benchmark_price | 否  |pandas.DataFrame or pandas.Series|基准价格，日期为索引。在price参数不为空的情况下，该参数生效，用于计算因子涉及到的股票的持有期**相对收益**--相对基准。默认为空，为空时计算的收益为**绝对收益**。|
|high |否  |pandas.DataFrame|因子涉及到的股票的最高价数据,用于计算持有期潜在最大上涨收益,日期为索引，股票品种为columns,默认为空|
|low |否  |pandas.DataFrame|因子涉及到的股票的最低价数据,用于计算持有期潜在最大下跌收益,日期为索引，股票品种为columns,默认为空|
|group |否  |pandas.DataFrame|因子涉及到的股票的分组(行业分类),日期为索引，股票品种为columns,默认为空|
|period |否  |int|持有周期,默认为5,即持有5天|
|quantiles |否  |int|根据每日因子值的大小分成quantiles组,默认为5,即将因子每天分成5组|
|mask |否  |pandas.DataFrame|一张由bool值组成的表格,日期为索引，股票品种为columns，表示在做因子分析时是否要对某期的某个品种过滤。对应位置为True则**过滤**（剔除）——不纳入因子分析考虑。默认为空，不执行过滤操作|
|can_enter |否  |pandas.DataFrame|一张由bool值组成的表格,日期为索引，股票品种为columns，表示某期的某个品种是否可以买入(进场)。对应位置为True则可以买入。默认为空，任何时间任何品种均可买入|
|can_exit |否  |pandas.DataFrame|一张由bool值组成的表格,日期为索引，股票品种为columns，表示某期的某个品种是否可以卖出(出场)。对应位置为True则可以卖出。默认为空，任何时间任何品种均可卖出|
|forward |否  |bool|收益对齐方式,forward=True则在当期因子下对齐下一期实现的收益；forward=False则在当期实现收益下对齐上一期的因子值。默认为True|
|commission |否 |float|手续费比例,每次换仓收取的手续费百分比,默认为万分之八0.0008|
|ret_type |否 |string|计算何种收益的ic。目前支持的收益类型有return, upside_ret, downside_ret,分别代表固定调仓收益,潜在最大上涨收益,潜在最大下跌收益。默认为return--固定调仓收益|

**返回:**

ic_df 多个因子ic值序列矩阵
类型pd.Dataframe,索引（index）为datetime,columns为各因子名称，与factors_dict中的对应。
如：

```

         BP	　　　     CFP	　　　EP	　　ILLIQUIDITY	REVS20	　　SRMI	　　　VOL20
date
2016-06-24	0.165260	0.002198	0.085632	-0.078074	0.173832	0.214377	0.068445
2016-06-27	0.165537	0.003583	0.063299	-0.048674	0.180890	0.202724	0.081748
2016-06-28	0.135215	0.010403	0.059038	-0.034879	0.111691	0.122554	0.042489
2016-06-29	0.068774	0.019848	0.058476	-0.049971	0.042805	0.053339	0.079592
2016-06-30	0.039431	0.012271	0.037432	-0.027272	0.010902	0.077293	-0.050667
```



**示例：**


```python
from jaqs_fxdayu.research.signaldigger.multi_factor import get_factors_ic_df

factor_ic_df = get_factors_ic_df(factors_dict,
                                 price=dv.get_ts("close_adj"),
                                 high=dv.get_ts("high_adj"), # 可为空
                                 low=dv.get_ts("low_adj"),# 可为空
                                 group=dv.get_ts("sw1"), # 可为空
                                 quantiles=5,# quantile分类数
                                 period=5,# 持有期
                                 benchmark_price=dv.data_benchmark, # 基准价格 可不传入，持有期收益（return）计算为绝对收益
                                 commission = 0.0008,
                                 ret_type = 'upside_ret' # 计算最大潜在上涨收益的ic 
                                 )
factor_ic_df.dropna(how="all").head()
```

    Nan Data Count (should be zero) : 0;  Percentage of effective data: 99%
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
      <th>pb</th>
      <th>pe</th>
    </tr>
    <tr>
      <th>trade_date</th>
      <th>group</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">20170503</th>
      <th>110000</th>
      <td>0.314286</td>
      <td>-0.600000</td>
    </tr>
    <tr>
      <th>210000</th>
      <td>0.214286</td>
      <td>-0.261905</td>
    </tr>
    <tr>
      <th>220000</th>
      <td>0.021978</td>
      <td>-0.032967</td>
    </tr>
    <tr>
      <th>230000</th>
      <td>0.100000</td>
      <td>0.100000</td>
    </tr>
    <tr>
      <th>240000</th>
      <td>0.209790</td>
      <td>0.510490</td>
    </tr>
  </tbody>
</table>
</div>



## get_factors_ret_df
- ` jaqs_fxdayu.research.signaldigger.multi_factor.get_factors_ret_df(*args, **kwargs) `

**简要描述：**

-  获取多个因子收益序列矩阵

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|factors_dict|是|dict of pandas.DataFrame | 若干因子组成的字典(dict),形式为:{"factor_name_1":factor_1,"factor_name_2":factor_2}。每个因子值格式为一个pd.DataFrame，索引(index)为date,column为asset|
|price |是|pandas.DataFrame|因子涉及到的股票的价格数据，用于作为进出场价用于计算收益,日期为索引，股票品种为columns|
|benchmark_price | 否  |pandas.DataFrame or pandas.Series|基准价格，日期为索引。在price参数不为空的情况下，该参数生效，用于计算因子涉及到的股票的持有期**相对收益**--相对基准。默认为空，为空时计算的收益为**绝对收益**。|
|high |否  |pandas.DataFrame|因子涉及到的股票的最高价数据,用于计算持有期潜在最大上涨收益,日期为索引，股票品种为columns,默认为空|
|low |否  |pandas.DataFrame|因子涉及到的股票的最低价数据,用于计算持有期潜在最大下跌收益,日期为索引，股票品种为columns,默认为空|
|group |否  |pandas.DataFrame|因子涉及到的股票的分组(行业分类),日期为索引，股票品种为columns,默认为空|
|period |否  |int|持有周期,默认为5,即持有5天|
|quantiles |否  |int|根据每日因子值的大小分成quantiles组,默认为5,即将因子每天分成5组|
|mask |否  |pandas.DataFrame|一张由bool值组成的表格,日期为索引，股票品种为columns，表示在做因子分析时是否要对某期的某个品种过滤。对应位置为True则**过滤**（剔除）——不纳入因子分析考虑。默认为空，不执行过滤操作|
|can_enter |否  |pandas.DataFrame|一张由bool值组成的表格,日期为索引，股票品种为columns，表示某期的某个品种是否可以买入(进场)。对应位置为True则可以买入。默认为空，任何时间任何品种均可买入|
|can_exit |否  |pandas.DataFrame|一张由bool值组成的表格,日期为索引，股票品种为columns，表示某期的某个品种是否可以卖出(出场)。对应位置为True则可以卖出。默认为空，任何时间任何品种均可卖出|
|forward |否  |bool|收益对齐方式,forward=True则在当期因子下对齐下一期实现的收益；forward=False则在当期实现收益下对齐上一期的因子值。默认为True|
|commission |否 |float|手续费比例,每次换仓收取的手续费百分比,默认为万分之八0.0008|
|ret_type |否 |string|计算何种收益的ic。目前支持的收益类型有return, upside_ret, downside_ret,分别代表固定调仓收益,潜在最大上涨收益,潜在最大下跌收益。默认为return--固定调仓收益|

**返回:**

ret_df 多个因子收益序列矩阵
类型pd.Dataframe,索引（index）为datetime,columns为各因子名称，与factors_dict中的对应。
如：

```

         BP	　　　     CFP	　　　EP	　　ILLIQUIDITY	REVS20	　　SRMI	　　　VOL20
date
2016-06-24	0.165260	0.002198	0.085632	-0.078074	0.173832	0.214377	0.068445
2016-06-27	0.165537	0.003583	0.063299	-0.048674	0.180890	0.202724	0.081748
2016-06-28	0.135215	0.010403	0.059038	-0.034879	0.111691	0.122554	0.042489
2016-06-29	0.068774	0.019848	0.058476	-0.049971	0.042805	0.053339	0.079592
2016-06-30	0.039431	0.012271	0.037432	-0.027272	0.010902	0.077293	-0.050667
```



**示例：**


```python
from jaqs_fxdayu.research.signaldigger.multi_factor import get_factors_ret_df

factor_ret_df = get_factors_ret_df(factors_dict,
                                   price=dv.get_ts("close_adj"),
                                   high=dv.get_ts("high_adj"), # 可为空
                                   low=dv.get_ts("low_adj"),# 可为空
                                   group=dv.get_ts("sw1"), # 可为空
                                   quantiles=5,# quantile分类数
                                   period=5,# 持有期
                                   benchmark_price=dv.data_benchmark, # 基准价格 可不传入，持有期收益（return）计算为绝对收益
                                   commission = 0.0008,
                                   ret_type = 'downside_ret' # 计算最大潜在下跌收益的因子收益 
                                 )
factor_ret_df.dropna(how="all").head()
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
      <th>pb</th>
      <th>pe</th>
    </tr>
    <tr>
      <th>trade_date</th>
      <th>group</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">20170503</th>
      <th>110000</th>
      <td>-0.029078</td>
      <td>0.000052</td>
    </tr>
    <tr>
      <th>210000</th>
      <td>-0.010770</td>
      <td>-0.000389</td>
    </tr>
    <tr>
      <th>220000</th>
      <td>-0.005822</td>
      <td>-0.000566</td>
    </tr>
    <tr>
      <th>230000</th>
      <td>-0.058078</td>
      <td>0.000080</td>
    </tr>
    <tr>
      <th>240000</th>
      <td>-0.041450</td>
      <td>0.000142</td>
    </tr>
  </tbody>
</table>
</div>



## combine_factors
- ` jaqs_fxdayu.research.signaldigger.multi_factor.combine_factors(*args, **kwargs) `

**简要描述：**

-  多因子组合——最终合成一个组合因子

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|factors_dict|是|dict of pandas.DataFrame | 若干因子组成的字典(dict),形式为:{"factor_name_1":factor_1,"factor_name_2":factor_2}。每个因子值格式为一个pd.DataFrame，索引(index)为date,column为asset|
|standardize_type|否|string| 标准化方法，有"rank"（排序标准化）,"z_score"(z-score标准化)两种（"rank"/"z_score"），默认为"z_score"|
|winsorization|否|bool| 是否对结果执行去极值操作。默认不执行（False）|
|index_member |否|pandas.DataFrame of bool |是否是指数成分股。日期为索引,证券品种为columns的二维bool值表格,True代表该品种在该日期下属于指数成分股。传入该参数,则在对结果进行标准化/去极值操作时所纳入的样本只有每期横截面上属于对应指数成分股的股票，默认为空|
|weighted_method|否|string | 组合方式，目前支持'equal_weight'(等权合成),'ic_weight'(以某个时间窗口的滚动平均ic为权重), 'ir_weight'(以某个时间窗口的滚动ic_ir为权重), 'max_IR'(最大化上个持有期的ic_ir为目标处理权重)，'max_IC'(最大化上个持有期的ic为目标处理权重)。默认采取'equal_weight'(等权合成)方式。若此处参数不为'equal_weight，则还需配置接下来的props参数|
|props|weighted_method不等于'equal_weight'时必须,否则可以缺省|dict|计算加权合成因子时的必要配置信息。具体配置方式见下|

**props配置参数**

|字段|缺省值|类型|说明|
|:----    |:---|:----- |-----   |
|price |是|pandas.DataFrame|因子涉及到的股票的价格数据，用于作为进出场价用于计算收益,日期为索引，股票品种为columns|
|high |否  |pandas.DataFrame|因子涉及到的股票的最高价数据,用于计算持有期潜在最大上涨收益,日期为索引，股票品种为columns,默认为空|
|low |否  |pandas.DataFrame|因子涉及到的股票的最低价数据,用于计算持有期潜在最大下跌收益,日期为索引，股票品种为columns,默认为空|
|ret_type |否 |string|计算何种收益的ic。目前支持的收益类型有return, upside_ret, downside_ret,分别代表固定调仓收益,潜在最大上涨收益,潜在最大下跌收益。默认为return--固定调仓收益|
|benchmark_price | 否  |pandas.DataFrame or pandas.Series|基准价格，日期为索引。在price参数不为空的情况下，该参数生效，用于计算因子涉及到的股票的持有期**相对收益**--相对基准。默认为空，为空时计算的收益为**绝对收益**。|
|period |否  |int|持有周期,默认为5,即持有5天|
|quantiles |否  |int|根据每日因子值的大小分成quantiles组,默认为5,即将因子每天分成5组|
|mask |否  |pandas.DataFrame|一张由bool值组成的表格,日期为索引，股票品种为columns，表示在做因子分析时是否要对某期的某个品种过滤。对应位置为True则**过滤**（剔除）——不纳入因子分析考虑。默认为空，不执行过滤操作|
|can_enter |否  |pandas.DataFrame|一张由bool值组成的表格,日期为索引，股票品种为columns，表示某期的某个品种是否可以买入(进场)。对应位置为True则可以买入。默认为空，任何时间任何品种均可买入|
|can_exit |否  |pandas.DataFrame|一张由bool值组成的表格,日期为索引，股票品种为columns，表示某期的某个品种是否可以卖出(出场)。对应位置为True则可以卖出。默认为空，任何时间任何品种均可卖出|
|forward |否  |bool|收益对齐方式,forward=True则在当期因子下对齐下一期实现的收益；forward=False则在当期实现收益下对齐上一期的因子值。默认为True|
|commission |否 |float|手续费比例,每次换仓收取的手续费百分比,默认为万分之八0.0008|
|covariance_type |否 |string|估算协方差矩阵的方法。有'simple'（普通协方差矩阵估算），'shrink'（压缩协方差矩阵估算）两种。默认为'simple'|
|rollback_period |否 |int| 滚动窗口天数。默认为120天|

**返回:**

合成后的新因子

**示例：**


```python
from jaqs_fxdayu.research.signaldigger.multi_factor import combine_factors

props = {
    'price':dv.get_ts("close_adj"),
    'high':dv.get_ts("high_adj"), # 可为空
    'low':dv.get_ts("low_adj"),# 可为空
    'ret_type': 'return',#可选参数还有upside_ret/downside_ret 则组合因子将以优化潜在上行、下行空间为目标
    'benchmark_price': dv.data_benchmark,  # 为空计算的是绝对收益　不为空计算相对收益
    'period': 30, # 30天的持有期
    'forward': True,
    'commission': 0.0008,
    "covariance_type": "shrink",  # 协方差矩阵估算方法 还可以为"simple"
    "rollback_period": 30}  # 滚动窗口天数

comb_factor = combine_factors(factors_dict,
                              standardize_type="rank",
                              winsorization=False,
                              weighted_method="ic_weight",
                              props=props)
    

comb_factor.dropna(how="all").head()
```

    Nan Data Count (should be zero) : 0;  Percentage of effective data: 99%
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
      <th>20170726</th>
      <td>0.957447</td>
      <td>0.775076</td>
      <td>0.243161</td>
      <td>0.118541</td>
      <td>0.860182</td>
      <td>0.376900</td>
      <td>0.197568</td>
      <td>0.133739</td>
      <td>0.732523</td>
      <td>0.884498</td>
      <td>...</td>
      <td>0.987842</td>
      <td>0.328267</td>
      <td>0.753799</td>
      <td>0.902736</td>
      <td>0.975684</td>
      <td>0.033435</td>
      <td>0.051672</td>
      <td>0.422492</td>
      <td>0.556231</td>
      <td>0.066869</td>
    </tr>
    <tr>
      <th>20170727</th>
      <td>0.969605</td>
      <td>0.765957</td>
      <td>0.264438</td>
      <td>0.124620</td>
      <td>0.863222</td>
      <td>0.382979</td>
      <td>0.206687</td>
      <td>0.139818</td>
      <td>0.796353</td>
      <td>0.881459</td>
      <td>...</td>
      <td>0.987842</td>
      <td>0.343465</td>
      <td>0.747720</td>
      <td>0.899696</td>
      <td>0.975684</td>
      <td>0.024316</td>
      <td>0.048632</td>
      <td>0.419453</td>
      <td>0.534954</td>
      <td>0.082067</td>
    </tr>
    <tr>
      <th>20170728</th>
      <td>0.969605</td>
      <td>0.759878</td>
      <td>0.273556</td>
      <td>0.121581</td>
      <td>0.875380</td>
      <td>0.398176</td>
      <td>0.209726</td>
      <td>0.142857</td>
      <td>0.775076</td>
      <td>0.872340</td>
      <td>...</td>
      <td>0.987842</td>
      <td>0.352584</td>
      <td>0.762918</td>
      <td>0.896657</td>
      <td>0.975684</td>
      <td>0.030395</td>
      <td>0.048632</td>
      <td>0.404255</td>
      <td>0.525836</td>
      <td>0.091185</td>
    </tr>
    <tr>
      <th>20170731</th>
      <td>0.966565</td>
      <td>0.753799</td>
      <td>0.285714</td>
      <td>0.121581</td>
      <td>0.887538</td>
      <td>0.404255</td>
      <td>0.203647</td>
      <td>0.151976</td>
      <td>0.775076</td>
      <td>0.869301</td>
      <td>...</td>
      <td>0.987842</td>
      <td>0.376900</td>
      <td>0.759878</td>
      <td>0.896657</td>
      <td>0.975684</td>
      <td>0.039514</td>
      <td>0.036474</td>
      <td>0.395137</td>
      <td>0.522796</td>
      <td>0.094225</td>
    </tr>
    <tr>
      <th>20170801</th>
      <td>0.960486</td>
      <td>0.753799</td>
      <td>0.282675</td>
      <td>0.124620</td>
      <td>0.887538</td>
      <td>0.425532</td>
      <td>0.237082</td>
      <td>0.167173</td>
      <td>0.765957</td>
      <td>0.869301</td>
      <td>...</td>
      <td>0.990881</td>
      <td>0.395137</td>
      <td>0.738602</td>
      <td>0.896657</td>
      <td>0.975684</td>
      <td>0.045593</td>
      <td>0.033435</td>
      <td>0.398176</td>
      <td>0.510638</td>
      <td>0.100304</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>


