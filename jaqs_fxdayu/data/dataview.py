import os
from copy import copy
import numpy as np
import pandas as pd
from jaqs import util as jutil
from jaqs.data.align import align
from jaqs.data.dataview import DataView as OriginDataView, EventDataView
from jaqs.data.dataservice import RemoteDataService
from jaqs.data.dataapi import DataApi
from jaqs.data.py_expression_eval import Parser

from jaqs_fxdayu.data.search_doc import FuncDoc
from jaqs_fxdayu.patch_util import auto_register_patch
from jaqs_fxdayu.data.dataservice import LocalDataService

try:
    basestring
except NameError:
    basestring = str


PF = "prepare_fields"


def get_api(data_api):
    if isinstance(data_api, RemoteDataService):
        return data_api.data_api
    elif isinstance(data_api, DataApi):
        return data_api
    elif isinstance(data_api, LocalDataService):
        return data_api  
    else:
        raise TypeError("Type of data_api should be jaqs.data.RemoteDataService or jaqs.data.DataApi or ")


# def quick_concat(dfs, level, index_name="trade_date"):
#     joined_index = pd.Index(np.concatenate([df.index.values for df in dfs]), name=index_name).sort_values().drop_duplicates()
#     joined_columns = pd.MultiIndex.from_tuples(np.concatenate([df.columns.values for df in dfs]), names=level)
#     result = [pd.DataFrame(df, joined_index).values for df in dfs]
#     return pd.DataFrame(np.concatenate(result, axis=1), joined_index, joined_columns)
from jaqs_fxdayu.util.concat import quick_concat


