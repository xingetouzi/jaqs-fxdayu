import os
import numpy as np
import pandas as pd
from jaqs import util as jutil
from jaqs_fxdayu.data.search_doc import FuncDoc
from jaqs_fxdayu.data.py_expression_eval import Parser

try:
    basestring
except NameError:
    basestring = str

from jaqs_fxdayu.util.concat import quick_concat


class HFDataView(object):

    def __init__(self):
        self.data_api = None

        self.universe = ""
        self.symbol = []
        self.benchmark = ""
        self.start_date = 0
        self.extended_start_date = 0
        self.end_date = 0
        self.fields = []
        self.meta_data_list = ['start_date', 'end_date',
                               'extended_start_date',
                               'fields', 'symbol', 'universe', 'benchmark']

        self.adjust_mode = 'post'

        self.data = None
        self.data_q = None
        self._data_benchmark = None
        self._data_inst = None

        self.market_fields = \
            {'open', 'high', 'low', 'close', 'volume', 'turnover', 'vwap', 'oi', 'trade_status',
             'open_adj', 'high_adj', 'low_adj', 'close_adj', 'vwap_adj', 'index_member', 'index_weight'}

        self.TRADE_STATUS_FIELD_NAME = 'trade_status'
        self.TRADE_DATE_FIELD_NAME = 'trade_date'

    # --------------------------------------------------------------------------------------------------------
    # Properties
    @property
    def data_benchmark(self):
        return self._data_benchmark

    @property
    def data_inst(self):
        """

        Returns
        -------
        pd.DataFrame

        """
        return self._data_inst

    @data_benchmark.setter
    def data_benchmark(self, df_new):
        if self.data is not None and df_new.shape[0] != self.data.shape[0]:
            raise ValueError("You must provide a DataFrame with the same shape of data_benchmark.")
        self._data_benchmark = df_new

    @property
    def dates(self):
        """
        Get daily date array of the underlying data.

        Returns
        -------
        res : np.array
            dtype: int

        """
        if self.data is not None:
            res = self.data.index.values
        return res

    def _is_predefined_field(self, field_name):
        """
        Check whether a field name can be recognized.
        field_name must be pre-defined or already added.

        Parameters
        ----------
        field_name : str

        Returns
        -------
        bool

        """
        res = field_name in self.market_fields
        return res

    # --------------------------------------------------------------------------------------------------------
    # Prepare data
    def init_from_config(self, props, data_api):
        """
        Initialize various attributes like start/end date, universe/symbol, fields, etc.
        If your want to parse symbol, but use a custom benchmark index, please directly assign self.data_benchmark.

        Parameters
        ----------
        props : dict
            start_date, end_date, freq, symbol, fields, etc.
        data_api : BaseDataServer

        """
        # data_api.init_from_config(props)
        self.data_api = data_api

        sep = ','

        # initialize parameters
        self.start_date = props['start_date']
        self.extended_start_date = jutil.shift(self.start_date, n_weeks=-1)  # query more data
        self.end_date = props['end_date']
        self.adjust_mode = props.get("adjust_mode", "post")

        # get and filter fields
        fields = props.get('fields', [])
        if fields:
            fields = props['fields'].split(sep)
            self.fields = [field for field in fields if self._is_predefined_field(field)]
            if len(self.fields) < len(fields):
                print("Field name [{}] not valid, ignore.".format(set.difference(set(fields), set(self.fields))))

        # initialize universe/symbol
        universe = props.get('universe', "")
        symbol = props.get('symbol', "")
        benchmark = props.get('benchmark', '')
        if symbol and universe:
            raise ValueError("Please use either [symbol] or [universe].")
        if not (symbol or universe):
            raise ValueError("One of [symbol] or [universe] must be provided.")
        if universe:
            univ_list = universe.split(',')
            self.universe = univ_list
            symbols_list = []
            for univ in univ_list:
                symbols_list.extend(data_api.query_index_member(univ, self.extended_start_date, self.end_date))
            self.symbol = sorted(list(set(symbols_list)))
        else:
            self.symbol = sorted(symbol.split(sep))
        if benchmark:
            self.benchmark = benchmark
        else:
            if self.universe:
                if len(self.universe) > 1:
                    print("More than one universe are used: {}, "
                          "use the first one ({}) as index by default. "
                          "If you want to use other benchmark, "
                          "please specify benchmark in configs.".format(repr(self.universe), self.universe[0]))
                self.benchmark = self.universe[0]

        print("Initialize config success.")

    # todo :prepare data, query data 初始化数据集,从数据接口取高频数据

    @staticmethod
    def _process_index_co(df, index_name):
        df = df.astype(dtype={index_name: "int64"})
        df = df.drop_duplicates(subset=['symbol', index_name])
        return df

    def _fill_missing_idx_col(self, df, index=None, symbols=None):
        if index is None:
            index = df.index
        if symbols is None:
            symbols = self.symbol
        fields = df.columns.levels[1]

        if len(fields) * len(self.symbol) != len(df.columns) or len(index) != len(df.index):
            cols_multi = pd.MultiIndex.from_product([symbols, fields], names=['symbol', 'field'])
            cols_multi = cols_multi.sort_values()
            df_final = pd.DataFrame(df, index=index, columns=cols_multi)
            df_final.index.name = df.index.name

            col_diff = sorted(set(df_final.columns.levels[0].values) - set(df.columns.levels[0].values))
            print("WARNING: some data is unavailable: "
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
        merge = quick_concat(dfs, ['symbol', 'field'])

        mask_duplicated = merge.columns.duplicated()
        if np.any(mask_duplicated):
            merge = merge.loc[:, ~mask_duplicated]
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
        self.extended_start_date = int(self.start_date)
        self.end_date = int(multi_df.index.levels[0][-1])
        self.fields = list(multi_df.columns)
        self.symbol = sorted(list(multi_df.index.levels[1]))

        # 处理data
        list_pivot = []
        for field in multi_df.columns:
            df = multi_df[field].reset_index()
            list_pivot.append(pivot_and_sort(df, self.TRADE_DATE_FIELD_NAME))
        self.data = self._merge_data(list_pivot, self.TRADE_DATE_FIELD_NAME)
        self.data = self._fill_missing_idx_col(self.data, index=self.dates, symbols=self.symbol)
        print("Initialize dataview success.")

    def remove_field(self, field_names):
        """
        Query and append new field to DataView.

        Parameters
        ----------
        field_names : str
            Separated by comma.
            The (custom) field to be removed from dataview.

        Returns
        -------
        bool
            whether add successfully.

        """
        if isinstance(field_names, basestring):
            field_names = field_names.split(',')
        else:
            raise ValueError("field_names must be str separated by comma.")

        for field_name in field_names:
            # parameter validation
            if field_name not in self.fields:
                print("Field name [{:s}] does not exist. Stop remove_field.".format(field_name))
                return
            # remove field data
            self.data = self.data.drop(field_name, axis=1, level=1)
            self.fields.remove(field_name)

    def _add_field(self, field_name):
        if field_name not in self.fields:
            self.fields.append(field_name)

    def append_df(self, df, field_name, overwrite=True):
        """
        Append DataFrame to existing multi-index DataFrame and add corresponding field name.

        Parameters
        ----------
        df : pd.DataFrame or pd.Series
        field_name : str or unicode
        overwrite : bool, optional
            Whether overwrite existing field. True by default.
        Notes
        -----
        append_df does not support overwrite. To overwrite a field, you must first do self.remove_fields(),
        then append_df() again.

        """

        exist_fields = self.data.columns.remove_unused_levels().levels[1]

        if field_name in exist_fields:
            if overwrite:
                self.remove_field(field_name)
                print("Field [{:s}] is overwritten.".format(field_name))
            else:
                print("Append df failed: name [{:s}] exist. Try another name.".format(field_name))
                return

        df = df.copy()
        if isinstance(df, pd.DataFrame):
            pass
        elif isinstance(df, pd.Series):
            df = pd.DataFrame(df)
        else:
            raise ValueError("Data to be appended must be pandas format. But we have {}".format(type(df)))

        the_data = self.data
        exist_symbols = the_data.columns.levels[0]

        if len(df.columns) < len(exist_symbols):
            df2 = pd.DataFrame(index=df.index, columns=exist_symbols, data=np.nan)
            df2.update(df)
            df = df2
        elif len(df.columns) > len(exist_symbols):
            df = df.loc[:, exist_symbols]
        multi_idx = pd.MultiIndex.from_product([exist_symbols, [field_name]])
        df.columns = multi_idx
        the_data = quick_concat([the_data, df.reindex(the_data.index)], ["symbol", "field"], how="inner")
        the_data = the_data.sort_index(axis=1)

        self.data = the_data
        self._add_field(field_name)

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
            if self.data is not None:
                self.data = self.data.drop(symbol, axis=1, level=0)

            # remove symbol from list
            self.symbol.remove(symbol)

        # change column index
        if self.data is not None:
            self.data.columns = self.data.columns.remove_unused_levels()

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

        the_data = self.data

        exist_fields = the_data.columns.levels[1]
        if len(set(exist_fields) - set(df.columns)):
            # if set(df.columns) < set(exist_fields):
            df2 = pd.DataFrame(index=df.index, columns=exist_fields, data=np.nan)
            df2.update(df)
            df = df2
        multi_idx = pd.MultiIndex.from_product([[symbol_name], exist_fields])
        df.columns = multi_idx

        the_data = pd.merge(the_data, df, left_index=True, right_index=True, how='left')
        the_data = the_data.sort_index(axis=1)

        self.data = the_data
        self._add_symbol(symbol_name)

    def add_formula(self, field_name, formula,
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
            raise ValueError("dv为空")
            # self.fields.extend(var_list)
            # self.prepare_data()
        else:
            for var in var_list:
                # todo
                if var not in self.fields:
                    raise ValueError("字段%s不存在."%(var,))
                    # print("Variable [{:s}] is not recognized (it may be wrong)," \
                    #       "try to fetch from the server...".format(var))
                    # success = self.add_field(var)
                    # if not success:
                    #     return

        for var in var_list:
            df_var = self.get_ts(var, start_date=self.extended_start_date, end_date=self.end_date)
            var_df_dic[var] = df_var

        # if within_index:
        #     df_index_member = self.get_ts('index_member', start_date=self.extended_start_date_d, end_date=self.end_date)
        #     if df_index_member.size == 0:
        #         df_index_member = None
        #     df_eval = parser.evaluate(var_df_dic, ann_dts=df_ann, trade_dts=self.dates, index_member=df_index_member)
        # else:
        df_eval = parser.evaluate(var_df_dic, ann_dts=None, trade_dts=self.dates)
        df_eval.index.name = self.TRADE_DATE_FIELD_NAME

        if add_data:
            self.append_df(df_eval, field_name)

        return df_eval.loc[self.start_date:self.end_date]

    @property
    def func_doc(self):
        search = FuncDoc()
        return search

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

        res = self.data.loc[pd.IndexSlice[start_date: end_date], pd.IndexSlice[symbol, fields]]
        if date_type!="int":
            res.index = pd.Series(res.index).apply(lambda x:trans_t(x))
        return res

    def get_snapshot(self, snapshot_date, symbol="", fields=""):
        """
        Get snapshot of given fields and symbol at snapshot_date.

        Parameters
        ----------
        snapshot_date : int
            Date of snapshot.
        symbol : str, optional
            Separated by ',' default "" (all securities).
        fields : str, optional
            Separated by ',' default "" (all fields).

        Returns
        -------
        res : pd.DataFrame
            symbol as index, field as columns

        """
        res = self.get(symbol=symbol, start_date=snapshot_date, end_date=snapshot_date, fields=fields)
        if res is None:
            print("No data. for date={}, fields={}, symbol={}".format(snapshot_date, fields, symbol))
            return

        res = res.stack(level='symbol', dropna=False)
        res.index = res.index.droplevel(level=self.TRADE_DATE_FIELD_NAME)

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

    # --------------------------------------------------------------------------------------------------------
    # DataView I/O
    @staticmethod
    def _load_h5(fp):
        """Load data and meta_data from hd5 file.

        Parameters
        ----------
        fp : str, optional
            File path of pre-stored hd5 file.

        """
        h5 = pd.HDFStore(fp)

        res = dict()
        for key in h5.keys():
            res[key] = h5.get(key)

        h5.close()

        return res

    def save_dataview(self, folder_path):
        """
        Save data and meta_data_to_store to a single hd5 file.
        Store at output/sub_folder

        Parameters
        ----------
        folder_path : str or unicode
            Path to store your data.

        """
        abs_folder = os.path.abspath(folder_path)
        meta_path = os.path.join(folder_path, 'meta_data.json')
        data_path = os.path.join(folder_path, 'data.hd5')

        data_to_store = {'data': self.data,
                         'data_benchmark': self.data_benchmark, 'data_inst': self._data_inst}
        data_to_store = {k: v for k, v in data_to_store.items() if v is not None}
        meta_data_to_store = {key: self.__dict__[key] for key in self.meta_data_list}

        print("\nStore data...")
        jutil.save_json(meta_data_to_store, meta_path)
        self._save_h5(data_path, data_to_store)

        print("Dataview has been successfully saved to:\n"
              + abs_folder + "\n\n"
              + "You can load it with load_dataview('{:s}')".format(abs_folder))

    def load_dataview(self, folder_path='.'):
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
        self.data = dic.get('/data', None)
        self._data_benchmark = dic.get('/data_benchmark', None)
        self._data_inst = dic.get('/data_inst', None)
        self.__dict__.update(meta_data)

        print("Dataview loaded successfully.")

    @staticmethod
    def _save_h5(fp, dic):
        """
        Save data in dic to a hd5 file.

        Parameters
        ----------
        fp : str
            File path.
        dic : dict

        """
        import warnings
        warnings.filterwarnings('ignore', category=pd.io.pytables.PerformanceWarning)

        jutil.create_dir(fp)
        h5 = pd.HDFStore(fp, complevel=9, complib='blosc')
        for key, value in dic.items():
            h5[key] = value
        h5.close()


