# encoding=utf-8
from functools import reduce
from . import process
import pandas as pd
import numpy as np
from sklearn.covariance import LedoitWolf
import jaqs.util as jutil
from . import performance as pfm
from . import SignalCreator
import statsmodels.api as sm


# 因子间存在较强同质性时，使用施密特正交化方法对因子做正交化处理，用得到的正交化残差作为因子
def orthogonalize(factors_dict=None,
                  standardize_type="z_score",
                  winsorization=False,
                  index_member=None):
    """
    # 因子间存在较强同质性时，使用施密特正交化方法对因子做正交化处理，用得到的正交化残差作为因子
    :param index_member:
    :param factors_dict: 若干因子组成的字典(dict),形式为:
                         {"factor_name_1":factor_1,"factor_name_2":factor_2}
                       　每个因子值格式为一个pd.DataFrame，索引(index)为date,column为asset
    :param standardize_type: 标准化方法，有"rank"（排序标准化）,"z_score"(z-score标准化)两种（"rank"/"z_score"）
    :return: factors_dict（new) 正交化处理后所得的一系列新因子。
    """

    from scipy import linalg
    from functools import partial

    def Schmidt(data):
        return linalg.orth(data)

    def get_vector(date, factor):
        return factor.loc[date]

    if not factors_dict or len(list(factors_dict.keys())) < 2:
        raise ValueError("你需要给定至少２个因子")

    new_factors_dict = {}  # 用于记录正交化后的因子值
    for factor_name in factors_dict.keys():
        new_factors_dict[factor_name] = []
        # 处理非法值
        factors_dict[factor_name] = jutil.fillinf(factors_dict[factor_name])
        factors_dict[factor_name] = process._mask_non_index_member(factors_dict[factor_name],
                                                                   index_member=index_member)
        if winsorization:
            factors_dict[factor_name] = process.winsorize(factors_dict[factor_name])

    factor_name_list = list(factors_dict.keys())
    factor_value_list = list(factors_dict.values())
    # 施密特正交
    for date in factor_value_list[0].index:
        data = list(map(partial(get_vector, date), factor_value_list))
        data = pd.concat(data, axis=1, join="inner")
        data = data.dropna()
        if len(data) == 0:
            continue
        data = pd.DataFrame(Schmidt(data), index=data.index)
        data.columns = factor_name_list
        for factor_name in factor_name_list:
            row = pd.DataFrame(data[factor_name]).T
            row.index = [date, ]
            new_factors_dict[factor_name].append(row)

    # 因子标准化
    for factor_name in factor_name_list:
        factor_value = pd.concat(new_factors_dict[factor_name])
        # 恢复在正交化过程中剔除的行和列
        factor_value = factor_value.reindex(index=factor_value_list[0].index,columns=factor_value_list[0].columns)
        if standardize_type == "z_score":
            new_factors_dict[factor_name] = process.standardize(factor_value, index_member)
        else:
            new_factors_dict[factor_name] = process.rank_standardize(factor_value, index_member)

    return new_factors_dict