@auto_register_patch(parent_level=1)
class DataView(OriginDataView):
    def __init__(self):
        super(DataView, self).__init__()
        self.factor_fields = set()

    def init_from_config(self, props, data_api):
        self.adjust_mode = props.get("adjust_mode", "post")
        _props = props.copy()
        if _props.pop(PF, False):
            self.prepare_fields(data_api)
        super(DataView, self).init_from_config(_props, data_api)

    def prepare_fields(self, data_api):
        api = get_api(data_api)

        table, msg = api.query("help.apiParam", "api=factor&ptype=OUT", "param")
        if msg == "0,":
            self.factor_fields = set(table["param"])
            self.custom_daily_fields.extend(self.factor_fields)

    def get_factor(self, symbol, start, end, fields, limit=500000):
        if isinstance(symbol, list):
            symbol = ",".join(symbol)
        if isinstance(fields, list):
            fields = ",".join(fields)

        data ,msg = self.distributed_query("query",
                                           symbol,
                                           start_date=start,
                                           end_date=end, limit=limit,
                                           fields = fields,
                                           view = "factor")
        if msg == "0,":
            data["symbol"] = data["symbol"].apply(lambda s: s[:6]+".SH" if s.startswith("6") else s[:6]+".SZ")
            data.rename_axis({"datetime": "trade_date"}, 1, inplace=True)
            return data
        else:
            raise Exception(msg)

    def distributed_query(self, query_func_name, symbol, start_date, end_date, limit=100000, **kwargs):

        def query(api, query_func_name, symbol, start_date, end_date, **kwargs):
            if query_func_name == "query":
                df, msg = api.query(
                    filter = "symbol={}&start={}&end={}".format(symbol, start_date, end_date),
                    **kwargs
                )
            else:
                df, msg = getattr(self.data_api, query_func_name)(symbol=symbol,
                                                                  start_date=start_date, end_date=end_date,
                                                                  **kwargs)
            return df, msg

        sep = ','
        symbol = symbol.split(sep)
        n_symbols = len(symbol)
        dates = self.data_api.query_trade_dates(start_date, end_date)
        n_days = len(dates)

        print("当前请求%s..." % (query_func_name,))
        print(kwargs)
        if n_symbols * n_days > limit:
            n = limit // n_days # 每次取n只股票

            df_list = []
            i = 0
            pos1, pos2 = n * i, n * (i + 1)
            while pos2 <= n_symbols:
                df, msg = query(self.data_api, query_func_name,
                                symbol=sep.join(symbol[pos1:pos2]),
                                start_date=dates[0], end_date=dates[-1],
                                **kwargs
                                )
                df_list.append(df)
                print("下载进度%s/%s." % (pos2, n_symbols))
                i += 1
                pos1, pos2 = n * i, n * (i + 1)
            if pos1 < n_symbols:
                df, msg = query(self.data_api, query_func_name,
                                symbol=sep.join(symbol[pos1:]),
                                start_date=dates[0], end_date=dates[-1],
                                **kwargs)
                df_list.append(df)
            df = pd.concat(df_list, axis=0)
        else:
            df, msg = query(self.data_api, query_func_name,
                            symbol=sep.join(symbol),
                            start_date=start_date, end_date=end_date,
                            **kwargs)
        return df, msg

    def _get_fields(self, field_type, fields, complement=False, append=False):
        """
        Get list of fields that are in ref_quarterly_fields.
        Parameters
        ----------
        field_type : {'market_daily', 'ref_daily', 'income', 'balance_sheet', 'cash_flow', 'daily', 'quarterly'
        fields : list of str
        complement : bool, optional
            If True, get fields that are NOT in ref_quarterly_fields.
        Returns
        -------
        list
        """
        pool_map = {'market_daily': self.market_daily_fields,
                    'ref_daily': self.reference_daily_fields,
                    'income': self.fin_stat_income,
                    'balance_sheet': self.fin_stat_balance_sheet,
                    'cash_flow': self.fin_stat_cash_flow,
                    'fin_indicator': self.fin_indicator,
                    'group': self.group_fields,
                    'factor': self.factor_fields}
        pool_map['daily'] = set.union(pool_map['market_daily'],
                                      pool_map['ref_daily'],
                                      pool_map['group'],
                                      self.custom_daily_fields)
        pool_map['quarterly'] = set.union(pool_map['income'],
                                          pool_map['balance_sheet'],
                                          pool_map['cash_flow'],
                                          pool_map['fin_indicator'],
                                          self.custom_quarterly_fields)

        pool = pool_map.get(field_type, None)
        if pool is None:
            raise NotImplementedError("field_type = {:s}".format(field_type))

        s = set.intersection(set(pool), set(fields))
        if not s:
            return []

        if complement:
            s = set(fields) - s

        if field_type == 'market_daily':
            if self.adjust_mode is not None:
                tmp = []
                for field in list(s):
                    if field in ["open","high",'low','close',"vwap"]:
                        tmp.append(field)
                        tmp.append(field+"_adj")
                    elif field in ["open_adj","high_adj",'low_adj','close_adj',"vwap_adj"]:
                        tmp.append(field)
                        tmp.append(field.replace("_adj",""))
                s.update(tmp)

        if append:
            s.add('symbol')
            if field_type == 'market_daily' or field_type == 'ref_daily':
                s.add('trade_date')
                if field_type == 'market_daily':
                    s.add(self.TRADE_STATUS_FIELD_NAME)
            elif (field_type == 'income'
                  or field_type == 'balance_sheet'
                  or field_type == 'cash_flow'
                  or field_type == 'fin_indicator'):
                s.add(self.ANN_DATE_FIELD_NAME)
                s.add(self.REPORT_DATE_FIELD_NAME)

        l = list(s)
        return l

    def _query_data(self, symbol, fields):
        """
        Query data using different APIs, then store them in dict.
        period, start_date and end_date are fixed.
        Keys of dict are securitites.
        Parameters
        ----------
        symbol : list of str
        fields : list of str
        Returns
        -------
        daily_list : list
        quarterly_list : list
        """
        sep = ','
        symbol_str = sep.join(symbol)
        limit = 500000

        if self.freq == 1:
            daily_list = []
            quarterly_list = []

            # TODO : use fields = {field: kwargs} to enable params

            fields_market_daily = self._get_fields('market_daily', fields, append=True)
            if fields_market_daily:
                print("NOTE: price adjust method is [{:s} adjust]".format(self.adjust_mode if self.adjust_mode is not None else "No"))
                # no adjust prices and other market daily fields
                df_daily, msg1 = self.distributed_query('daily', symbol_str,
                                                        start_date=self.extended_start_date_d, end_date=self.end_date,
                                                        adjust_mode=None, fields=sep.join(fields_market_daily),
                                                        limit=limit)
                if self.adjust_mode is not None:
                    adjust_fields = list(set(fields_market_daily)&set(["open","high",'low','close',"vwap"]))
                    if len(adjust_fields)!=0:
                        adjust_fields+= ['symbol', 'trade_date']
                        df_daily_adjust, msg1 = self.distributed_query('daily', symbol_str,
                                                                       start_date=self.extended_start_date_d,
                                                                       end_date=self.end_date,
                                                                       adjust_mode=self.adjust_mode,
                                                                       fields=sep.join(adjust_fields),
                                                                       limit=limit)

                        df_daily = pd.merge(df_daily, df_daily_adjust, how='outer',
                                            on=['symbol', 'trade_date'], suffixes=('', '_adj'))
                daily_list.append(df_daily.loc[:, fields_market_daily])

            fields_ref_daily = self._get_fields('ref_daily', fields, append=True)
            if fields_ref_daily:
                df_ref_daily, msg2 = self.distributed_query('query_lb_dailyindicator', symbol_str,
                                                            start_date=self.extended_start_date_d,
                                                            end_date=self.end_date,
                                                            fields=sep.join(fields_ref_daily),
                                                            limit=limit)
                daily_list.append(df_ref_daily.loc[:, fields_ref_daily])

            # ----------------------------- query factor -----------------------------
            factor_fields = self._get_fields("factor", fields)
            if factor_fields:
                df_factor = self.get_factor(symbol, self.extended_start_date_d, self.end_date, factor_fields, limit=limit)
                daily_list.append(df_factor)

            # ----------------------------- query factor -----------------------------

            fields_income = self._get_fields('income', fields, append=True)
            if fields_income:
                df_income, msg3 = self.data_api.query_lb_fin_stat('income', symbol_str, self.extended_start_date_q,
                                                                  self.end_date,
                                                                  sep.join(fields_income),
                                                                  drop_dup_cols=['symbol', self.REPORT_DATE_FIELD_NAME])
                quarterly_list.append(df_income.loc[:, fields_income])

            fields_balance = self._get_fields('balance_sheet', fields, append=True)
            if fields_balance:
                df_balance, msg3 = self.data_api.query_lb_fin_stat(
                    'balance_sheet', symbol_str,
                    self.extended_start_date_q, self.end_date,
                    sep.join(fields_balance), drop_dup_cols=['symbol', self.REPORT_DATE_FIELD_NAME])
                quarterly_list.append(df_balance.loc[:, fields_balance])

            fields_cf = self._get_fields('cash_flow', fields, append=True)
            if fields_cf:
                df_cf, msg3 = self.data_api.query_lb_fin_stat('cash_flow', symbol_str, self.extended_start_date_q,
                                                              self.end_date,
                                                              sep.join(fields_cf),
                                                              drop_dup_cols=['symbol', self.REPORT_DATE_FIELD_NAME])
                quarterly_list.append(df_cf.loc[:, fields_cf])

            fields_fin_ind = self._get_fields('fin_indicator', fields, append=True)
            if fields_fin_ind:
                df_fin_ind, msg4 = self.data_api.query_lb_fin_stat(
                    'fin_indicator', symbol_str,
                    self.extended_start_date_q, self.end_date,
                    sep.join(fields_fin_ind),
                    drop_dup_cols=['symbol', self.REPORT_DATE_FIELD_NAME])
                quarterly_list.append(df_fin_ind.loc[:, fields_fin_ind])

        else:
            raise NotImplementedError("freq = {}".format(self.freq))
        return daily_list, quarterly_list

    def _fill_missing_idx_col(self, df, index=None, symbols=None):
        if index is None:
            index = df.index
        if symbols is None:
            symbols = self.symbol
        fields = df.columns.levels[1]

        if len(fields) * len(self.symbol) != len(df.columns) or len(index) != len(df.index):
            cols_multi = pd.MultiIndex.from_product([symbols, fields], names=['symbol', 'field'])
            cols_multi = cols_multi.sort_values()
            # df_final = pd.DataFrame(index=index, columns=cols_multi, data=np.nan)
            df_final = pd.DataFrame(df, index=index, columns=cols_multi)
            df_final.index.name = df.index.name
            # 取消了生成空表并update的步骤（速度太慢），改为直接扩展索引生成表
            # df_final.update(df)

            # idx_diff = sorted(set(df_final.index) - set(df.index))
            col_diff = sorted(set(df_final.columns.levels[0].values) - set(df.columns.levels[0].values))
            print("WARNING: some data is unavailable: "
                  # + "\n    At index " + ', '.join(idx_diff)
                  + "\n    At fields " + ', '.join(col_diff))
            return df_final
        else:
            return df

    @staticmethod
    def _merge_data(dfs, index_name='trade_date'):
        """
        Merge data from different APIs into one DataFrame.

        Parameters
        ----------
        dfs : list of pd.DataFrame

        Returns
        -------
        merge : pd.DataFrame or None
            If dfs is empty, return None

        Notes
        -----
        Align on date index, concatenate on columns (symbol and fields)

        """
        # dfs = [df for df in dfs if df is not None]

        # 这里用优化后的快速concat方法取代原生pandas的concat方法，在columns较长的情况下有明显提速
        # merge = pd.concat(dfs, axis=1, join='outer')
        merge = quick_concat(dfs, ['symbol', 'field'])

        # drop duplicated columns. ONE LINE EFFICIENT version
        mask_duplicated = merge.columns.duplicated()
        if np.any(mask_duplicated):
            # print("Duplicated columns found. Dropped.")
            merge = merge.loc[:, ~mask_duplicated]

            # if merge.isnull().sum().sum() > 0:
            # print "WARNING: nan in final merged data. NO fill"
            # merge.fillna(method='ffill', inplace=True)

        merge = merge.sort_index(axis=1, level=['symbol', 'field'])
        merge.index.name = index_name

        return merge

    def prepare_data(self):
        """Prepare data for the FIRST time."""
        # prepare benchmark and group
        print("Query data...")
        data_d, data_q = self._prepare_daily_quarterly(self.fields)
        self.data_d, self.data_q = data_d, data_q
        if self.data_q is not None:
            self._prepare_report_date()
        self._align_and_merge_q_into_d()

        print("Query instrument info...")
        self._prepare_inst_info()

        print("Query adj_factor...")
        self._prepare_adj_factor()

        if self.benchmark:
            print("Query benchmark...")
            self._data_benchmark = self._prepare_benchmark()
        if self.universe:
            print("Query benchmar member info...")
            self._prepare_comp_info()

        group_fields = self._get_fields('group', self.fields)
        if group_fields:
            print("Query groups (industry)...")
            self._prepare_group(group_fields)

        self.fields = []
        if (self.data_d is not None) and self.data_d.size != 0:
            self.fields += list(self.data_d.columns.levels[1])
        if (self.data_q is not None) and self.data_q.size != 0:
            self.fields += list(self.data_q.columns.levels[1])
        self.fields = list(set(self.fields))

        print("Data has been successfully prepared.")

    # Add/Remove Fields&Formulas
    def _add_field(self, field_name, is_quarterly=None):
        if field_name not in self.fields:
            self.fields.append(field_name)
        if not self._is_predefined_field(field_name):
            if is_quarterly is None:
                raise ValueError("Field [{:s}] is not a predefined field, but no frequency information is provided.")
            if is_quarterly:
                self.custom_quarterly_fields.append(field_name)
            else:
                self.custom_daily_fields.append(field_name)

    def add_field(self, field_name, data_api=None):
        """
        Query and append new field to DataView.

        Parameters
        ----------
        data_api : BaseDataServer
        field_name : str
            Must be a known field name (which is given in documents).

        Returns
        -------
        bool
            whether add successfully.

        """
        if data_api is None:
            if self.data_api is None:
                print("Add field failed. No data_api available. Please specify one in parameter.")
                return False
        else:
            self.data_api = data_api

        if field_name in self.fields:
            print("Field name [{:s}] already exists.".format(field_name))
            return False

        if not self._is_predefined_field(field_name):
            print("Field name [{}] not valid, ignore.".format(field_name))
            return False

        # prepare group type
        group_map = ['sw1',
                     'sw2',
                     'sw3',
                     'sw4',
                     'zz1',
                     'zz2']
        if field_name in group_map:
            self._prepare_group([field_name])
            return True

        if self._is_daily_field(field_name):
            if self.data_d is None:
                raise ValueError("Please prepare [{:s}] first.".format(field_name))
            merge, _ = self._prepare_daily_quarterly([field_name])
            is_quarterly = False
        else:
            if self.data_q is None:
                raise ValueError("Please prepare [{:s}] first.".format(field_name))
            _, merge = self._prepare_daily_quarterly([field_name])
            is_quarterly = True

        df = merge.loc[:, pd.IndexSlice[:, field_name]]
        df.columns = df.columns.droplevel(level=1)
        # whether contain only trade days is decided by existing data.

        # 季度添加至data_q　日度添加至data_d
        self.append_df(df, field_name, is_quarterly=is_quarterly)

        if is_quarterly:
            df_ann = merge.loc[:, pd.IndexSlice[:, self.ANN_DATE_FIELD_NAME]]
            df_ann.columns = df_ann.columns.droplevel(level='field')
            df_expanded = align(df, df_ann, self.dates)
            self.append_df(df_expanded, field_name, is_quarterly=False)
        return True

    def append_df(self, df, field_name, is_quarterly=False, overwrite=True):
        """
        Append DataFrame to existing multi-index DataFrame and add corresponding field name.

        Parameters
        ----------
        df : pd.DataFrame or pd.Series
        field_name : str or unicode
        is_quarterly : bool
            Whether df is quarterly data (like quarterly financial statement) or daily data.
        overwrite : bool, optional
            Whether overwrite existing field. True by default.
        Notes
        -----
        append_df does not support overwrite. To overwrite a field, you must first do self.remove_fields(),
        then append_df() again.

        """
        if is_quarterly:
            if self.data_q is None:
                raise ValueError("append_df前需要先确保季度数据集data_q不为空！")
            exist_fields = self.data_q.columns.remove_unused_levels().levels[1]
        else:
            if self.data_d is None:
                raise ValueError("append_df前需要先确保日度数据集data_d不为空！")
            exist_fields = self.data_d.columns.remove_unused_levels().levels[1]
        if field_name in exist_fields:
            if overwrite:
                self.remove_field(field_name)
                print("Field [{:s}] is overwritten.".format(field_name))
            else:
                print("Append df failed: name [{:s}] exist. Try another name.".format(field_name))
                return

        # 季度添加至data_q　日度添加至data_d
        df = df.copy()
        if isinstance(df, pd.DataFrame):
            pass
        elif isinstance(df, pd.Series):
            df = pd.DataFrame(df)
        else:
            raise ValueError("Data to be appended must be pandas format. But we have {}".format(type(df)))

        if is_quarterly:
            the_data = self.data_q
        else:
            the_data = self.data_d

        exist_symbols = the_data.columns.levels[0]
        if len(df.columns) < len(exist_symbols):
            df2 = pd.DataFrame(index=df.index, columns=exist_symbols, data=np.nan)
            df2.update(df)
            df = df2
        elif len(df.columns) > len(exist_symbols):
            df = df.loc[:, exist_symbols]
        multi_idx = pd.MultiIndex.from_product([exist_symbols, [field_name]])
        df.columns = multi_idx

        # the_data = apply_in_subprocess(pd.merge, args=(the_data, df),
        #                            kwargs={'left_index': True, 'right_index': True, 'how': 'left'})  # runs in *only* one process
        # the_data = pd.merge(the_data, df, left_index=True, right_index=True, how='left')
        the_data = quick_concat([the_data, df], ["symbol", "field"], how="inner")
        the_data = the_data.sort_index(axis=1)
        # merge = the_data.join(df, how='left')  # left: keep index of existing data unchanged
        # sort_columns(the_data)

        if is_quarterly:
            self.data_q = the_data
        else:
            self.data_d = the_data
        self._add_field(field_name, is_quarterly)

    def append_df_quarter(self, df, field_name, overwrite=True):
        if field_name in self.fields:
            if overwrite:
                self.remove_field(field_name)
                print("Field [{:s}] is overwritten.".format(field_name))
            else:
                print("Append df failed: name [{:s}] exist. Try another name.".format(field_name))
                return
        self.append_df(df, field_name, is_quarterly=True)
        df_ann = self._get_ann_df()
        df_expanded = align(df, df_ann, self.dates)
        self.append_df(df_expanded, field_name, is_quarterly=False)

    def add_comp_info(self, index, data_api=None):
        """
        Query and append index components info.

        Parameters
        ----------
        data_api : BaseDataServer
        index : str
            Index code separated by ','.

        Returns
        -------
        bool
            whether add successfully.

        """
        if data_api is None:
            if self.data_api is None:
                print("Add field failed. No data_api available. Please specify one in parameter.")
                return False
        else:
            self.data_api = data_api

        # if a symbol is index member of any one universe, its value of index_member will be 1.0
        universe = index.split(',')

        exist_symbols = self.data_d.columns.remove_unused_levels().levels[0]
        exist_fields = self.data_d.columns.remove_unused_levels().levels[1]

        for univ in universe:
            if univ + '_member' not in exist_fields:
                df = self.data_api.query_index_member_daily(univ, self.extended_start_date_d, self.end_date)

                if len(set(exist_symbols) - set(df.columns)) > 0:
                    symbols = list(set(exist_symbols) & set(df.columns))
                    df = df.loc[:, symbols]

                self.append_df(df, univ + '_member', is_quarterly=False)

                # use weights of the first universe
                df_weights = self.data_api.query_index_weights_daily(univ, self.extended_start_date_d, self.end_date)

                if len(set(exist_symbols) - set(df_weights.columns)) > 0:
                    symbols = list(set(exist_symbols) & set(df_weights.columns))
                    df_weights = df_weights.loc[:, symbols]

                self.append_df(df_weights, univ + '_weight', is_quarterly=False)

    def _add_symbol(self, symbol_name):
        if symbol_name in self.symbol:
            print("symbol [{:s}] already exists, add_symbol failed.".format(symbol_name))
            return
        self.symbol.append(symbol_name)

    def append_df_symbol(self, df, symbol_name, overwrite=False):
        """
        Append DataFrame to existing multi-index DataFrame and add corresponding field name.

        Parameters
        ----------
        df : pd.DataFrame or pd.Series
        symbol_name : str
        overwrite : bool, optional
            Whether overwrite existing field. True by default.
        Notes
        -----
        append_df does not support overwrite. To overwrite a field, you must first do self.remove_fields(),
        then append_df() again.

        """
        if symbol_name in self.symbol:
            if overwrite:
                self.remove_symbol(symbol_name)
                print("Symbol [{:s}] is overwritten.".format(symbol_name))
            else:
                print("Append symbol failed: symbol [{:s}] exist. ".format(symbol_name))
                return

        df = df.copy()
        if isinstance(df, pd.DataFrame):
            pass
        elif isinstance(df, pd.Series):
            df = pd.DataFrame(df)
        else:
            raise ValueError("Data to be appended must be pandas format. But we have {}".format(type(df)))

        the_data = self.data_d

        exist_fields = the_data.columns.levels[1]
        if len(set(exist_fields) - set(df.columns)):
            # if set(df.columns) < set(exist_fields):
            df2 = pd.DataFrame(index=df.index, columns=exist_fields, data=np.nan)
            df2.update(df)
            df = df2
        multi_idx = pd.MultiIndex.from_product([[symbol_name], exist_fields])
        df.columns = multi_idx

        # the_data = apply_in_subprocess(pd.merge, args=(the_data, df),
        #                            kwargs={'left_index': True, 'right_index': True, 'how': 'left'})  # runs in *only* one process
        the_data = pd.merge(the_data, df, left_index=True, right_index=True, how='left')
        the_data = the_data.sort_index(axis=1)
        # merge = the_data.join(df, how='left')  # left: keep index of existing data unchanged
        # sort_columns(the_data)

        self.data_d = the_data
        self._add_symbol(symbol_name)

    def remove_symbol(self, symbols):
        """

        Parameters
        ----------
        symbols : str or list
            The (custom) symbols to be removed from dataview.

        Returns
        -------
        bool
            whether remove successfully.

        """
        if isinstance(symbols, basestring):
            symbols = symbols.split(',')
        elif isinstance(symbols, (list, tuple)):
            pass
        else:
            raise ValueError("symbols must be str or list of str.")

        for symbol in symbols:
            # parameter validation
            if symbol not in self.symbol:
                print("symbol [{:s}] does not exist.".format(symbol))
                continue

            # remove symbol data
            if self.data_d is not None:
                self.data_d = self.data_d.drop(symbol, axis=1, level=0)

            if self.data_q is not None:
                self.data_q = self.data_q.drop(symbol, axis=1, level=0)

            # remove symbol from list
            self.symbol.remove(symbol)

        # change column index
        if self.data_d is not None:
            self.data_d.columns = self.data_d.columns.remove_unused_levels()

        if self.data_q is not None:
            self.data_q.columns = self.data_q.columns.remove_unused_levels()

    def add_formula(self, field_name, formula, is_quarterly,
                    add_data=False,
                    overwrite=True,
                    formula_func_name_style='camel', data_api=None,
                    register_funcs=None,
                    within_index=True):
        """
        Add a new field, which is calculated using existing fields.

        Parameters
        ----------
        formula : str or unicode
            A formula contains operations and function calls.
        field_name : str or unicode
            A custom name for the new field.
        is_quarterly : bool
            Whether df is quarterly data (like quarterly financial statement) or daily data.
        add_data: bool
            Whether add new data to the data set or return directly.
        overwrite : bool, optional
            Whether overwrite existing field. True by default.
        formula_func_name_style : {'upper', 'lower'}, optional
        data_api : RemoteDataService, optional
        register_funcs :Dict of functions you definite by yourself like {"name1":func1},
                        optional
        within_index : bool
            When do cross-section operatioins, whether just do within index components.

        Notes
        -----
        Time cost of this function:
            For a simple formula (like 'a + 1'), almost all time is consumed by append_df;
            For a complex formula (like 'GroupRank'), half of time is consumed by evaluation and half by append_df.
        """
        if data_api is not None:
            self.data_api = data_api

        if add_data:
            if field_name in self.fields:
                if overwrite:
                    self.remove_field(field_name)
                    print("Field [{:s}] is overwritten.".format(field_name))
                else:
                    raise ValueError("Add formula failed: name [{:s}] exist. Try another name.".format(field_name))
            elif self._is_predefined_field(field_name):
                raise ValueError("[{:s}] is alread a pre-defined field. Please use another name.".format(field_name))

        parser = Parser()
        parser.set_capital(formula_func_name_style)

        # 注册自定义函数
        if register_funcs is not None:
            for func in register_funcs.keys():
                if func in parser.ops1 or func in parser.ops2 or func in parser.functions or \
                                func in parser.consts or func in parser.values:
                    raise ValueError("注册的自定义函数名%s与内置的函数名称重复,请更换register_funcs中定义的相关函数名称." % (func,))
                parser.functions[func] = register_funcs[func]

        expr = parser.parse(formula)

        var_df_dic = dict()
        var_list = expr.variables()

        # TODO: users do not need to prepare data before add_formula
        if not self.fields:
            self.fields.extend(var_list)
            self.prepare_data()
        else:
            for var in var_list:
                if var not in self.fields:
                    print("Variable [{:s}] is not recognized (it may be wrong)," \
                          "try to fetch from the server...".format(var))
                    success = self.add_field(var)
                    if not success:
                        return

        for var in var_list:
            if self._is_quarter_field(var):
                df_var = self.get_ts_quarter(var, start_date=self.extended_start_date_q)
            else:
                # must use extended date. Default is start_date
                df_var = self.get_ts(var, start_date=self.extended_start_date_d, end_date=self.end_date)

            var_df_dic[var] = df_var

        # TODO: send ann_date into expr.evaluate. We assume that ann_date of all fields of a symbol is the same
        df_ann = self._get_ann_df()
        if within_index:
            df_index_member = self.get_ts('index_member', start_date=self.extended_start_date_d, end_date=self.end_date)
            if df_index_member.size == 0:
                df_index_member = None
            df_eval = parser.evaluate(var_df_dic, ann_dts=df_ann, trade_dts=self.dates, index_member=df_index_member)
        else:
            df_eval = parser.evaluate(var_df_dic, ann_dts=df_ann, trade_dts=self.dates)

        if add_data:
            if is_quarterly:
                self.append_df_quarter(df_eval, field_name)
            else:
                self.append_df(df_eval, field_name, is_quarterly=False)

        if is_quarterly:
            df_ann = self._get_ann_df()
            df_expanded = align(df_eval, df_ann, self.dates)
            return df_expanded.loc[self.start_date:self.end_date]
        else:
            return df_eval.loc[self.start_date:self.end_date]

    @property
    def func_doc(self):
        search = FuncDoc()
        return search
