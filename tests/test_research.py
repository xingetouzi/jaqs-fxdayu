# encoding: utf-8
from __future__ import unicode_literals

from jaqs_fxdayu import patch_all

patch_all()

import numpy as np
import os
from pathlib import Path
from jaqs.data import DataView
from jaqs.data import RemoteDataService
from jaqs.research import SignalDigger
from jaqs.research.signaldigger import performance as pfm
from jaqs.research.signaldigger import plotting
from jaqs_fxdayu.research.signaldigger.analysis import analysis
from tests.data_config import data_config

output_root = Path(__file__).absolute().parent

dataview_folder = str(output_root / ".persist" / "test_signal")
if not (os.path.isdir(dataview_folder)):
    os.makedirs(dataview_folder)


# --------------------------------------------------------------------------------
# 定义信号过滤条件-非指数成分
def mask_index_member(dv):
    df_index_member = dv.get_ts('index_member')
    mask_index_member = df_index_member == 0
    return mask_index_member


# 定义可买卖条件——未停牌、未涨跌停
def limit_up_down(dv):
    trade_status = dv.get_ts('trade_status')
    mask_sus = trade_status != 1 # 不可交易
    # 涨停
    dv.add_formula('up_limit', '(close - Delay(close, 1)) / Delay(close, 1) > 0.095', is_quarterly=False,
                   add_data=True)
    # 跌停
    dv.add_formula('down_limit', '(close - Delay(close, 1)) / Delay(close, 1) < -0.095', is_quarterly=False,
                   add_data=True)
    can_enter = np.logical_and(dv.get_ts('up_limit') < 1, ~mask_sus)  # 未涨停未停牌
    can_exit = np.logical_and(dv.get_ts('down_limit') < 1, ~mask_sus)  # 未跌停未停牌
    return can_enter, can_exit


def test_save_dataview():
    ds = RemoteDataService()
    ds.init_from_config(data_config)
    dv = DataView()
    print(DataView)
    props = {'start_date': 20170501, 'end_date': 20171001, 'universe': '000016.SH',
             'fields': 'volume,pb,pe,ps,float_mv,sw1',
             'freq': 1}

    dv.init_from_config(props, ds)
    dv.prepare_data()

    dv.save_dataview(dataview_folder)


def test_analyze_signal():
    # --------------------------------------------------------------------------------
    # Step.1 load dataview
    dv = DataView()
    dv.load_dataview(dataview_folder)

    mask = mask_index_member(dv)
    can_enter, can_exit = limit_up_down(dv)

    # --------------------------------------------------------------------------------
    # Step.3 get signal, benchmark and price data
    dv.add_formula('divert', '- Correlation(vwap_adj, volume, 10)', is_quarterly=False, add_data=True)

    signal = dv.get_ts('divert')
    price = dv.get_ts('close_adj')
    price_bench = dv.data_benchmark

    # Step.4 analyze!
    my_period = 5
    obj = SignalDigger(output_folder='../output/test_signal', output_format='pdf')
    obj.process_signal_before_analysis(signal=signal,
                                       price=price,
                                       high=dv.get_ts("high_adj"),  # 可为空
                                       low=dv.get_ts("low_adj"),  # 可为空
                                       group=dv.get_ts("sw1"),
                                       n_quantiles=5,  # quantile分类数
                                       mask=mask,  # 过滤条件
                                       can_enter=can_enter,  # 是否能进场
                                       can_exit=can_exit,  # 是否能出场
                                       period=my_period,  # 持有期
                                       benchmark_price=price_bench,  # 基准价格 可不传入，持有期收益（return）计算为绝对收益
                                       commission=0.0008,
                                       )
    signal_data = obj.signal_data
    result = analysis(signal_data, is_event=False, period=my_period)
    ic = pfm.calc_signal_ic(signal_data, by_group=True)
    mean_ic_by_group = pfm.mean_information_coefficient(ic, by_group=True)
    plotting.plot_ic_by_group(mean_ic_by_group)
    res = obj.create_full_report()


def test_DIY_signal():
    # --------------------------------------------------------------------------------
    # Step.1 load dataview
    dv = DataView()
    dv.load_dataview(dataview_folder)
    # 方法1：add_formula 基于dataview里已有的字段,通过表达式定义因子
    dv.add_formula("momentum", "Return(close_adj, 20)", is_quarterly=False, add_data=True)
    # 方法2: append_df 构造一个因子表格（pandas.Dataframe）,直接添加到dataview当中
    import pandas as pd
    import talib as ta

    close = dv.get_ts("close_adj").dropna(how='all', axis=1)
    slope_df = pd.DataFrame(
        {sec_symbol: -ta.LINEARREG_SLOPE(value.values, 10) for sec_symbol, value in close.iteritems()},
        index=close.index)
    dv.append_df(slope_df, 'slope')
    dv.get_ts("slope")

    # 定义事件
    from jaqs_fxdayu.research.signaldigger import process

    Open = dv.get_ts("open_adj")
    High = dv.get_ts("high_adj")
    Low = dv.get_ts("low_adj")
    Close = dv.get_ts("close_adj")
    trade_status = dv.get_ts('trade_status')
    mask_sus = trade_status!=1
    # 剔除掉停牌期的数据　再计算指标
    open_masked = process._mask_df(Open, mask=mask_sus)
    high_masked = process._mask_df(High, mask=mask_sus)
    low_masked = process._mask_df(Low, mask=mask_sus)
    close_masked = process._mask_df(Close, mask=mask_sus)
    from jaqs_fxdayu.data import signal_function_mod as sfm
    MA5 = sfm.ta(ta_method='MA',
                 ta_column=0,
                 Open=open_masked,
                 High=high_masked,
                 Low=low_masked,
                 Close=close_masked,
                 Volume=None,
                 timeperiod=10)
    MA10 = sfm.ta('MA', Close=close_masked, timeperiod=10)
    dv.append_df(MA5, 'MA5')
    dv.append_df(MA10, 'MA10')
    dv.add_formula("Cross", "(MA5>=MA10)&&(Delay(MA5<MA10, 1))", is_quarterly=False, add_data=True)