# 获取多个因子收益序列矩阵
def get_factors_ret_df(factors_dict,
                       price=None, daily_ret=None,
                       benchmark_price=None, daily_benchmark_ret=None,
                       high=None, low=None,
                       group=None,
                       period=5, n_quantiles=5,
                       mask=None,
                       can_enter=None,
                       can_exit=None,
                       forward=True,
                       commission=0.0008,
                       ret_type="return",
                       **kwargs):
    """
    获取多个因子收益序列矩阵
    :param factors_dict: 若干因子组成的字典(dict),形式为:
                         {"factor_name_1":factor_1,"factor_name_2":factor_2}
    :param period: 指定持有周期(int)
    :param n_quantiles: 根据因子大小将股票池划分的分位数量(int)
    :param price : 包含了pool中所有股票的价格时间序列(pd.Dataframe)，索引（index)为datetime,columns为各股票代码，与pool对应。
    :param benchmark_price:基准收益，不为空计算相对收益，否则计算绝对收益
    :return: ret_df 多个因子收益序列矩阵
             类型pd.Dataframe,索引（index）为datetime,columns为各因子名称，与factors_dict中的对应。
             如：

            　　　　　　　　　　　BP	　　　CFP	　　　EP	　　ILLIQUIDITY	REVS20	　　　SRMI	　　　VOL20
            date
            2016-06-24	0.165260	0.002198	0.085632	-0.078074	0.173832	0.214377	0.068445
            2016-06-27	0.165537	0.003583	0.063299	-0.048674	0.180890	0.202724	0.081748
            2016-06-28	0.135215	0.010403	0.059038	-0.034879	0.111691	0.122554	0.042489
            2016-06-29	0.068774	0.019848	0.058476	-0.049971	0.042805	0.053339	0.079592
            2016-06-30	0.039431	0.012271	0.037432	-0.027272	0.010902	0.077293	-0.050667
    """

    def stack_td_symbol(df):
        df = pd.DataFrame(df.stack(dropna=False))  # do not dropna
        df.index.names = ['trade_date', 'symbol']
        df.sort_index(axis=0, level=['trade_date', 'symbol'], inplace=True)
        return df

    def get_regression_result(df):
        ret = df.pop("return")
        if "group" in df.columns:
            df = df.drop("group", axis=1)
        ols_model = sm.OLS(ret, df)
        regression_results = ols_model.fit()
        return regression_results.params

    if ret_type is None:
        ret_type = "return"

    if not (ret_type in ["return", "upside_ret", "downside_ret"]):
        raise ValueError("不支持对%s收益的ic计算!支持的收益类型有return, upside_ret, downside_ret." % (ret_type,))

    sc = SignalCreator(
        price=price, daily_ret=daily_ret,
        benchmark_price=benchmark_price, daily_benchmark_ret=daily_benchmark_ret,
        high=high, low=low,
        group=group,
        period=period, n_quantiles=n_quantiles,
        mask=mask,
        can_enter=can_enter,
        can_exit=can_exit,
        forward=forward,
        commission=commission
    )

    res = None

    # 获取factor_value的时间（index）,将用来生成 factors_ic_df 的对应时间（index）
    times = sorted(
        pd.concat([pd.Series(factors_dict[factor_name].index) for factor_name in factors_dict.keys()]).unique())
    for factor_name in factors_dict.keys():
        signal = factors_dict[factor_name]
        if (not isinstance(signal, pd.DataFrame)) or (signal.size == 0):
            raise ValueError("因子%s为空或不合法!请确保传入因子有值且数据类型为pandas.DataFrame." % (factor_name,))
        sc._judge(signal)
        sc._cal_ret()
        if ret_type not in sc.signal_ret.keys():
            raise ValueError("无法计算%s收益,请重新设置输入参数." % (ret_type,))
        if res is None:
            res = stack_td_symbol(sc.signal_ret[ret_type]).fillna(0)
            res.columns = ["return"]
        signal = jutil.fillinf(signal)
        signal = signal.shift(1)  # avoid forward-looking bias
        if not forward:
            signal = signal.shift(period)
        res[factor_name] = stack_td_symbol(signal)

    grouper = ['trade_date']
    if group is not None:
        res["group"] = stack_td_symbol(group)
        grouper.append('group')

    res = res.dropna()
    result = res.groupby(grouper).apply(get_regression_result)

    if group is None:
        result = result.dropna(how="all").reindex(times)
    else:
        result = result.dropna(how="all")
        result = result.reindex(pd.MultiIndex.from_product([times, result.index.levels[1]],
                                                           names=["trade_date", "group"]))
    return result


