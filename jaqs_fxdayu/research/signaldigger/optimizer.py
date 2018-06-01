# encoding=utf-8
# 参数优化器


from itertools import product
from .analysis import analysis
from .signal_creator import SignalCreator
import warnings
import pandas as pd

target_types = {
    'factor': {
        "ic": [
            "return_ic",
            "upside_ret_ic",
            "downside_ret_ic"
        ],
        "ret": [
            "long_ret",
            "short_ret",
            "long_short_ret",
            'top_quantile_ret',
            'bottom_quantile_ret',
            "tmb_ret",
            "all_sample_ret"],
        "space": [
            'long_space',
            'short_space',
            'long_short_space',
            "top_quantile_space",
            "bottom_quantile_space",
            "tmb_space",
            "all_sample_space"
        ]
    },
    "event": {
        "ret": [
            "long_ret",
            "short_ret",
            "long_short_ret",
        ],
        "space": [
            'long_space',
            'short_space',
            'long_short_space',
        ]
    }
}

targets = {
    "ic": ["IC Mean", "IC Std.", "t-stat(IC)", "p-value(IC)", "IC Skew", "IC Kurtosis", "Ann. IR"],
    "ret": ['t-stat', "p-value", "skewness", "kurtosis", "Ann. Ret", "Ann. Vol", "Ann. IR", "occurance"],
    "space": [
        'Up_sp Mean',
        'Up_sp Std',
        'Up_sp IR',
        'Up_sp Pct5',
        'Up_sp Pct25 ',
        'Up_sp Pct50 ',
        'Up_sp Pct75',
        'Up_sp Pct95',
        'Up_sp Occur',
        'Down_sp Mean',
        'Down_sp Std',
        'Down_sp IR',
        'Down_sp Pct5',
        'Down_sp Pct25 ',
        'Down_sp Pct50 ',
        'Down_sp Pct75',
        'Down_sp Pct95',
        'Down_sp Occur',
    ]
}


