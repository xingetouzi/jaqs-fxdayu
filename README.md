# jaqs-fxdayu:股票多因子策略研究和分析框架jaqs拓展包

## 介绍

大鱼金融在jaqs官方版本的基础上,重点改进和优化了股票多因子研究部分的功能,帮助使用者更方便的去设计/评估和分析因子表现,优化因子效果，进行因子组合研究．

主要包括:

### 基础：
- dataview

可视为一个基于pandas的针对因子场景的数据库,方便因子的设计实现.大鱼金融fork版改进了官方版本,提供更便捷灵活的因子数据查询和操作功能

- digger

单因子分析及绩效可视化.改进官方版本

### 拓展：
- analysis

单因子多维度分析.从因子ic,因子收益,选股潜在收益空间三个维度给出因子评价.新增模块

- process

提供常用的因子处理操作，如去极值，中性化等.新增模块

- optimizer

提供因子参数优化功能.新增模块

- multi_factor

提供多因子处理和组合功能.新增模块

## 安装和更新
### 依赖
该模块基于JAQS进行拓展，且只支持`python3`，需要安装：`jaqs>=0.6.10`

### 安装
```bash
$ pip install jaqs_fxdayu
```

### 更新
当有新版本发布时，使用以下命令更新
```bash
$ pip uninstall jaqs_fxdayu
$ pip install jaqs_fxdayu
```

## 使用
该模块主要分为两部分：

### 基础API：
基于jaqs项目的原有模块进行替换和拓展。
支持monkey_patch或直接从jaqs_fxdayu中导入。

以使用Dataview为例：

- monkey_patch:
```
import jaqs_fxdayu
jaqs_fxdayu.patch_all() # 需要放在任何import jaqs.* 之前

from jaqs.data import DataView

dv = DataView()

...
```

!!! Note
    该使用方法的好处是最大程度兼容原生JAQS的代码，方便迁移。

- 直接导入:
```
from jaqs_fxdayu.data import DataView

dv = DataView()

...
```

!!! Note
    该使用方法的好处是更为直观，且支持IDE的静态代码提示功能。

### 拓展API：
主要为独立开发，提供一些因子分析中常用，而jaqs中未实现的拓展功能。
使用方法主要是从jaqs_fxdayu模块中导入:
例如：
```python
from jaqs_fxdayu.research import Optimizer
```


### 文档

[详细文档地址](http://jaqs-fxdayu.readthedocs.io/zh_CN/latest/)

## 最新功能
### 2018/3/20

作为单独模块发布，更新文档

### 2018/3/19 更新

新增dataview-fields可选字段查询方式，详见文档　dataview-fields可选字段查询方式

## 技术支持

- [GitHub](https://github.com/xingetouzi/jaqs_fxdayu/tree/master)
- [访问大鱼学院获得更多的案例和金融量化知识](http://www.fxdayu.com)
- 加qq群(372592121)进行讨论