# 获取因子的ic序列
def get_factors_ic_df(factors_dict,
                      price=None, daily_ret=None,
                      benchmark_price=None, daily_benchmark_ret=None,
                      high=None, low=None,
                      group=None,
                      period=5, n_quantiles=5,
                      mask=None,
                      can_enter=None,
                      can_exit=None,
                      forward=True,
                      commission=0.0008,
                      ret_type="return",
                      **kwargs):
    """
    获取多个因子ic值序列矩阵
    :param factors_dict: 若干因子组成的字典(dict),形式为:
                         {"factor_name_1":factor_1,"factor_name_2":factor_2}
    :param period: 指定持有周期(int)
    :param n_quantiles: 根据因子大小将股票池划分的分位数量(int)
    :param price : 包含了pool中所有股票的价格时间序列(pd.Dataframe)，索引（index)为datetime,columns为各股票代码，与pool对应。
    :param benchmark_price:基准收益，不为空计算相对收益，否则计算绝对收益
    :return: ic_df 多个因子ｉc值序列矩阵
             类型pd.Dataframe,索引（index）为datetime,columns为各因子名称，与factors_dict中的对应。
             如：

            　　　　　　　　　　　BP	　　　CFP	　　　EP	　　ILLIQUIDITY	REVS20	　　　SRMI	　　　VOL20
            date
            2016-06-24	0.165260	0.002198	0.085632	-0.078074	0.173832	0.214377	0.068445
            2016-06-27	0.165537	0.003583	0.063299	-0.048674	0.180890	0.202724	0.081748
            2016-06-28	0.135215	0.010403	0.059038	-0.034879	0.111691	0.122554	0.042489
            2016-06-29	0.068774	0.019848	0.058476	-0.049971	0.042805	0.053339	0.079592
            2016-06-30	0.039431	0.012271	0.037432	-0.027272	0.010902	0.077293	-0.050667
    """
    if ret_type is None:
        ret_type = "return"

    if not (ret_type in ["return", "upside_ret", "downside_ret"]):
        raise ValueError("不支持对%s收益的ic计算!支持的收益类型有return, upside_ret, downside_ret." % (ret_type,))

    ic_table = []
    sc = SignalCreator(
        price=price, daily_ret=daily_ret,
        benchmark_price=benchmark_price, daily_benchmark_ret=daily_benchmark_ret,
        high=high, low=low,
        group=group,
        period=period, n_quantiles=n_quantiles,
        mask=mask,
        can_enter=can_enter,
        can_exit=can_exit,
        forward=forward,
        commission=commission
    )
    # 获取factor_value的时间（index）,将用来生成 factors_ic_df 的对应时间（index）
    times = sorted(
        pd.concat([pd.Series(factors_dict[factor_name].index) for factor_name in factors_dict.keys()]).unique())
    for factor_name in factors_dict.keys():
        factor_value = factors_dict[factor_name]
        if (not isinstance(factor_value, pd.DataFrame)) or (factor_value.size == 0):
            raise ValueError("因子%s为空或不合法!请确保传入因子有值且数据类型为pandas.DataFrame." % (factor_name,))
        signal_data = sc.get_signal_data(factor_value)
        if ret_type in signal_data.columns:
            origin_fields = ["signal", ret_type]
            new_fields = ["signal", "return"]
            if group is not None:
                origin_fields.append("group")
                new_fields.append("group")
            signal_data = signal_data[origin_fields]
            signal_data.columns = new_fields
            ic = pd.DataFrame(pfm.calc_signal_ic(signal_data, group is not None))
            ic.columns = [factor_name, ]
            ic_table.append(ic)
        else:
            raise ValueError("signal_data中不包含%s收益,无法进行ic计算!" % (ret_type,))

    if group is None:
        ic_df = pd.concat(ic_table, axis=1).dropna(how="all").reindex(times)
    else:
        ic_df = pd.concat(ic_table, axis=1).dropna(how="all")
        ic_df = ic_df.reindex(pd.MultiIndex.from_product([times,ic_df.index.levels[1]],
                                                         names=["trade_date","group"]))
    return ic_df