class Optimizer(object):
    '''
    :param dataview: 包含了计算公式所需要的所有数据的jaqs.data.DataView对象
    :param formula: str(N) 需要优化的公式：如'(open - Delay(close, l1)) / Delay(close, l2)'
    :param params: dict(N) 需要优化的参数范围：如{"LEN1"：range(1,10,1),"LEN2":range(1,10,1)}
    :param name: str (N) 信号的名称
    :param price: dataFrame (N) 价格与daily_ret不能同时存在
    :param daily_ret: dataFrame (N) 每日收益
    :param high: dataFrame (N) 最高价　用于计算上行收益空间
    :param low: dataFrame (N) 最低价　用于计算下行收益空间
    :param benchmark_price: dataFrame (N) 基准价格　若不为空收益计算模式为相对benchmark的收益　与daily_benchmark_ret不能同时存在
    :param daily_benchmark_ret: dataFrame (N) 基准日收益　若不为空收益计算模式为相对benchmark的收益
    :param period: int (5) 选股持有期
    :param n_quantiles: int (5)
    :param mask: 过滤条件 dataFrame (N)
    :param can_enter: dataFrame (N) 是否能进场
    :param can_exit: dataFrame (N) 是否能出场
    :param forward: bool(True) 是否forward return
    :param commission:　float(0.0008) 手续费率
    :param is_event: bool(False) 是否是事件(0/1因子)
    :param is_quarterly: bool(False) 是否是季度因子
    '''

    def __init__(self,
                 dataview=None,
                 formula=None,
                 params=None,
                 name=None,
                 price=None,
                 daily_ret=None,
                 high=None,
                 low=None,
                 benchmark_price=None,
                 daily_benchmark_ret=None,
                 period=5,
                 n_quantiles=5,
                 mask=None,
                 can_enter=None,
                 can_exit=None,
                 forward=True,
                 commission=0.0008,
                 is_event=False,
                 is_quarterly=False,
                 register_funcs=None,
                 ):
        self.dataview = dataview
        self.formula = formula
        self.params = params
        if self.formula is not None:
            self._judge_params()
        self.name = name if name else formula
        if price is None and daily_ret is None:
            try:
                price = dataview.get_ts('close_adj')
            except:
                raise ValueError("One of price / ret must be provided.")
        self.period = period
        if is_event:
            n_quantiles = 1
        self.is_event = is_event
        self.is_quarterly = is_quarterly
        self.register_funcs = register_funcs
        self.signal_creator = SignalCreator(
            price=price, daily_ret=daily_ret,
            benchmark_price=benchmark_price, daily_benchmark_ret=daily_benchmark_ret,
            high=high, low=low,
            period=period, n_quantiles=n_quantiles,
            mask=mask,
            can_enter=can_enter,
            can_exit=can_exit,
            forward=forward,
            commission=commission
        )
        self.all_signals = None
        self.all_signals_perf = None
        self.in_sample_range = None

    # 判断参数命名的规范性
    def _judge_params(self):
        if self.params is None:
            raise ValueError("未给优化器提供优化空间(需要参数params)")
        if not isinstance(self.params, dict):
            raise ValueError("优化空间参数不符合格式要求:如{'LEN1'：range(1,10,1),'LEN2':range(1,10,1)}")
        for para in self.params.keys():
            if len(para) < 2 or not para.isupper():
                raise ValueError("formula的参数%s的命名不符合要求!参数名称需全部由大写英文字母组成,且字母数不少于2"%(para,))

    # 判断target合法性
    def _judge_target(self, target_type, target):
        legal = True
        # 判断所提供的输入数据是否支持空间分析
        if self.signal_creator.high is None or self.signal_creator.low is None:
            if (target_type in target_types["factor"]["space"]) or \
                    (target_types in ["upside_ret_ic", "downside_ret_ic"]) or \
                    (target in targets["space"]):
                legal = False
                print("需要在Optimizer中传入[high]&[low],以支持收益空间分析和优化")
        # 判断是否target/target_type参数在可选的选项内
        if self.is_event:
            if target_type in target_types["event"]["ret"]:
                if not (target in targets["ret"]):
                    legal = False
                    print("可选的优化目标仅能从%s选取" % (str(targets["ret"])))
            elif target_type in target_types["event"]["space"]:
                if not (target in targets["space"]):
                    legal = False
                    print("可选的优化目标仅能从%s选取" % (str(targets["space"])))
            else:
                legal = False
                print("可选的优化类型仅能从%s选取" % (str(target_types["event"]["ret"] + target_types["event"]["space"])))
        else:
            if target_type in target_types["factor"]["ret"]:
                if not (target in targets["ret"]):
                    legal = False
                    print("可选的优化目标仅能从%s选取" % (str(targets["ret"])))
            elif target_type in target_types["factor"]["ic"]:
                if not (target in targets["ic"]):
                    legal = False
                    print("可选的优化目标仅能从%s选取" % (str(targets["ic"])))
            elif target_type in target_types["factor"]["space"]:
                if not (target in targets["space"]):
                    legal = False
                    print("可选的优化目标仅能从%s选取" % (str(targets["space"])))
            else:
                print("可选的优化类型仅能从%s选取" % (
                    str(target_types["factor"]["ret"] + target_types["factor"]["ic"] + target_types["factor"][
                        "space"])))
        return legal

    def enumerate_optimizer(self,
                            target_type="long_ret",
                            target="Ann. IR",
                            ascending=False,
                            in_sample_range=None):
        '''
        :param target_type: 目标种类
        :param target: 优化目标
        :param ascending: bool(False)升序or降序排列
        :param in_sample_range: [date_start(int),date_end(int)] (N) 定义样本内优化范围.
        :return:
        '''

        if self._judge_target(target_type, target):  # 判断target合法性
            self.get_all_signals_perf(in_sample_range)
            if len(self.all_signals_perf) == 0:
                return []
            if target_type in (target_types["factor"]["ic"]):
                order_index = "ic"
            elif target_type in (target_types["factor"]["ret"]):
                order_index = "ret"
            else:
                order_index = "space"
            ordered_perf = self.all_signals_perf.values()
            return sorted(ordered_perf,
                          key=lambda x: x[order_index].loc[target, target_type],
                          reverse=(ascending == False))
        return []

    def get_all_signals(self):
        if self.all_signals is None:
            self.all_signals = dict()
            keys = list(self.params.keys())
            for value in product(*self.params.values()):
                para_dict = dict(zip(keys, value))
                formula = self.formula
                for vars in para_dict.keys():
                    formula = formula.replace(vars, str(para_dict[vars]))
                signal = self.dataview.add_formula(field_name=self.name,
                                                   formula=formula,
                                                   is_quarterly=self.is_quarterly,
                                                   register_funcs=self.register_funcs)
                if (not isinstance(signal,pd.DataFrame)) or (signal.size==0):
                    warnings.warn("待优化公式%s不能计算出有效结果,请检查数据和公式是否正确完备!")
                    continue
                self.all_signals[self.name + str(para_dict)] = self.cal_signal(signal)

    def get_all_signals_perf(self, in_sample_range=None):
        self.get_all_signals()
        if self.all_signals_perf is None or \
                (self.in_sample_range != in_sample_range) or \
                (len(set(self.all_signals_perf.keys()) - set(self.all_signals.keys())) != 0):
            self.all_signals_perf = dict()
            for sig_name in self.all_signals.keys():
                perf = self.cal_perf(self.all_signals[sig_name], in_sample_range)
                if perf is not None:
                    self.all_signals_perf[sig_name] = perf
                    self.all_signals_perf[sig_name]["signal_name"] = sig_name
            if len(self.all_signals_perf) == 0:
                print("没有计算出可用的信号绩效，请确保至少有一个信号可用.(可尝试增加样本内数据的时间范围以确保有信号发生)")
            self.in_sample_range = in_sample_range

    def cal_signal(self, signal):
        return self.signal_creator.get_signal_data(signal)

    # TODO 输入绩效要求，过滤掉不符合要求的结果
    def cal_perf(self,
                 signal_data,
                 in_sample_range=None,
                 constraints=None):
        '''
        :param signal_data:
        :param in_sample_range: like [20100312,20170405] 样本内范围起止时间
        :param constraints: like [{"target_type":"long_ret",
                                   "target":"Ann. IR",
                                   "condition":}]
        :return:
        '''
        perf = None
        if signal_data is not None:
            if in_sample_range is not None:
                signal_data = signal_data.loc[in_sample_range[0]:in_sample_range[1]]
            if len(signal_data) > 0:
                perf = analysis(signal_data, self.is_event, self.period)
        return perf
