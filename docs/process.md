
# 介绍
提供常用的因子处理操作，如去极值，中性化等

## standardize
- ` jaqs_fxdayu.research.signaldigger.process.standardize(factor_df, index_member=None) `

**简要描述：**

- 横截面z-score标准化

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|factor_df |是|pandas.DataFrame |日期为索引,证券品种为columns的二维因子表格|
|index_member |否|pandas.DataFrame of bool |是否是指数成分股。日期为索引,证券品种为columns的二维bool值表格,True代表该品种在该日期下属于指数成分股。传入该参数,则进行标准化所纳入的样本只有每期横截面上属于对应指数成分股的股票，默认为空|

**返回:**

标准化后的因子

**示例：**


```python
import warnings
warnings.filterwarnings('ignore')
```


```python
from jaqs_fxdayu.data import DataView
from jaqs_fxdayu.research.signaldigger.process import standardize

# 加载dataview数据集
dv = DataView()
dataview_folder = './data'
dv.load_dataview(dataview_folder)

# z-score标准化
standardize(factor_df = dv.get_ts("pe"), index_member = dv.get_ts("index_member")).head()
```

    Dataview loaded successfully.





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
      <td>-0.363380</td>
      <td>-0.340032</td>
      <td>-0.106714</td>
      <td>0.152518</td>
      <td>-0.266414</td>
      <td>0.216918</td>
      <td>0.086421</td>
      <td>0.857408</td>
      <td>-0.411592</td>
      <td>-0.343106</td>
      <td>...</td>
      <td>-0.366394</td>
      <td>0.891601</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.361782</td>
      <td>0.677455</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.248940</td>
      <td>0.131240</td>
    </tr>
    <tr>
      <th>20170503</th>
      <td>-0.364271</td>
      <td>-0.341856</td>
      <td>-0.107757</td>
      <td>0.151190</td>
      <td>-0.268283</td>
      <td>0.219121</td>
      <td>0.083804</td>
      <td>0.852450</td>
      <td>-0.412694</td>
      <td>-0.344699</td>
      <td>...</td>
      <td>-0.367529</td>
      <td>0.879934</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.363002</td>
      <td>0.697502</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.248411</td>
      <td>0.128307</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>-0.364991</td>
      <td>-0.340861</td>
      <td>-0.107070</td>
      <td>0.154148</td>
      <td>-0.267100</td>
      <td>0.213994</td>
      <td>0.078180</td>
      <td>0.849831</td>
      <td>-0.412865</td>
      <td>-0.344161</td>
      <td>...</td>
      <td>-0.367343</td>
      <td>0.871015</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.363119</td>
      <td>0.674523</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.248024</td>
      <td>0.118993</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>-0.364277</td>
      <td>-0.339788</td>
      <td>-0.116436</td>
      <td>0.142003</td>
      <td>-0.266276</td>
      <td>0.199128</td>
      <td>0.080549</td>
      <td>0.857999</td>
      <td>-0.412033</td>
      <td>-0.343666</td>
      <td>...</td>
      <td>-0.365914</td>
      <td>0.858166</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.362034</td>
      <td>0.659895</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.243558</td>
      <td>0.114178</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>-0.360932</td>
      <td>-0.337663</td>
      <td>-0.121213</td>
      <td>0.133428</td>
      <td>-0.265375</td>
      <td>0.197282</td>
      <td>0.087274</td>
      <td>0.871560</td>
      <td>-0.408468</td>
      <td>-0.340375</td>
      <td>...</td>
      <td>-0.361849</td>
      <td>0.824399</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.358094</td>
      <td>0.662941</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.242522</td>
      <td>0.121454</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>



## winsorize
- ` jaqs_fxdayu.research.signaldigger.process.winsorize(factor_df, alpha=0.05, index_member=None) `

**简要描述：**

- 横截面去极值

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|factor_df |是|pandas.DataFrame |日期为索引,证券品种为columns的二维因子表格|
|alpha |否|float|去极值的边界，如0.05代表去掉左右两边各2.5%分位的极端值(保留中心部分95%分布的数据)。默认0.05|
|index_member |否|pandas.DataFrame of bool |是否是指数成分股。日期为索引,证券品种为columns的二维bool值表格,True代表该品种在该日期下属于指数成分股。传入该参数,则进行去极值所纳入的样本只有每期横截面上属于对应指数成分股的股票，默认为空|

**返回:**

去极值后的因子

**示例：**