def test_multi_factor():
    from jaqs_fxdayu.research.signaldigger import multi_factor, process
    dv = DataView()
    dv.load_dataview(dataview_folder)
    dv.add_formula("momentum", "Return(close_adj, 20)", is_quarterly=False, add_data=True)

    mask = mask_index_member(dv)
    can_enter, can_exit = limit_up_down(dv)

    ic = dict()
    factors_dict = {signal: dv.get_ts(signal) for signal in ["pb", "pe", "ps", "momentum"]}
    for period in [5, 15]:
        ic[period] = multi_factor.get_factors_ic_df(factors_dict,
                                                    price=dv.get_ts("close_adj"),
                                                    high=dv.get_ts("high_adj"),  # 可为空
                                                    low=dv.get_ts("low_adj"),  # 可为空
                                                    n_quantiles=5,  # quantile分类数
                                                    mask=mask,  # 过滤条件
                                                    can_enter=can_enter,  # 是否能进场
                                                    can_exit=can_exit,  # 是否能出场
                                                    period=period,  # 持有期
                                                    benchmark_price=dv.data_benchmark,  # 基准价格 可不传入，持有期收益（return）计算为绝对收益
                                                    commission=0.0008,
                                                    )
    factor_dict = dict()
    index_member = dv.get_ts("index_member")
    for name in ["pb", "pe", "ps", "momentum"]:
        signal = -1 * dv.get_ts(name)  # 调整符号
        process.winsorize(factor_df=signal, alpha=0.05, index_member=index_member)  # 去极值
        signal = process.rank_standardize(signal, index_member)  # 因子在截面排序并归一化到0-1(只保留排序信息)
        signal = process.standardize(signal, index_member)  # z-score标准化 保留排序信息和分布信息
        # 行业市值中性化
        signal = process.neutralize(signal,
                                    group=dv.get_ts("sw1"),
                                    float_mv=dv.get_ts("float_mv"),
                                    index_member=index_member,  # 是否只处理时只考虑指数成份股
                                    )
        factor_dict[name] = signal

    # 因子间存在较强同质性时，使用施密特正交化方法对因子做正交化处理，用得到的正交化残差作为因子
    new_factors = multi_factor.orthogonalize(factors_dict=factor_dict,
                                             standardize_type="rank",
                                             # 输入因子标准化方法，有"rank"（排序标准化）,"z_score"(z-score标准化)两种（"rank"/"z_score"）
                                             winsorization=False,  # 是否对输入因子去极值
                                             index_member=index_member)  # 是否只处理指数成分股

    #  多因子组合-动态加权参数配置
    props = {
        'price': dv.get_ts("close_adj"),
        'high': dv.get_ts("high_adj"),  # 可为空
        'low': dv.get_ts("low_adj"),  # 可为空
        'ret_type': 'return',  # 可选参数还有upside_ret/downside_ret 则组合因子将以优化潜在上行、下行空间为目标
        'benchmark_price': dv.data_benchmark,  # 为空计算的是绝对收益　不为空计算相对收益
        'period': 30,  # 30天的持有期
        'mask': mask,
        'can_enter': can_enter,
        'can_exit': can_exit,
        'forward': True,
        'commission': 0.0008,
        "covariance_type": "shrink",  # 协方差矩阵估算方法 还可以为"simple"
        "rollback_period": 120}  # 滚动窗口天数

    comb_factors = dict()
    for method in ["equal_weight", "ic_weight", "ir_weight", "max_IR", "max_IC", "factors_ret_weight"]:
        comb_factors[method] = multi_factor.combine_factors(factor_dict,
                                                            standardize_type="rank",
                                                            winsorization=False,
                                                            weighted_method=method,
                                                            props=props)


def test_optimizer():
    from jaqs_fxdayu.research import Optimizer

    dv = DataView()
    dv.load_dataview(dataview_folder)

    mask = mask_index_member(dv)
    can_enter, can_exit = limit_up_down(dv)

    price = dv.get_ts('close_adj')
    high = dv.get_ts('high_adj')
    low = dv.get_ts('low_adj')
    price_bench = dv.data_benchmark
    optimizer = Optimizer(dataview=dv,
                          formula='- Correlation(vwap_adj, volume, LEN)',
                          params={"LEN": range(2, 4, 1)},
                          name='divert',
                          price=price,
                          high=high,
                          low=low,
                          benchmark_price=price_bench,  # =None求绝对收益 #=price_bench求相对收益
                          period=30,
                          n_quantiles=5,
                          mask=mask,
                          can_enter=can_enter,
                          can_exit=can_exit,
                          commission=0.0008,  # 手续费 默认0.0008
                          is_event=False,  # 是否是事件(0/1因子)
                          is_quarterly=False)  # 是否是季度因子 默认为False

    ret_best = optimizer.enumerate_optimizer(target_type="top_quantile_ret",  # 优化目标类型
                                             target="Ann. IR",  # 优化目标
                                             in_sample_range=[20140101, 20160101],  # 样本内范围 默认为None,在全样本上优化
                                             ascending=False)  # 是否按优化目标升序排列(从小到大)


if __name__ == "__main__":
    test_save_dataview()
    test_analyze_signal()
    test_DIY_signal()
    test_multi_factor()
    test_optimizer()
