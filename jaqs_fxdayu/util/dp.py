import pandas as pd
from collections import defaultdict


English_classify = {'480000': 'Bank',
                    '430000': 'Real_Estate',
                    '460000': 'Leisure_Service',
                    '640000': 'Mechanical_Equipment',
                    '240000': 'Nonferrous_Metals',
                    '510000': 'Synthesis',
                    '410000': 'Public_Utility',
                    '450000': 'Commercial_Trade',
                    '730000': 'Communication',
                    '330000': 'Household_Appliances',
                    '720000': 'Media',
                    '630000': 'Electrical_Equipment',
                    '270000': 'Electronic_Engineering',
                    '490000': 'Non_Bank_Finance',
                    '370000': 'Medical_Biology',
                    '710000': 'Computer',
                    '280000': 'Car',
                    '340000': 'Food_Beverage',
                    '220000': 'Chemical_Engineering',
                    '210000': 'Digging',
                    '230000': 'Steel',
                    '650000': 'Military',
                    '110000': 'Agriculture_Fishing',
                    '420000': 'Transportation',
                    '620000': 'Architectural_Ornament',
                    '350000': 'Textile_Garment',
                    '610000': 'Building_Materials',
                    '360000': 'Light_Manufacturing'}


# 交易日列表(return pandas.Index)
def trade_days(api, start, end):
    """

    :param api: jaqs.data.DataApi
    :param start: int, sample: 20170101
    :param end: int, sample: 20180101
    :return:
    """
    data, msg = api.query("jz.secTradeCal", "start_date={}&end_date={}".format(start, end))
    if msg == "0,":
        return data.set_index("trade_date").rename_axis(int).index
    else:
        raise Exception(msg)


def st_status(api, symbol, start, end):
    """
    :param api: jaqs.data.DataApi
    :param symbol: str, sample: 600000.SH,000001.SZ
    :param start: int, sample: 20170101
    :param end: int, sample: 20180101
    :return:
    """
    dates = trade_days(api, start, end)
    data, msg = api.query("lb.sState", "symbol={}".format(symbol))
    if len(data) == 0:
        return None
    data["in_date"] = data["effDate"].apply(int)
    data["out_date"] = 99999999
    data = data.sort_values(by=["in_date"])
    if msg != "0,":
        raise Exception(msg)

    return expand(data, dates, None, value="state").fillna(0)


# 指数成分股(return pandas.DataFrame)
def index_cons(api, index_code, start, end):
    """

    :param api: jaqs.data.DataApi
    :param index_code: str, sample: 000300.SH
    :param start: int, sample: 20170101
    :param end: int, sample: 20180101
    :return:
    """
    data, msg = api.query("lb.indexCons", "index_code={}&start_date={}&end_date={}".format(index_code, start, end))
    if msg == "0,":
        data["in_date"] = data["in_date"].apply(int)
        data["out_date"] = data["out_date"].replace("", "99999999").apply(int)
        return data
    else:
        raise Exception(msg)


# range扩展为daily
def expand(data, index, default=False, prefix=True, key="symbol", start="in_date", end="out_date", value=None):
    """

    :param data: pd.DataFrame
    :param index: pd.Index, 作为输出表的index
    :param default: 新表的默认值
    :param prefix: 将符合范围判断条件的数据设为该值
    :param key: 指定data中用来作为输出表的columns的列
    :param start: 指定用来作为开始取值范围的列
    :param end: 指定用来作为结束取值范围的列
    :param value: 以data中的特定列作为预设值
    :return:

    Examples
    --------
    > dates
    Int64Index([20170626, 20170627, 20170628, 20170629, 20170630, 20170703, 20170704, 20170705],
               dtype='int64', name='trade_date')

    > industry
        in_date  out_date     symbol industry1_name industry1_code
    0  20140101  99999999  000001.SZ             银行         480000
    1  20140101  20151001  000006.SZ            房地产         430000
    2  20151001  20170629  000006.SZ             采掘         210000
    3  20170629  99999999  000006.SZ            房地产         430000
    4  20140101  99999999  000651.SZ           家用电器         330000

    > expand(industry, dates, None, value="industry1_name")
                   000001.SZ 000006.SZ 000651.SZ
    trade_date
    20170626          银行        采掘      家用电器
    20170627          银行        采掘      家用电器
    20170628          银行        采掘      家用电器
    20170629          银行       房地产      家用电器
    20170630          银行       房地产      家用电器
    20170703          银行       房地产      家用电器
    20170704          银行       房地产      家用电器
    20170705          银行       房地产      家用电器

    """
    if isinstance(data, pd.DataFrame) and isinstance(index, pd.Index):
        dct = defaultdict(lambda: pd.Series(default, index))
        for name, row in data.iterrows():
            s = dct[row[key]]
            s.loc[row[start]:row[end]] = prefix if value is None else row[value]
        return pd.DataFrame(dct)


# 日线级指数表
def daily_index_cons(api, index_code, start, end):
    """

    :param api: jaqs.data.DataApi
    :param index_code: str, sample: 000300.SH
    :param start: int, sample: 20170101
    :param end: int, sample: 20180101
    :return:
    """
    dates = trade_days(api, start, end)
    codes = index_cons(api, index_code, start, end)
    return expand(codes, dates)


# 日线级行业分类表
def daily_sec_industry(api, symbol, start, end, source="sw", value="industry1_code"):
    """

    :param api: jaqs.data.DataApi
    :param symbol: str, sample: 600000.SH,000001.SZ
    :param start: int, sample: 20170101
    :param end: int, sample: 20180101
    :param source: str, sample: sw
    :param value: str, sample: industry1_code
    :return:
    """
    dates = trade_days(api, start, end)
    data, msg = api.query("lb.secIndustry", "symbol={}&industry_src={}".format(symbol, source))
    data["in_date"] = data["in_date"].apply(int)
    data["out_date"] = data["out_date"].replace("", "99999999").apply(int)
    if msg != "0,":
        raise Exception(msg)

    return expand(data, dates, None, value=value)