```python
from jaqs_fxdayu.research.signaldigger.process import winsorize

winsorize(factor_df = dv.get_ts("pe"), 
          alpha=0.05,
          index_member = dv.get_ts("index_member")).head()
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
      <td>6.7925</td>
      <td>10.0821</td>
      <td>42.9544</td>
      <td>79.4778</td>
      <td>20.4542</td>
      <td>88.5511</td>
      <td>70.1653</td>
      <td>178.7903</td>
      <td>0.0</td>
      <td>9.6490</td>
      <td>...</td>
      <td>6.3679</td>
      <td>183.6078</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>7.0177</td>
      <td>153.4365</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>22.9161</td>
      <td>76.4800</td>
    </tr>
    <tr>
      <th>20170503</th>
      <td>6.7697</td>
      <td>9.9035</td>
      <td>42.6314</td>
      <td>78.8332</td>
      <td>20.1893</td>
      <td>88.3302</td>
      <td>69.4123</td>
      <td>176.8719</td>
      <td>0.0</td>
      <td>9.5060</td>
      <td>...</td>
      <td>6.3143</td>
      <td>180.7143</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>6.9472</td>
      <td>155.2097</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>22.9674</td>
      <td>75.6340</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>6.6405</td>
      <td>9.9876</td>
      <td>42.4161</td>
      <td>78.6490</td>
      <td>20.2187</td>
      <td>86.9501</td>
      <td>68.1117</td>
      <td>175.1454</td>
      <td>0.0</td>
      <td>9.5298</td>
      <td>...</td>
      <td>6.3143</td>
      <td>178.0838</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>6.9002</td>
      <td>150.8288</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>22.8647</td>
      <td>73.7727</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>6.5570</td>
      <td>9.9193</td>
      <td>40.5860</td>
      <td>76.0703</td>
      <td>20.0127</td>
      <td>83.9137</td>
      <td>67.6325</td>
      <td>174.3781</td>
      <td>0.0</td>
      <td>9.3869</td>
      <td>...</td>
      <td>6.3322</td>
      <td>174.4011</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>6.8649</td>
      <td>147.1780</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>23.1319</td>
      <td>72.2499</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>6.5114</td>
      <td>9.6988</td>
      <td>39.3479</td>
      <td>74.2284</td>
      <td>19.6007</td>
      <td>82.9752</td>
      <td>67.9063</td>
      <td>175.3372</td>
      <td>0.0</td>
      <td>9.3273</td>
      <td>...</td>
      <td>6.3858</td>
      <td>168.8771</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>6.9002</td>
      <td>146.7608</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>22.7311</td>
      <td>72.5883</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>



## rank_standardize
- ` jaqs_fxdayu.research.signaldigger.process.rank_standardize(factor_df, index_member=None) `

**简要描述：**

- 排序标准化。将因子处理成横截面上的排序值（升序），并处理到0-1之间——仅保留原因子的顺序特征，剔除分布特征

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|factor_df |是|pandas.DataFrame |日期为索引,证券品种为columns的二维因子表格|
|index_member |否|pandas.DataFrame of bool |是否是指数成分股。日期为索引,证券品种为columns的二维bool值表格,True代表该品种在该日期下属于指数成分股。传入该参数,则进行排序标准化所纳入的样本只有每期横截面上属于对应指数成分股的股票，默认为空|

**返回:**

排序标准化后的因子

**示例：**


```python
from jaqs_fxdayu.research.signaldigger.process import rank_standardize

rank_standardize(factor_df = dv.get_ts("pe"), 
                 index_member = dv.get_ts("index_member")).head()
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
      <td>0.063545</td>
      <td>0.117057</td>
      <td>0.722408</td>
      <td>0.886288</td>
      <td>0.361204</td>
      <td>0.90301</td>
      <td>0.862876</td>
      <td>0.966555</td>
      <td>0.0</td>
      <td>0.107023</td>
      <td>...</td>
      <td>0.053512</td>
      <td>0.969900</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.070234</td>
      <td>0.943144</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.408027</td>
      <td>0.876254</td>
    </tr>
    <tr>
      <th>20170503</th>
      <td>0.063545</td>
      <td>0.113712</td>
      <td>0.722408</td>
      <td>0.886288</td>
      <td>0.354515</td>
      <td>0.90301</td>
      <td>0.859532</td>
      <td>0.966555</td>
      <td>0.0</td>
      <td>0.100334</td>
      <td>...</td>
      <td>0.053512</td>
      <td>0.969900</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.066890</td>
      <td>0.939799</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.408027</td>
      <td>0.872910</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>0.063545</td>
      <td>0.113712</td>
      <td>0.725753</td>
      <td>0.886288</td>
      <td>0.357860</td>
      <td>0.90301</td>
      <td>0.852843</td>
      <td>0.963211</td>
      <td>0.0</td>
      <td>0.100334</td>
      <td>...</td>
      <td>0.053512</td>
      <td>0.969900</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.066890</td>
      <td>0.939799</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.408027</td>
      <td>0.872910</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>0.063545</td>
      <td>0.113712</td>
      <td>0.712375</td>
      <td>0.882943</td>
      <td>0.351171</td>
      <td>0.90301</td>
      <td>0.859532</td>
      <td>0.963211</td>
      <td>0.0</td>
      <td>0.100334</td>
      <td>...</td>
      <td>0.053512</td>
      <td>0.966555</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.070234</td>
      <td>0.943144</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.424749</td>
      <td>0.872910</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>0.060201</td>
      <td>0.103679</td>
      <td>0.719064</td>
      <td>0.882943</td>
      <td>0.331104</td>
      <td>0.90301</td>
      <td>0.862876</td>
      <td>0.969900</td>
      <td>0.0</td>
      <td>0.096990</td>
      <td>...</td>
      <td>0.053512</td>
      <td>0.963211</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.070234</td>
      <td>0.946488</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.421405</td>
      <td>0.879599</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>