# 根据样本协方差矩阵估算结果求最大化IC_IR下的多因子组合权重
def max_IR_weight(ic_df,
                  holding_period,
                  rollback_period=120,
                  covariance_type="shrink"):
    """
    输入ic_df(ic值序列矩阵),指定持有期和滚动窗口，给出相应的多因子组合权重
    :param ic_df: ic值序列矩阵 （pd.Dataframe），索引（index）为datetime,columns为各因子名称。
             如：

            　　　　　　　　　　　BP	　　　CFP	　　　EP	　　ILLIQUIDITY	REVS20	　　　SRMI	　　　VOL20
            date
            2016-06-24	0.165260	0.002198	0.085632	-0.078074	0.173832	0.214377	0.068445
            2016-06-27	0.165537	0.003583	0.063299	-0.048674	0.180890	0.202724	0.081748
            2016-06-28	0.135215	0.010403	0.059038	-0.034879	0.111691	0.122554	0.042489
            2016-06-29	0.068774	0.019848	0.058476	-0.049971	0.042805	0.053339	0.079592
            2016-06-30	0.039431	0.012271	0.037432	-0.027272	0.010902	0.077293	-0.050667

    :param holding_period: 持有周期(int)
    :param rollback_period: 滚动窗口，即计算每一天的因子权重时，使用了之前rollback_period下的IC时间序列来计算IC均值向量和IC协方差矩阵（int)。
    :param covariance_type:"shrink"/"simple" 协防差矩阵估算方式　Ledoit-Wolf压缩估计或简单估计
    :return: weight_df:使用Sample协方差矩阵估算方法得到的因子权重(pd.Dataframe),
             索引（index)为datetime,columns为待合成的因子名称。
    """
    # 最大化t-n ~ t天的ic_ir,用到了截止到t+period的数据（算收益）,
    # 算得的权重用于t+period的因子进行加权
    n = rollback_period
    weight_df = pd.DataFrame(index=ic_df.index, columns=ic_df.columns)
    lw = LedoitWolf()
    for dt in ic_df.index:
        ic_dt = ic_df[ic_df.index <= dt].tail(n)
        if len(ic_dt) < n:
            continue
        if covariance_type == "shrink":
            try:
                ic_cov_mat = lw.fit(ic_dt.as_matrix()).covariance_
            except:
                ic_cov_mat = np.mat(np.cov(ic_dt.T.as_matrix()).astype(float))
        else:
            ic_cov_mat = np.mat(np.cov(ic_dt.T.as_matrix()).astype(float))
        inv_ic_cov_mat = np.linalg.inv(ic_cov_mat)
        weight = inv_ic_cov_mat * np.mat(ic_dt.mean().values).reshape(len(inv_ic_cov_mat), 1)
        weight = np.array(weight.reshape(len(weight), ))[0]
        weight_df.ix[dt] = weight / np.sum(np.abs(weight))

    return weight_df.shift(holding_period)


# 根据样本协方差矩阵估算结果求最大化单期IC下的多因子组合权重
def max_IC_weight(ic_df,
                  factors_dict,
                  holding_period,
                  covariance_type="shrink"):
    """
    输入ic_df(ic值序列矩阵),指定持有期和滚动窗口，给出相应的多因子组合权重
    :param factors_dict: 若干因子组成的字典(dict),形式为:
                         {"factor_name_1":factor_1,"factor_name_2":factor_2}
                       　每个因子值格式为一个pd.DataFrame，索引(index)为date,column为asset
    :param ic_df: ic值序列矩阵 （pd.Dataframe），索引（index）为datetime,columns为各因子名称。
             如：

            　　　　　　　　　　　BP	　　　CFP	　　　EP	　　ILLIQUIDITY	REVS20	　　　SRMI	　　　VOL20
            date
            2016-06-24	0.165260	0.002198	0.085632	-0.078074	0.173832	0.214377	0.068445
            2016-06-27	0.165537	0.003583	0.063299	-0.048674	0.180890	0.202724	0.081748
            2016-06-28	0.135215	0.010403	0.059038	-0.034879	0.111691	0.122554	0.042489
            2016-06-29	0.068774	0.019848	0.058476	-0.049971	0.042805	0.053339	0.079592
            2016-06-30	0.039431	0.012271	0.037432	-0.027272	0.010902	0.077293	-0.050667

    :param holding_period: 持有周期(int)
    :param covariance_type:"shrink"/"simple" 协防差矩阵估算方式　Ledoit-Wolf压缩估计或简单估计
    :return: weight_df:使用Sample协方差矩阵估算方法得到的因子权重(pd.Dataframe),
             索引（index)为datetime,columns为待合成的因子名称。
    """
    weight_df = pd.DataFrame(index=ic_df.index, columns=ic_df.columns)
    lw = LedoitWolf()
    # 最大化第t天的ic,用到了截止到t+period的数据（算收益）,
    # 算得的权重用于t+period的因子进行加权
    for dt in ic_df.index:
        f_dt = pd.concat([factors_dict[factor_name].loc[dt] for factor_name in ic_df.columns], axis=1).dropna()
        if len(f_dt) == 0:
            continue
        if covariance_type == "shrink":
            try:
                f_cov_mat = lw.fit(f_dt.as_matrix()).covariance_
            except:
                f_cov_mat = np.mat(np.cov(f_dt.T.as_matrix()).astype(float))
        else:
            f_cov_mat = np.mat(np.cov(f_dt.T.as_matrix()).astype(float))
        inv_f_cov_mat = np.linalg.inv(f_cov_mat)
        weight = inv_f_cov_mat * np.mat(ic_df.loc[dt].values).reshape(len(inv_f_cov_mat), 1)
        weight = np.array(weight.reshape(len(weight), ))[0]
        weight_df.ix[dt] = weight / np.sum(np.abs(weight))

    return weight_df.shift(holding_period)


