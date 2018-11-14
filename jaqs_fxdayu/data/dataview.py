import os
import copy
import numpy as np
import pandas as pd
from jaqs import util as jutil
from jaqs.data.align import align
from jaqs.data.dataview import DataView as OriginDataView, EventDataView

from jaqs_fxdayu.data.search_doc import FuncDoc
from jaqs_fxdayu.patch_util import auto_register_patch
from jaqs_fxdayu.data.py_expression_eval import Parser

try:
    basestring
except NameError:
    basestring = str


PF = "prepare_fields"


# def quick_concat(dfs, level, index_name="trade_date"): joined_index = pd.Index(np.concatenate([df.index.values for
# df in dfs]), name=index_name).sort_values().drop_duplicates() joined_columns = pd.MultiIndex.from_tuples(
# np.concatenate([df.columns.values for df in dfs]), names=level) result = [pd.DataFrame(df, joined_index).values for
#  df in dfs] return pd.DataFrame(np.concatenate(result, axis=1), joined_index, joined_columns)
from jaqs_fxdayu.util.concat import quick_concat


@auto_register_patch(parent_level=1)
class DataView(OriginDataView):
    def __init__(self):
        super(DataView, self).__init__()
        self.fields_mapper = {
            "lb.secDailyIndicator": self.reference_daily_fields,
            "lb.income": self.fin_stat_income,
            "lb.balanceSheet": self.fin_stat_balance_sheet,
            "lb.cashFlow": self.fin_stat_cash_flow,
            "lb.finIndicator": self.fin_indicator,
            "daily": self.market_daily_fields,
            "lb.secAdjFactor": {"adjust_factor"}
        }
        self.external_fields = {}
        self.external_quarterly_fields = {}
        self.factor_fields = set()
        self.meta_data_list = self.meta_data_list + ['_prepare_fields','report_type']
        self._prepare_fields = False
        self._has_prepared_fields = False
        self.report_type = None

    def init_from_config(self, props, data_api):
        self.adjust_mode = props.get("adjust_mode", "post")
        self.report_type = props.get("report_type", "408001000") # 默认报表类型为合并报表
        _props = props.copy()
        self._prepare_fields = _props.pop(PF, False)
        if self._prepare_fields:
            self.prepare_fields(data_api)
        super(DataView, self).init_from_config(_props, data_api)

    def _is_predefined_field(self, field_name):
        if self._prepare_fields and not self._has_prepared_fields:
            if self.data_api is None:
                raise RuntimeError("DataView's data_api is None when calling self.prepare_data.")
            self.prepare_fields(self.data_api)
        return super(DataView, self)._is_predefined_field(field_name)

    @staticmethod
    def _is_quarterly(params):
        for name in ("ann_date", "report_date", "symbol"):
            if name not in params:
                return False
        return True

    def prepare_fields(self, data_api):
        mapper = data_api.predefined_fields()
        custom_daily = set()
        custom_quarterly = set()
        for name in self.fields_mapper:
            offical = mapper.pop(name, set())
            offical.difference_update({"trade_date", "symbol"})
            self.fields_mapper[name].update(offical)
        for api, param in mapper.items():
            if self._is_quarterly(param):
                param.difference_update({"ann_date", "symbol", "report_date"})
                self.external_quarterly_fields.update(dict.fromkeys(param, api))
                custom_quarterly.update(set(param))
            else:
                param.difference_update({"trade_date", "symbol"})
                self.external_fields.update(dict.fromkeys(param, api))
                custom_daily.update(set(param))
        for fields in self.fields_mapper.values():
            custom_daily.difference_update(fields)
            custom_quarterly.difference_update(fields)
        self.custom_daily_fields.extend(custom_daily)
        self.custom_quarterly_fields.extend(custom_quarterly)
        self._has_prepared_fields = True

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
                    'group': self.group_fields}
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
        if isinstance(fields, set):
            for f in l:
                fields.discard(f)
        return l

    @staticmethod
    def _find_external_params(fields, external_map):
        dct = {}
        for field in fields:
            dct.setdefault(external_map.get(field, None), set()).add(field)
        dct.pop(None, None)
        return dct

    def query_external_quaterly(self, fields, start, end, symbol):
        if not isinstance(symbol, str):
            from collections import Iterable
            if isinstance(symbol, Iterable):
                symbol = ",".join(symbol)
        filters = "start_ann_date=%s&end_ann_date=%s&symbol=%s" % (start, end, symbol)
        target = self._find_external_params(fields, self.external_quarterly_fields)
        for view, params in target.items():
            params.update({"ann_date", "report_date", "symbol"})
            data, msg = self.data_api.query(view, filters, ",".join(params))
            if msg == "0,":
                for key in ["ann_date", "report_date"]:
                    data[key] = data[key].apply(int)
                yield data
            else:
                raise Exception(msg)

    def query_external_daily(self, fields, start, end, symbol):
        if not isinstance(symbol, str):
            from collections import Iterable
            if isinstance(symbol, Iterable):
                symbol = ",".join(symbol)
        filters = "start_date=%s&end_date=%s&symbol=%s" % (start, end, symbol)
        target = self._find_external_params(fields, self.external_fields)
        for view, params in target.items():
            data, msg = self.data_api.query(view, filters, ",".join(params))
            if msg == "0,":
                yield data
            else:
                raise Exception(msg)

        if isinstance(fields, set):
            for view, params in target.items():
                for p in params: 
                    fields.discard(p)

    def _query_data(self, symbol, fields, report_type='408001000'):
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
        fields = set(fields)

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


            fields_income = self._get_fields('income', fields, append=True)
            if fields_income:
                df_income, msg3 = self.data_api.query_lb_fin_stat('income', symbol_str, self.extended_start_date_q,
                                                                  self.end_date,
                                                                  sep.join(fields_income),
                                                                  drop_dup_cols=['symbol', self.REPORT_DATE_FIELD_NAME],
                                                                  report_type=report_type)
                quarterly_list.append(df_income.loc[:, fields_income])

            fields_balance = self._get_fields('balance_sheet', fields, append=True)
            if fields_balance:
                df_balance, msg3 = self.data_api.query_lb_fin_stat(
                    'balance_sheet', symbol_str,
                    self.extended_start_date_q, self.end_date,
                    sep.join(fields_balance), drop_dup_cols=['symbol', self.REPORT_DATE_FIELD_NAME],
                    report_type=report_type)
                quarterly_list.append(df_balance.loc[:, fields_balance])

            fields_cf = self._get_fields('cash_flow', fields, append=True)
            if fields_cf:
                df_cf, msg3 = self.data_api.query_lb_fin_stat('cash_flow', symbol_str, self.extended_start_date_q,
                                                              self.end_date,
                                                              sep.join(fields_cf),
                                                              drop_dup_cols=['symbol', self.REPORT_DATE_FIELD_NAME],
                                                              report_type=report_type)
                quarterly_list.append(df_cf.loc[:, fields_cf])

            fields_fin_ind = self._get_fields('fin_indicator', fields, append=True)
            if fields_fin_ind:
                df_fin_ind, msg4 = self.data_api.query_lb_fin_stat(
                    'fin_indicator', symbol_str,
                    self.extended_start_date_q, self.end_date,
                    sep.join(fields_fin_ind),
                    drop_dup_cols=['symbol', self.REPORT_DATE_FIELD_NAME],
                    report_type=report_type)

                quarterly_list.append(df_fin_ind.loc[:, fields_fin_ind])

            # ----------------------------- query external -----------------------------
            # daily
            for data in self.query_external_daily(fields, self.extended_start_date_d, self.end_date, self.symbol):
                daily_list.append(data)
            
            # quarterly
            for data in self.query_external_quaterly(fields, self.extended_start_date_d, self.end_date, self.symbol):
                quarterly_list.append(data)
            
            # ----------------------------- query external -----------------------------
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
        # for df in dfs:
        #     df.rename_axis(lambda s: int(s), inplace=True)
            
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

    def create_init_dv(self, multi_df):

        def pivot_and_sort(df, index_name):
            df = self._process_index_co(df, index_name)
            df = df.pivot(index=index_name, columns='symbol')
            df.columns = df.columns.swaplevel()
            col_names = ['symbol', 'field']
            df.columns.names = col_names
            df = df.sort_index(axis=1, level=col_names)
            df.index.name = index_name
            return df

        # initialize parameters
        self.start_date = int(multi_df.index.levels[0][0])
        self.extended_start_date_d = int(self.start_date)
        self.end_date = int(multi_df.index.levels[0][-1])
        self.fields = list(multi_df.columns)
        self.symbol = sorted(list(multi_df.index.levels[1]))

        # 处理data
        list_pivot = []
        for field in multi_df.columns:
            df = multi_df[field].reset_index()
            list_pivot.append(pivot_and_sort(df, self.TRADE_DATE_FIELD_NAME))
        self.data_d = self._merge_data(list_pivot, self.TRADE_DATE_FIELD_NAME)
        self.data_d = self._fill_missing_idx_col(self.data_d, index=self.dates, symbols=self.symbol)
        print("Initialize dataview success.")

    def prepare_data(self):
        """Prepare data for the FIRST time."""
        # prepare benchmark and group
        print("Query data...")
        self.fields = list(set(self.fields)|set(["trade_status"]))
        data_d, data_q = self._prepare_daily_quarterly(self.fields, self.report_type)
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

        trade_status = self.get_ts("trade_status")
        if trade_status.size>0:
            try:
                trade_status = trade_status.fillna(-1).astype(int)
            except:
                tmp = (trade_status.fillna("")==u"交易").astype(int)
                tmp[trade_status.fillna("") == ""] = np.NaN
                self.append_df(tmp,"trade_status")

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

    def add_field(self, field_name, data_api=None, report_type='408001000'):
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
            if self.data_d is None:
                self.fields = []
            else:
                print("Field name [{:s}] already exists.".format(field_name))
                return False

        if not self._is_predefined_field(field_name):
            print("Field name [{}] not valid, ignore.".format(field_name))
            return False

        if self.data_d is None:
            self.data_d, _ = self._prepare_daily_quarterly(["trade_status"])
            self._add_field("trade_status")
            trade_status = self.get_ts("trade_status")
            if trade_status.size > 0:
                try:
                    trade_status = trade_status.astype(int)
                except:
                    tmp = (trade_status.fillna("") == u"交易").astype(int)
                    tmp[trade_status.fillna("") == ""] = np.NaN
                    self.append_df(tmp, "trade_status")

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
            merge, _ = self._prepare_daily_quarterly([field_name])
            is_quarterly = False
        else:
            if self.data_q is None:
                _, self.data_q = self._prepare_daily_quarterly(["ann_date"])
                self._add_field("ann_date")
                self._prepare_report_date()
                self._align_and_merge_q_into_d()
            _, merge = self._prepare_daily_quarterly([field_name],report_type)
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
        the_data = quick_concat([the_data, df.reindex(the_data.index)], ["symbol", "field"], index_name=the_data.index.name, how="inner")
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
        df_expanded = align(df.reindex_like(df_ann), df_ann, self.dates)
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

        all_quarterly=True
        for var in var_list:
            if self._is_quarter_field(var) and is_quarterly:
                df_var = self.get_ts_quarter(var, start_date=self.extended_start_date_q)
            else:
                # must use extended date. Default is start_date
                df_var = self.get_ts(var, start_date=self.extended_start_date_d, end_date=self.end_date)
                all_quarterly=False
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
            if all_quarterly:
                self.append_df_quarter(df_eval, field_name)
            else:
                self.append_df(df_eval, field_name, is_quarterly=False)

        if all_quarterly:
            df_ann = self._get_ann_df()
            df_expanded = align(df_eval.reindex(df_ann.index), df_ann, self.dates)
            df_expanded.index.name = self.TRADE_DATE_FIELD_NAME
            return df_expanded.loc[self.start_date:self.end_date]
        else:
            df_eval.index.name = self.TRADE_DATE_FIELD_NAME
            return df_eval.loc[self.start_date:self.end_date]

    @property
    def func_doc(self):
        search = FuncDoc()
        return search

    def load_dataview(self, folder_path='.', *args, **kwargs):
        """
        Load data from local file.
        Parameters
        ----------
        folder_path : str or unicode, optional
            Folder path to store hd5 file and meta data.
        """

        path_meta_data = os.path.join(folder_path, 'meta_data.json')
        path_data = os.path.join(folder_path, 'data.hd5')
        if not (os.path.exists(path_meta_data) and os.path.exists(path_data)):
            raise IOError("There is no data file under directory {}".format(folder_path))

        meta_data = jutil.read_json(path_meta_data)
        dic = self._load_h5(path_data)
        self.data_d = dic.get('/data_d', None)
        self.data_q = dic.get('/data_q', None)
        self._data_benchmark = dic.get('/data_benchmark', None)
        self._data_inst = dic.get('/data_inst', None)
        self.__dict__.update(meta_data)
        print("Dataview loaded successfully.")

    def add_symbol(self, symbol, data_api=None):
        # TODO to realize it.
        data_api = data_api or self.data_api
        if self.data_api is None:
            self.data_api = data_api
        if self.data_api is None:
            raise ValueError("You must provide the data_api to refresh data.")
        tmp_dv = DataView()
        new_symbol = list(set(symbol.split(",")).difference(self.symbol + [""]))
        if not new_symbol:
            return
        props={
            "start_date": self.start_date,
            "end_date": self.end_date,
            "symbol": ",".join(new_symbol),
            "fields": ",".join(self.fields),
            "adjust_mode": self.adjust_mode,
            "prepare_fields": self._prepare_fields,
        }
        tmp_dv.init_from_config(data_api=data_api, props=props)
        tmp_dv.universe = self.universe
        tmp_dv.prepare_data()
        if self.data_d is not None and tmp_dv.data_d is not None:
            self.data_d = pd.concat([self.data_d,tmp_dv.data_d],axis=1)
        else:
            self.data_d = self.data_d or tmp_dv.data_d
        if self.data_q is not None and tmp_dv.data_q is not None:
            self.data_q = pd.concat([self.data_q,tmp_dv.data_q],axis=1)
        else:
            self.data_q = self.data_q or tmp_dv.data_q
        self._data_inst = pd.concat([self.data_inst, tmp_dv.data_inst], axis=0).drop_duplicates()

    def _prepare_comp_info(self):
        # if a symbol is index member of any one universe, its value of index_member will be 1.0
        res = dict()
        for univ in self.universe:
            df = self.data_api.query_index_member_daily(univ, self.extended_start_date_d, self.end_date)
            res[univ] = df
        df_res = pd.concat(res, axis=0)
        df = df_res.groupby(by='trade_date').apply(lambda df: df.any(axis=0)).astype(float)
        extra_symbol = list(set(self.symbol) - set(df.columns))
        if extra_symbol:
            df = pd.concat([df, pd.DataFrame(np.zeros((len(df.index), len(extra_symbol))), index=df.index, columns=extra_symbol)], axis=1)
        self.append_df(df, 'index_member', is_quarterly=False)
    
        # use weights of the first universe
        df_weights = self.data_api.query_index_weights_daily(self.universe[0], self.extended_start_date_d, self.end_date)
        extra_symbol_weights = df_weights.columns
        extra_symbol_weights = list(set(self.symbol) - set(df_weights.columns))
        if extra_symbol_weights:
            df_weights = pd.concat([df_weights, pd.DataFrame(np.zeros((len(df_weights.index), len(extra_symbol_weights))), index=df_weights.index, columns=extra_symbol_weights)], axis=1)
        self.append_df(df_weights, 'index_weight', is_quarterly=False)

    def refresh_data(self, end_date, symbol="", data_api=None):
        """
        Update the dataview's data to new end_date.
        
        Parameters
        ----------
        end_date : int 
            The dataview will refresh it's data to the end_date.
        symbol : str, optional
            The dataview's symbol will be the union set of self.symbol and symbol, 
            and all data will be prepared automatically.
            Using it when you calcualtor logic need also update new symbols.
            (the default is "", which means no symbol will be update)
        data_api : DataService, optional
            The data_api by which to fetch the data (the default is None, which means using this dataview's data_api)
        
        Notes
        -----
        If you using universe rather than symbol, you needn't to handle new universe member yourself,
        This fucntion will automatically handle it.

        Raises
        ------
        ValueError
            raise when no data_api is provided.
        """
        if self.end_date < end_date:
            union_symbol = list(set(self.symbol + symbol.split(","))-set([""]))
            data_api = data_api or self.data_api
            if self.data_api is None:
                self.data_api = data_api
            if self.data_api is None:
                raise ValueError("You must provide the data_api to refresh data.")
            start = self.end_date
            end = end_date
            tmp_dv = DataView()
            # if you use universe, it will automate update symbol.
            if self.universe and len(self.universe) > 0:
                props={
                    "start_date":start,
                    "end_date": end,
                    "universe": ",".join(self.universe),
                    "fields": ",".join(self.fields),
                    "all_price": self.all_price,
                    "report_type": self.report_type,
                    "benchmark": self.benchmark,
                    "adjust_mode":self.adjust_mode,
                    "prepare_fields":self._prepare_fields
                }
            # if you use symbol and in you logic
            else:
                props={
                    "start_date": start,
                    "end_date": end,
                    "symbol": ",".join(union_symbol),
                    "fields": ",".join(self.fields),
                    "all_price": self.all_price,
                    "report_type": self.report_type,
                    "benchmark": self.benchmark,
                    "adjust_mode":self.adjust_mode,
                    "prepare_fields":self._prepare_fields
                }
            tmp_dv.init_from_config(data_api=data_api, props=props)
            tmp_dv.benchmark = self.benchmark
            tmp_dv.universe = self.universe
            tmp_dv.prepare_data()
            new_symbol_dv = list(set(tmp_dv.symbol).difference(self.symbol))
            new_symbol_tmp_dv = list(set(self.symbol).difference(tmp_dv.symbol))
            if new_symbol_dv:
                self.add_symbol(",".join(new_symbol_dv))
            if new_symbol_tmp_dv:
                tmp_dv.add_symbol(",".join(new_symbol_tmp_dv))

            # TODO change to quick concat.
            if self.data_d is not None and tmp_dv.data_d is not None:
                self.data_d = pd.concat([self.data_d,tmp_dv.data_d.loc[self.end_date+1:]],axis=0)
            else:
                self.data_d = self.data_d or tmp_dv.data_d
            if self.data_q is not None and tmp_dv.data_q is not None:
                self.data_q = pd.concat([self.data_q,tmp_dv.data_q.loc[self.end_date+1:]],axis=0)
            else:
                self.data_q = self.data_q or tmp_dv.data_q
            self._data_inst = pd.concat([self.data_inst, tmp_dv.data_inst], axis=0).drop_duplicates()
            if self.benchmark:
                self._data_benchmark = pd.concat([self._data_benchmark,tmp_dv._data_benchmark.loc[self.end_date+1:]],axis=0)
            self.end_date = int(self.data_d.index[-1])
        else:
            print("New end_date %s is earlier than dv's end_date %s, skip." % (end_date, self.end_date))
        
    def slice_dv(self, start_date, end_date, data_api=None, inplace=False):
        if start_date < self.start_date:
            raise IndexError("Sliced dataview beyond its start_date %s: %s!" % (self.start_date, start_date))
        if inplace:
            dv =  self
        else:
            dv = self.__class__()
            if self.universe and len(self.universe) > 0:
                props={
                    "start_date": start_date,
                    "end_date": end_date,
                    "universe": ",".join(self.universe),
                    'fields': ",".join(self.fields),
                    "all_price": self.all_price,
                    "report_type": self.report_type,
                    "benchmark": self.benchmark,
                    "adjust_mode":self.adjust_mode,
                    "prepare_fields":self._prepare_fields
                }
            # if you use symbol and in you logic
            else:
                props={
                    "start_date": start_date,
                    "end_date": end_date,
                    "symbol": ",".join(self.symbol),
                    "fields": ",".join(self.fields),
                    "all_price": self.all_price,
                    "report_type": self.report_type,
                    "benchmark": self.benchmark,
                    "adjust_mode":self.adjust_mode,
                    "prepare_fields":self._prepare_fields
                }
            dv.init_from_config(data_api = data_api or self.data_api, props=props)
            dv.fields = copy.copy(self.fields)
            dv.data_q = self.data_q.loc[dv.extended_start_date_q:dv.end_date]
            dv.data_d = self.data_d.loc[dv.extended_start_date_d:dv.end_date]
            dv.data_benchmark = self.data_benchmark.loc[dv.extended_start_date_d:dv.end_date]
        if end_date > dv.end_date:
            print("Sliced dataview's end_date is %s, expected %s, refresh_data is called to extend it." % (dv.end_date, end_date))
            dv.refresh_data(end_date, data_api)
        dv.end_date = int(dv.data_d.index[-1])
        return dv

    # data_q存在NaN时会导致合并数据丢失，这里做用前值填充data_q的处理
    def _prepare_daily_quarterly(self, fields, report_type='408001000'):
        if not fields:
            return None, None

        # query data
        print("Query data - query...")
        daily_list, quarterly_list = self._query_data(self.symbol, fields, report_type)

        def pivot_and_sort(df, index_name):
            df = self._process_index_co(df, index_name)
            df = df.pivot(index=index_name, columns='symbol')
            df.columns = df.columns.swaplevel()
            col_names = ['symbol', 'field']
            df.columns.names = col_names
            df = df.sort_index(axis=1, level=col_names)
            df.index.name = index_name
            return df

        multi_daily = None
        multi_quarterly = None
        if daily_list:
            daily_list_pivot = [pivot_and_sort(df, self.TRADE_DATE_FIELD_NAME) for df in daily_list]
            multi_daily = self._merge_data(daily_list_pivot, self.TRADE_DATE_FIELD_NAME)
            # use self.dates as index because original data have weekends
            multi_daily = self._fill_missing_idx_col(multi_daily, index=self.dates, symbols=self.symbol)
            print("Query data - daily fields prepared.")
        if quarterly_list:
            quarterly_list_pivot = [pivot_and_sort(df, self.REPORT_DATE_FIELD_NAME) for df in quarterly_list]
            multi_quarterly = self._merge_data(quarterly_list_pivot, self.REPORT_DATE_FIELD_NAME)
            multi_quarterly = self._fill_missing_idx_col(multi_quarterly, index=None, symbols=self.symbol)
            print("Query data - quarterly fields prepared.")

        data_d, data_q = multi_daily, multi_quarterly
        # 判断data_q 是否为DataFrame
        if isinstance(data_q, pd.DataFrame):
            data_q = data_q.ffill()
        return data_d, data_q

    def get(self, symbol="", start_date=0, end_date=0, fields="", date_type="int"):
        """
        Basic API to get arbitrary data. If nothing fetched, return None.

        Parameters
        ----------
        symbol : str, optional
            Separated by ',' default "" (all securities).
        start_date : int, optional
            Default 0 (self.start_date).
        end_date : int, optional
            Default 0 (self.start_date).
        fields : str, optional
            Separated by ',' default "" (all fields).

        Returns
        -------
        res : pd.DataFrame or None
            index is datetimeindex, columns are (symbol, fields) MultiIndex

        """

        def trans_t(x):
            value = str(int(x))
            format = '%Y%m%d' if len(value) == 8 else '%Y%m%d%H%M%S'
            pd.to_datetime(value, format=format)
            return pd.to_datetime(value, format=format)

        sep = ','

        if not fields:
            fields = slice(None)  # self.fields
        else:
            fields = fields.split(sep)

        if not symbol:
            symbol = slice(None)  # this is 3X faster than symbol = self.symbol
        else:
            symbol = symbol.split(sep)

        if not start_date:
            start_date = self.start_date
        if not end_date:
            end_date = self.end_date

        res = self.data_d.loc[pd.IndexSlice[start_date: end_date], pd.IndexSlice[symbol, fields]]
        if date_type!="int":
            res.index = pd.Series(res.index).apply(lambda x:trans_t(x))
        return res

    def get_symbol(self, symbol, start_date=0, end_date=0, fields="", date_type="int"):
        res = self.get(symbol, start_date=start_date, end_date=end_date, fields=fields, date_type=date_type)
        if res is None:
            raise ValueError("No data. for "
                             "start_date={}, end_date={}, field={}, symbol={}".format(start_date, end_date,
                                                                                      fields, symbol))

        res.columns = res.columns.droplevel(level='symbol')
        return res

    def get_ts(self, field, symbol="", start_date=0, end_date=0, date_type="int"):
        """
        Get time series data of single field.

        Parameters
        ----------
        field : str or unicode
            Single field.
        symbol : str, optional
            Separated by ',' default "" (all securities).
        start_date : int, optional
            Default 0 (self.start_date).
        end_date : int, optional
            Default 0 (self.start_date).

        Returns
        -------
        res : pd.DataFrame
            Index is int date, column is symbol.

        """
        res = self.get(symbol, start_date=start_date, end_date=end_date, fields=field, date_type=date_type)
        if res is None:
            print("No data. for start_date={}, end_date={}, field={}, symbol={}".format(start_date,
                                                                                        end_date, field, symbol))
            raise ValueError

        res.columns = res.columns.droplevel(level='field')

        return res