## get_disturbed_factor
- ` jaqs_fxdayu.research.signaldigger.process.rank_standardizeget_disturbed_factor(factor_df) `

**简要描述：**

- 将因子值加一个极小的扰动项,用于对quantile分组做区分

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|factor_df |是|pandas.DataFrame |日期为索引,证券品种为columns的二维因子表格|

**返回:**

加扰动项后的因子

**示例：**


```python
from jaqs_fxdayu.research.signaldigger.process import get_disturbed_factor

get_disturbed_factor(factor_df = dv.get_ts("pe")).head()
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
      <td>6.7925</td>
      <td>10.0821</td>
      <td>42.9544</td>
      <td>79.4778</td>
      <td>20.4542</td>
      <td>88.5511</td>
      <td>70.1653</td>
      <td>178.7903</td>
      <td>3.437688e-10</td>
      <td>9.6490</td>
      <td>...</td>
      <td>6.3679</td>
      <td>183.6078</td>
      <td>32.7886</td>
      <td>9.8565</td>
      <td>7.0177</td>
      <td>153.4365</td>
      <td>50.8349</td>
      <td>31.0157</td>
      <td>22.9161</td>
      <td>76.4800</td>
    </tr>
    <tr>
      <th>20170503</th>
      <td>6.7697</td>
      <td>9.9035</td>
      <td>42.6314</td>
      <td>78.8332</td>
      <td>20.1893</td>
      <td>88.3302</td>
      <td>69.4123</td>
      <td>176.8719</td>
      <td>4.412786e-10</td>
      <td>9.5060</td>
      <td>...</td>
      <td>6.3143</td>
      <td>180.7143</td>
      <td>30.2450</td>
      <td>9.8817</td>
      <td>6.9472</td>
      <td>155.2097</td>
      <td>50.7259</td>
      <td>31.0311</td>
      <td>22.9674</td>
      <td>75.6340</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>6.6405</td>
      <td>9.9876</td>
      <td>42.4161</td>
      <td>78.6490</td>
      <td>20.2187</td>
      <td>86.9501</td>
      <td>68.1117</td>
      <td>175.1454</td>
      <td>4.559244e-10</td>
      <td>9.5298</td>
      <td>...</td>
      <td>6.3143</td>
      <td>178.0838</td>
      <td>31.4771</td>
      <td>9.8188</td>
      <td>6.9002</td>
      <td>150.8288</td>
      <td>50.3727</td>
      <td>30.6805</td>
      <td>22.8647</td>
      <td>73.7727</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>6.5570</td>
      <td>9.9193</td>
      <td>40.5860</td>
      <td>76.0703</td>
      <td>20.0127</td>
      <td>83.9137</td>
      <td>67.6325</td>
      <td>174.3781</td>
      <td>6.587699e-10</td>
      <td>9.3869</td>
      <td>...</td>
      <td>6.3322</td>
      <td>174.4011</td>
      <td>30.8809</td>
      <td>9.5609</td>
      <td>6.8649</td>
      <td>147.1780</td>
      <td>49.3963</td>
      <td>30.2527</td>
      <td>23.1319</td>
      <td>72.2499</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>6.5114</td>
      <td>9.6988</td>
      <td>39.3479</td>
      <td>74.2284</td>
      <td>19.6007</td>
      <td>82.9752</td>
      <td>67.9063</td>
      <td>175.3372</td>
      <td>6.254412e-10</td>
      <td>9.3273</td>
      <td>...</td>
      <td>6.3858</td>
      <td>168.8771</td>
      <td>27.9399</td>
      <td>9.3282</td>
      <td>6.9002</td>
      <td>146.7608</td>
      <td>50.3779</td>
      <td>29.5167</td>
      <td>22.7311</td>
      <td>72.5883</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>



## neutralize
- ` jaqs_fxdayu.research.signaldigger.process.neutralize(factor_df,group,float_mv=None,index_member=None) `

**简要描述：**

- 对因子做行业、市值中性化

**参数:**

|字段|必选|类型|说明|
|:----    |:---|:----- |-----   |
|factor_df |是|pandas.DataFrame |因子。日期为索引,证券品种为columns的二维表格|
|group |是|pandas.DataFrame |行业分类（也可以是其他分组方式）。日期为索引,证券品种为columns的二维表格,对应每一个品种在某期所属的分类|
|float_mv |否|pandas.DataFrame |流通市值。日期为索引,证券品种为columns的二维表格。默认为空,为空时不进行市值中性化处理|
|index_member |否|pandas.DataFrame of bool |是否是指数成分股。日期为索引,证券品种为columns的二维bool值表格,True代表该品种在该日期下属于指数成分股。传入该参数,则进行行业、市值中性化所纳入的样本只有每期横截面上属于对应指数成分股的股票，默认为空|

**返回:**

行业、市值中性化后的因子

**示例：**


```python
from jaqs_fxdayu.research.signaldigger.process import neutralize