# 以IC为多因子组合权重
def ic_weight(ic_df,
              holding_period,
              rollback_period=120):
    """
    输入ic_df(ic值序列矩阵),指定持有期和滚动窗口，给出相应的多因子组合权重
    :param ic_df: ic值序列矩阵 （pd.Dataframe），索引（index）为datetime,columns为各因子名称。
             如：

            　　　　　　　　　　　BP	　　　CFP	　　　EP	　　ILLIQUIDITY	REVS20	　　　SRMI	　　　VOL20
            date
            2016-06-24	0.165260	0.002198	0.085632	-0.078074	0.173832	0.214377	0.068445
            2016-06-27	0.165537	0.003583	0.063299	-0.048674	0.180890	0.202724	0.081748
            2016-06-28	0.135215	0.010403	0.059038	-0.034879	0.111691	0.122554	0.042489
            2016-06-29	0.068774	0.019848	0.058476	-0.049971	0.042805	0.053339	0.079592
            2016-06-30	0.039431	0.012271	0.037432	-0.027272	0.010902	0.077293	-0.050667

    :param holding_period: 持有周期(int)
    :param rollback_period: 滚动窗口，即计算每一天的因子权重时，使用了之前rollback_period下的IC时间序列来计算。
    :return: weight_df:因子权重(pd.Dataframe),
             索引（index)为datetime,columns为待合成的因子名称。
    """
    # t-n ~ t天的ic,用到了截止到t+period的数据（算收益）,
    # 算得的权重用于t+period的因子进行加权
    n = rollback_period
    weight_df = pd.DataFrame(index=ic_df.index, columns=ic_df.columns)
    for dt in ic_df.index:
        ic_dt = ic_df[ic_df.index <= dt].tail(n)
        if len(ic_dt) < n:
            continue
        weight = ic_dt.mean(axis=0)
        weight = np.array(weight.reshape(len(weight), ))
        weight_df.ix[dt] = weight / np.sum(np.abs(weight))

    return weight_df.shift(holding_period)


# 以因子收益为多因子组合权重
def factors_ret_weight(factors_ret_df,
                       holding_period,
                       rollback_period=120):
    """
    输入factors_ret_df(因子收益序列矩阵),指定持有期和滚动窗口，给出相应的多因子组合权重
    :param factors_ret_df: 因子收益序列矩阵 （pd.Dataframe），索引（index）为datetime,columns为各因子名称。
             如：

            　　　　　　　　　　　BP	　　　CFP	　　　EP	　　ILLIQUIDITY	REVS20	　　　SRMI	　　　VOL20
            date
            2016-06-24	0.165260	0.002198	0.085632	-0.078074	0.173832	0.214377	0.068445
            2016-06-27	0.165537	0.003583	0.063299	-0.048674	0.180890	0.202724	0.081748
            2016-06-28	0.135215	0.010403	0.059038	-0.034879	0.111691	0.122554	0.042489
            2016-06-29	0.068774	0.019848	0.058476	-0.049971	0.042805	0.053339	0.079592
            2016-06-30	0.039431	0.012271	0.037432	-0.027272	0.010902	0.077293	-0.050667

    :param holding_period: 持有周期(int)
    :param rollback_period: 滚动窗口，即计算每一天的因子权重时，使用了之前rollback_period下的IC时间序列来计算。
    :return: weight_df:因子权重(pd.Dataframe),
             索引（index)为datetime,columns为待合成的因子名称。
    """
    # t-n ~ t天的因子收益,用到了截止到t+period的数据（算收益）,
    # 算得的权重用于t+period的因子进行加权
    n = rollback_period
    weight_df = pd.DataFrame(index=factors_ret_df.index, columns=factors_ret_df.columns)
    for dt in factors_ret_df.index:
        ret_dt = factors_ret_df[factors_ret_df.index <= dt].tail(n)
        if len(ret_dt) < n:
            continue
        weight = ret_dt.mean(axis=0)
        weight = np.array(weight.reshape(len(weight), ))
        weight_df.ix[dt] = weight / np.sum(np.abs(weight))

    return weight_df.shift(holding_period)