neutralize(factor_df = dv.get_ts("pe"),
           group = dv.get_ts("sw1")).head()
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
      <td>-2.662629</td>
      <td>-7.782230</td>
      <td>-27.98201</td>
      <td>-38.33350</td>
      <td>-4.083109</td>
      <td>17.61469</td>
      <td>-83.013425</td>
      <td>107.385838</td>
      <td>-168.217857</td>
      <td>-8.215330</td>
      <td>...</td>
      <td>-3.087229</td>
      <td>26.912500</td>
      <td>9.87725</td>
      <td>0.401371</td>
      <td>-2.437429</td>
      <td>108.584833</td>
      <td>3.357346</td>
      <td>-55.150405</td>
      <td>-6.266428</td>
      <td>-76.698725</td>
    </tr>
    <tr>
      <th>20170503</th>
      <td>-2.682662</td>
      <td>-7.829960</td>
      <td>-28.76077</td>
      <td>-39.50720</td>
      <td>-3.544909</td>
      <td>16.93803</td>
      <td>-83.589442</td>
      <td>105.819463</td>
      <td>-168.313357</td>
      <td>-8.227460</td>
      <td>...</td>
      <td>-3.138062</td>
      <td>24.588600</td>
      <td>8.60545</td>
      <td>0.429338</td>
      <td>-2.505162</td>
      <td>110.440158</td>
      <td>3.330400</td>
      <td>-55.949523</td>
      <td>-6.084489</td>
      <td>-77.367742</td>
    </tr>
    <tr>
      <th>20170504</th>
      <td>-2.815043</td>
      <td>-7.733890</td>
      <td>-28.67189</td>
      <td>-38.74790</td>
      <td>-4.016945</td>
      <td>15.86211</td>
      <td>-82.429800</td>
      <td>104.271487</td>
      <td>-168.140586</td>
      <td>-8.191690</td>
      <td>...</td>
      <td>-3.141243</td>
      <td>26.910367</td>
      <td>9.39235</td>
      <td>0.363257</td>
      <td>-2.555343</td>
      <td>106.489883</td>
      <td>3.025662</td>
      <td>-55.572859</td>
      <td>-6.116911</td>
      <td>-76.768800</td>
    </tr>
    <tr>
      <th>20170505</th>
      <td>-2.762233</td>
      <td>-7.653145</td>
      <td>-28.89854</td>
      <td>-37.39795</td>
      <td>-3.835882</td>
      <td>14.42916</td>
      <td>-82.012883</td>
      <td>103.912075</td>
      <td>-167.959957</td>
      <td>-8.185545</td>
      <td>...</td>
      <td>-2.987033</td>
      <td>27.853900</td>
      <td>9.18745</td>
      <td>0.241667</td>
      <td>-2.454333</td>
      <td>103.302950</td>
      <td>2.387592</td>
      <td>-55.251945</td>
      <td>-5.618411</td>
      <td>-77.395483</td>
    </tr>
    <tr>
      <th>20170508</th>
      <td>-2.564538</td>
      <td>-7.591140</td>
      <td>-29.02696</td>
      <td>-36.10530</td>
      <td>-3.576855</td>
      <td>14.60034</td>
      <td>-80.613975</td>
      <td>104.639975</td>
      <td>-167.807429</td>
      <td>-7.962640</td>
      <td>...</td>
      <td>-2.690138</td>
      <td>30.356133</td>
      <td>7.68590</td>
      <td>0.252262</td>
      <td>-2.175738</td>
      <td>102.756587</td>
      <td>4.286408</td>
      <td>-54.397259</td>
      <td>-5.803628</td>
      <td>-75.931975</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 330 columns</p>
</div>