# 以IC_IR为多因子组合权重
def ir_weight(ic_df,
              holding_period,
              rollback_period=120):
    """
    输入ic_df(ic值序列矩阵),指定持有期和滚动窗口，给出相应的多因子组合权重
    :param ic_df: ic值序列矩阵 （pd.Dataframe），索引（index）为datetime,columns为各因子名称。
             如：

            　　　　　　　　　　　BP	　　　CFP	　　　EP	　　ILLIQUIDITY	REVS20	　　　SRMI	　　　VOL20
            date
            2016-06-24	0.165260	0.002198	0.085632	-0.078074	0.173832	0.214377	0.068445
            2016-06-27	0.165537	0.003583	0.063299	-0.048674	0.180890	0.202724	0.081748
            2016-06-28	0.135215	0.010403	0.059038	-0.034879	0.111691	0.122554	0.042489
            2016-06-29	0.068774	0.019848	0.058476	-0.049971	0.042805	0.053339	0.079592
            2016-06-30	0.039431	0.012271	0.037432	-0.027272	0.010902	0.077293	-0.050667

    :param holding_period: 持有周期(int)
    :param rollback_period: 滚动窗口，即计算每一天的因子权重时，使用了之前rollback_period下的IC时间序列来计算。
    :return: weight_df:因子权重(pd.Dataframe),
             索引（index)为datetime,columns为待合成的因子名称。
    """
    # t-n ~ t天的ic_ir,用到了截止到t+period的数据（算收益）,
    # 算得的权重用于t+period的因子进行加权
    n = rollback_period
    weight_df = pd.DataFrame(index=ic_df.index, columns=ic_df.columns)
    for dt in ic_df.index:
        ic_dt = ic_df[ic_df.index <= dt].tail(n)
        if len(ic_dt) < n:
            continue
        weight = ic_dt.mean(axis=0) / ic_dt.std(axis=0)
        weight = np.array(weight.reshape(len(weight), ))
        weight_df.ix[dt] = weight / np.sum(np.abs(weight))

    return weight_df.shift(holding_period)


def combine_factors(factors_dict=None,
                    standardize_type="rank",
                    winsorization=False,
                    index_member=None,
                    weighted_method="equal_weight",
                    props=None):
    """
    # 因子组合
    :param index_member:　是否是指数成分 pd.DataFrame
    :param winsorization: 是否去极值
    :param props:　当weighted_method不为equal_weight时　需传入此配置　配置内容包括
     props = {
            'price': None,
            'daily_ret':None,
            'high': None,
            'low': None,
            'ret_type': 'return',
            'benchmark_price': None,
            'daily_benchmark_ret':None,
            'period': 5,
            'mask': None,
            'can_enter': None,
            'can_exit': None,
            'forward': True,
            'commission': 0.0008,
            "covariance_type": "simple",  # 还可以为"shrink"
            "rollback_period": 120
        }
    :param factors_dict: 若干因子组成的字典(dict),形式为:
                         {"factor_name_1":factor_1,"factor_name_2":factor_2}
                       　每个因子值格式为一个pd.DataFrame，索引(index)为date,column为asset
    :param standardize_type: 标准化方法，有"rank"（排序标准化）,"z_score"(z-score标准化),为空则不进行标准化操作
    :param weighted_method 组合方法，有equal_weight,ic_weight, ir_weight, max_IR.若不为equal_weight，则还需配置props参数．
    :return: new_factor 合成后所得的新因子。
    """

    def generate_props():
        props = {
            'price': None,
            'daily_ret': None,
            'high': None,
            'low': None,
            'ret_type': 'return',
            'benchmark_price': None,
            'daily_benchmark_ret':None,
            'period': 5,
            'mask': None,
            'can_enter': None,
            'can_exit': None,
            'forward': True,
            'commission': 0.0008,
            "covariance_type": "simple",  # 还可以为"shrink"
            "rollback_period": 120
        }
        return props

    def standarize_factors(factors):
        if isinstance(factors, pd.DataFrame):
            factors_dict = {"factor": factors}
        else:
            factors_dict = factors
        factor_name_list = factors_dict.keys()
        for factor_name in factor_name_list:
            factors_dict[factor_name] = jutil.fillinf(factors_dict[factor_name])
            factors_dict[factor_name] = process._mask_non_index_member(factors_dict[factor_name],
                                                                       index_member=index_member)
            if winsorization:
                factors_dict[factor_name] = process.winsorize(factors_dict[factor_name])
            if standardize_type == "z_score":
                factors_dict[factor_name] = process.standardize(factors_dict[factor_name])
            elif standardize_type == "rank":
                factors_dict[factor_name] = process.rank_standardize(factors_dict[factor_name])
            elif standardize_type is not None:
                raise ValueError("standardize_type 只能为'z_score'/'rank'/None")
        return factors_dict

    def _cal_weight(weighted_method="ic_weight"):
        _props = generate_props()
        if not (props is None):
            _props.update(props)
        if _props["price"] is None and _props["daily_ret"] is None:
            raise ValueError("您需要在配置props中提供price或者daily_ret")

        if weighted_method == "factors_ret_weight":
            factors_ret = get_factors_ret_df(factors_dict=factors_dict,
                                             **_props)
            return factors_ret_weight(factors_ret,
                                      _props['period'],
                                      _props["rollback_period"])
        else:
            # 此处计算的ic,用到的因子值是shift(1)后的
            # t日ic计算逻辑:t-1的因子数据，t日决策买入，t+n天后卖出对应的ic
            ic_df = get_factors_ic_df(factors_dict=factors_dict,
                                      **_props)
            if weighted_method == 'max_IR':
                return max_IR_weight(ic_df,
                                     _props['period'],
                                     _props["rollback_period"],
                                     _props["covariance_type"])
            elif weighted_method == "ic_weight":
                return ic_weight(ic_df,
                                 _props['period'],
                                 _props["rollback_period"])
            elif weighted_method == "ir_weight":
                return ir_weight(ic_df,
                                 _props['period'],
                                 _props["rollback_period"])
            elif weighted_method == "max_IC":
                # 计算t期因子ic用的是t-1期因子，所以要把因子数据shift(1)
                shift_factors = {
                    factor_name: factors_dict[factor_name].shift(1) for factor_name in factors_dict.keys()
                }
                return max_IC_weight(ic_df,
                                     shift_factors,
                                     _props['period'],
                                     _props["covariance_type"])

    def sum_weighted_factors(x, y):
        return x + y

    if not factors_dict or len(list(factors_dict.keys())) < 2:
        raise ValueError("你需要给定至少2个因子")
    factors_dict = standarize_factors(factors_dict)

    if weighted_method in ["max_IR", "max_IC", "ic_weight", "ir_weight", "factors_ret_weight"]:
        weight = _cal_weight(weighted_method)
        weighted_factors = {}
        factor_name_list = factors_dict.keys()
        for factor_name in factor_name_list:
            w = pd.DataFrame(data=weight[factor_name], index=factors_dict[factor_name].index)
            w = pd.concat([w] * len(factors_dict[factor_name].columns), axis=1)
            w.columns = factors_dict[factor_name].columns
            weighted_factors[factor_name] = factors_dict[factor_name] * w
    elif weighted_method == "equal_weight":
        weighted_factors = factors_dict
    else:
        raise ValueError('weighted_method 只能为equal_weight, ic_weight, ir_weight, max_IR, max_IC, factors_ret_weight')
    new_factor = reduce(sum_weighted_factors, weighted_factors.values())
    new_factor = standarize_factors(new_factor)["factor"]
    return new_factor
