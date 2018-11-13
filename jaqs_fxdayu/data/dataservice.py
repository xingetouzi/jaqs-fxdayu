# noinspection PyUnresolvedReferences
from jaqs.data.dataservice import *
from jaqs.data.dataservice import RemoteDataService as OriginRemoteDataService
import os
import h5py
import json
import bisect
import numpy as np
import pandas as pd
import jaqs.util as jutil
from datetime import datetime
from jaqs.data.align import align
from jaqs_fxdayu.patch_util import auto_register_patch


class DataNotFoundError(Exception):
    pass


class SqlError(Exception):
    pass


@auto_register_patch(parent_level=1)
class RemoteDataService(OriginRemoteDataService):
    def __init__(self):
        super(OriginRemoteDataService, self).__init__()
        self.data_api = None
        self._address = ""
        self._username = ""
        self._password = ""
        self._timeout = 60

        self._REPORT_DATE_FIELD_NAME = 'report_date'

    def query_industry_daily(self, symbol, start_date, end_date, type_='SW', level=1):
        """
        Get index components on each day during start_date and end_date.

        Parameters
        ----------
        symbol : str
            separated by ','
        start_date : int
        end_date : int
        type_ : {'SW', 'ZZ'}

        Returns
        -------
        res : pd.DataFrame
            index dates, columns symbols
            values are industry code

        """
        df_raw = self.query_industry_raw(symbol, type_=type_, level=level)

        dic_sec = jutil.group_df_to_dict(df_raw, by='symbol')
        dic_sec = {sec: df.sort_values(by='in_date', axis=0).reset_index()
                   for sec, df in dic_sec.items()}

        df_ann_tmp = pd.concat({sec: df.loc[:, 'in_date'] for sec, df in dic_sec.items()}, axis=1)
        df_value_tmp = pd.concat({sec: df.loc[:, 'industry{:d}_name'.format(level)]
                                  for sec, df in dic_sec.items()},
                                 axis=1)

        idx = np.unique(np.concatenate([df.index.values for df in dic_sec.values()]))
        symbol_arr = np.sort(symbol.split(','))
        df_ann = pd.DataFrame(index=idx, columns=symbol_arr, data=np.nan)
        df_ann.loc[df_ann_tmp.index, df_ann_tmp.columns] = df_ann_tmp
        df_value = pd.DataFrame(index=idx, columns=symbol_arr, data=np.nan)
        df_value.loc[df_value_tmp.index, df_value_tmp.columns] = df_value_tmp

        dates_arr = self.query_trade_dates(start_date, end_date)
        df_industry = align(df_value, df_ann, dates_arr)

        # TODO before industry classification is available, we assume they belong to their first group.
        df_industry = df_industry.fillna(method='bfill')
        df_industry = df_industry.astype(str)

        return df_industry

    def query_lb_fin_stat(self, type_, symbol, start_date, end_date, fields="", drop_dup_cols=None,
                          report_type='408001000'):
        """
        Helper function to call data_api.query with 'lb.income' more conveniently.

        Parameters
        ----------
        type_ : {'income', 'balance_sheet', 'cash_flow'}
        symbol : str
            separated by ','
        start_date : int
            Annoucement date in results will be no earlier than start_date
        end_date : int
            Annoucement date in results will be no later than start_date
        fields : str, optional
            separated by ',', default ""
        drop_dup_cols : list or tuple
            Whether drop duplicate entries according to drop_dup_cols.

        Returns
        -------
        df : pd.DataFrame
            index date, columns fields
        err_msg : str

        """
        view_map = {'income': 'lb.income', 'cash_flow': 'lb.cashFlow', 'balance_sheet': 'lb.balanceSheet',
                    'fin_indicator': 'lb.finIndicator'}
        view_name = view_map.get(type_, None)
        if view_name is None:
            raise NotImplementedError("type_ = {:s}".format(type_))

        dic_argument = {'symbol': symbol,
                        'start_date': start_date,
                        'end_date': end_date,
                        # 'update_flag': '0'
                        }
        if view_name != 'lb.finIndicator':
            dic_argument.update({'report_type': report_type})  # we do not use single quarter single there are zeros
            """
            408001000: joint
            408002000: joint (single quarter)
            """

        filter_argument = self._dic2url(dic_argument)  # 0 means first time, not update

        res, err_msg = self.query(view_name, fields=fields, filter=filter_argument,
                                  order_by=self._REPORT_DATE_FIELD_NAME)
        self._raise_error_if_msg(err_msg)

        # change data type
        try:
            cols = list(set.intersection({'ann_date', 'report_date'}, set(res.columns)))
            dic_dtype = {col: np.integer for col in cols}
            res = res.astype(dtype=dic_dtype)
        except:
            pass

        if drop_dup_cols is not None:
            res = res.sort_values(by=drop_dup_cols, axis=0)
            res = res.drop_duplicates(subset=drop_dup_cols, keep='first')

        return res, err_msg

    def predefined_fields(self):
        params, msg = self.query("help.predefine", "", "")
        if msg != "0,":
            raise Exception(msg)
        mapper = {}
        for api, param in params[params.ptype == "OUT"][["api", "param"]].values:
            mapper.setdefault(api, set()).add(param)
        return mapper

    def query_index_member_daily(self, index, start_date, end_date):
        """
        Get index components on each day during start_date and end_date.

        Parameters
        ----------
        index : str
            separated by ','
        start_date : int
        end_date : int

        Returns
        -------
        res : pd.DataFrame
            index dates, columns all securities that have ever been components,
            values are 0 (not in) or 1 (in)

        """
        df_io, err_msg = self._get_index_comp(index, start_date, end_date)
        if err_msg != '0,':
            print(err_msg)

        def str2int(s):
            if isinstance(s, basestring):
                return int(s) if s else 99999999
            elif isinstance(s, (int, np.integer, float, np.float)):
                return s
            else:
                raise NotImplementedError("type s = {}".format(type(s)))

        df_io.loc[:, 'in_date'] = df_io.loc[:, 'in_date'].apply(str2int)
        df_io.loc[:, 'out_date'] = df_io.loc[:, 'out_date'].apply(str2int)

        # df_io.set_index('symbol', inplace=True)
        dates = self.query_trade_dates(start_date=start_date, end_date=end_date)

        dic = dict()
        gp = df_io.groupby(by='symbol')
        for sec, df in gp:
            mask = np.zeros_like(dates, dtype=np.integer)
            for idx, row in df.iterrows():
                bool_index = np.logical_and(dates >= row['in_date'], dates <= row['out_date'])
                mask[bool_index] = 1
            dic[sec] = mask

        res = pd.DataFrame(index=dates, data=dic)
        res.index.name = 'trade_date'

        return res


class LocalDataService(object):
    def __init__(self, fp=None):
        if fp:
            import sqlite3 as sql
            self.fp = os.path.abspath(fp)
            sql_path = os.path.join(fp, 'data.sqlite')

            if not os.path.exists(sql_path):
                raise FileNotFoundError("在{}目录下没有找到数据文件".format(fp))

            conn = sql.connect("file:%s?mode=ro" % sql_path, uri=True)
            self.conn = conn
            self.c = conn.cursor()

    def _get_attrs(self):
        dic = {}
        for root, dirs, files in os.walk(self.fp):
            name = root.split(self.fp)[-1][1:]
            for file_name in files:
                if file_name.endswith('.hd5'):
                    with h5py.File(os.path.join(root, (file_name, )), 'r') as file:
                        if 'meta' in file.attrs:
                            value = json.loads(file.attrs['meta'])
                            dic[name + '_' + file_name[:-4]] = value
                        else:
                            dic[name + '_' + file_name[:-4]] = None

        sql = '''select * from "attrs";'''
        data = pd.read_sql(sql, self.conn)
        dic.update(data.set_index(['view']).to_dict(orient='index'))
        return dic

    def _get_last_updated_date(self):
        lst = []
        for path, fields in self._walk_path().items():
            view = path
            for i in fields:
                with h5py.File(os.path.join(self.fp, path, "%s.hd5" % i), 'r') as file:
                    # noinspection PyBroadException
                    try:
                        lst.append({'view': view + '.' + i,
                                    'updated_date': int(file['date_flag'][-1][0])})
                    except Exception:
                        pass
        d1 = pd.DataFrame(lst)
        d1['freq'] = '1d'

        sql = '''select * from "attrs";'''
        d2 = pd.read_sql(sql, self.conn)
        return pd.concat([d1, d2])

    @staticmethod
    def _dic2url(d):
        l = ['='.join([key, str(value)]) for key, value in d.items()]
        return '&'.join(l)

    def predefined_fields(self):
        params, msg = self.query("help.predefine", "", "")
        if msg != "0,":
            raise Exception(msg)
        mapper = {}
        for api, param in params[params.ptype == "OUT"][["api", "param"]].values:
            mapper.setdefault(api, set()).add(param)

        keys = os.listdir(self.fp)
        [keys.remove(i) for i in os.listdir(self.fp)]
        updater = {k: set([i[:-4] for i in os.listdir(os.path.join(self.fp, k)) if i.endswith('hd5')]) for k in keys if os.path.isfile(k)}
        mapper.update(updater)
        return mapper

    @staticmethod
    def query_one(field, path, symbol=None, start_date=None, end_date=None):
        _dir = os.path.join(path, field + '.hd5')
        with h5py.File(_dir, 'r') as file:
            # noinspection PyBroadException
            try:
                dset = file['data']
                exist_symbol = file['symbol_flag'][:, 0].astype(str)
                exist_dates = file['date_flag'][:, 0].astype(np.int64)

            except Exception:
                raise ValueError('error hdf5 file')

            if not start_date:
                start_date = min(exist_dates)
            if not end_date:
                end_date = max(exist_dates)

            if not symbol:
                symbol = exist_symbol

            symbol_index = [i for i in range(len(exist_symbol)) if exist_symbol[i] in symbol]
            sorted_symbol = [exist_symbol[i] for i in symbol_index]
            start_index = bisect.bisect_left(exist_dates, start_date)
            end_index = bisect.bisect_left(exist_dates, end_date)

            try:
                data = dset[start_index:end_index, symbol_index]
            except Exception:
                raise NameError('不支持的symbol或date,请检查输入是否正确')
                
            _index = exist_dates[start_index:end_index]

            # try:
            #    data = data.astype(float)
            # except Exception:
            #    pass

            if data.dtype not in ['float', 'float32', 'float16', 'int']:
                data = data.astype(str)

            cols_multi = pd.MultiIndex.from_product([[field], sorted_symbol], names=['fields', 'symbol'])
            return pd.DataFrame(columns=cols_multi, index=_index, data=data)

    def bar_reader(self, path, props, resample_rules=None):
        '''
        :param props:
        配置项包括symbol, start_date, end_date , field, freq
        start_date/end_date : int   精确到秒 ，共14位数字
        symbol :str/list
        field  :  str/list
        freq  :  str/list
        配置项均可为空，代表读全部数据
        :param path:
        hdf5文件上一级目录
        :return:
        pandas.DataFrame
        多个freq返回
        '''
        symbol = props.get('symbol')
        fields = props.get('fields')
        start_date = props.get('start_date')
        end_date = props.get('end_date')
        freq = props.get('freq')

        if isinstance(fields, str):
            fields = fields.split(',')
        if isinstance(symbol, str):
            symbol = symbol.split(',')
        if isinstance(freq, str):
            freq = freq.split(',')

        try:
            exist_field = [i.split('.')[0] for i in os.listdir(path) if i.endswith('hd5')]
        except Exception:
            raise FileNotFoundError('指定路径下未找到数据文件，请检查输入路径是否正确')
            
        basic_field = ['datetime']
        if not fields or fields == ['']:
            fld = exist_field
        else:
            fields.extend(basic_field)
            fld = list(set(exist_field) & set(fields))
        df = pd.concat([self.query_one(f, path, start_date=start_date, end_date=end_date, symbol=symbol) for f in fld],
                       axis=1)

        df.index.name = 'trade_date'
        df = df.stack(-1, dropna=False).reset_index()

        def trans_time(d, _type):
            if d == 'None':
                return np.NaN
            else:
                if _type == 'datetime':
                    datetime(int(d[:4]), int(d[5:7]), int(d[8:10]), int(d[11:13]), int(d[14:16]), int(d[17:19]))
                    return datetime.strptime(d[:19], '%Y-%m-%d %H:%M:%S')
                elif _type == 'int':
                    return int(str(d)[:19].replace('-', '').replace(' ', '').replace(':', ''))
                elif _type == 'int_to_datetime':
                    return datetime.strptime(str(d), '%Y%m%d%H%M%S')

        df['datetime'] = [trans_time(i, 'datetime') for i in df['datetime']]
        df = df.set_index(['symbol', 'trade_date']).dropna(how='all').reset_index()
        df = df.sort_values(by=['symbol', 'trade_date'])
        # df['trade_date'] = df['trade_date'].astype(ctypes.c_int64)
        res = df

        if freq:
            df = df.set_index('datetime')
            if not resample_rules:
                resample_rules = {'high': 'max', 'open': 'first', 'close': 'last',
                                  'low': 'min', 'volume': 'sum', 'symbol': 'last',
                                  'Ignore': 'last', 'buy_base_volume': 'sum',
                                  'buy_quote_volume': 'sum', 'closetime': 'last',
                                  'date': 'last', 'datetime': 'first', 'exchange': 'last',
                                  'gatewayName': 'last', 'number_of_trades': 'sum',
                                  'openInterest': 'last', 'quote_volume': 'sum',
                                  'rawData': 'last', 'time': 'first', 'vtSymbol': 'last',
                                  'trade_date': 'first'}
            new_rules = {i: resample_rules[i] for i in df.columns.values}

            # df = df.set_index('datetime')
            res = {}
            for f in freq:
                if f == '1Min':
                    res[f] = df
                else:
                    df1 = df.groupby('symbol').resample(f).agg(new_rules).drop('symbol', axis=1).reset_index()
                    df1['trade_date'] = [trans_time(i, 'int') for i in df1['datetime']]
                    res[f] = df1

            if len(res.keys()) == 1:
                k, res = list(res.items())[0]
        return res

    def query(self, view, filter, fields, **kwargs):
        if view == 'attrs':
            return pd.DataFrame(self._get_attrs()).T

        if view == 'updated_date':
            return self._get_last_updated_date()

        self.c.execute('''select * from sqlite_master where type="table";''')
        sql_tables = [i[1] for i in self.c.fetchall()]
        
        if fields == '':
            fields = '*' 
        
        if view in sql_tables:
            self.c.execute('''PRAGMA table_info([%s])''' % (view, ))
            cols = [i[1] for i in self.c.fetchall()]
            date_names = [i for i in cols if 'date' in i]
            if 'ann_date' in date_names:
                date_name = 'ann_date'
            elif 'report_date' in date_names:
                date_name = 'report_date'
            elif len(date_names) == 0:
                date_name = None
            else:
                date_name = date_names[0]

            flt = filter.split('&')
            flt.sort()
            if flt[0] != '':
                k, v = flt[0].split('=')
                if 'start_date' in flt[0]:
                    condition = '''SELECT %s FROM "%s" WHERE %s >= "%s"''' % (fields, view, date_name, v)
                elif 'end_date' in flt[0]:
                    condition = '''SELECT %s FROM "%s" WHERE %s <= "%s"''' % (fields, view, date_name, v)
                else:
                    condition = '''SELECT %s FROM "%s" WHERE %s = "%s"''' % (fields, view, k, v)

                for i in flt[1:]:
                    k, v = i.split('=')
                    if k == 'start_date':
                        condition += ''' AND %s >= "%s"''' % (date_name, v)
                    elif k == 'end_date':
                        condition += ''' AND %s <= "%s"''' % (date_name, v)
                    elif k == 'symbol':
                        symbols = '("' + '","'.join(v.split(',')) + '")'
                        condition += ''' AND %s IN %s''' % (k, symbols)
                    else:
                        condition += ''' AND %s = "%s"''' % (k, v)
                condition = condition + ';'

            else:
                condition = '''SELECT %s FROM "%s";''' % (fields, view)

            data_format = kwargs.get('data_format')
            if not data_format:
                data_format = 'pandas'

            if data_format == 'list':
                data = [i[0] for i in self.c.fetchall()]
                return data, '0, '
            elif data_format == 'pandas':
                data = pd.read_sql(condition, self.conn)
                if 'ann_date' in data.columns:
                    data['ann_date'] = data['ann_date'].astype(float)
                return data, "0,"

        elif '.' not in view:
            dic = {}
            for i in filter.split('&'):
                k, v = i.split('=')
                dic[k] = v
            return self.daily(dic['symbol'], dic['start_date'], dic['end_date'], fields, adjust_mode=None, view=view)

    def query_trade_dates(self, start_date, end_date):
        sql = '''SELECT * FROM "jz.secTradeCal" 
                 WHERE trade_date>=%s 
                 AND trade_date<=%s ''' % (start_date, end_date)

        data = pd.read_sql(sql, self.conn)
        return data['trade_date'].values

    def query_index_member(self, universe, start_date, end_date,data_format='list'):
        sql = '''SELECT * FROM "lb.indexCons"
                 WHERE index_code = "%s" ''' % (universe, )

        data = pd.read_sql(sql, self.conn)

        symbols = [i for i in data['symbol'] if (i[0] == '0' or i[0] == '3' or i[0] == '6')]
        data = data[data['symbol'].isin(symbols)]

        data['out_date'][data['out_date'] == ''] = '20990101'
        data['in_date'] = data['in_date'].astype(int)
        data['out_date'] = data['out_date'].astype(int)
        data = data[(data['in_date'] <= end_date) & (data['out_date'] >= start_date)]
        if data_format == 'list':
            return list(set(data['symbol'].values))
        elif data_format == 'pandas':
            return data, "0,"

    def query_index_member_daily(self, index, start_date, end_date):
        """
        Get index components on each day during start_date and end_date.

        Parameters
        ----------
        index : str
            separated by ','
        start_date : int
        end_date : int

        Returns
        -------
        res : pd.DataFrame
            index dates, columns all securities that have ever been components,
            values are 0 (not in) or 1 (in)

        """
        df_io, err_msg = self.query_index_member(index, start_date, end_date, data_format='pandas')
        if err_msg != '0,':
            print(err_msg)

        def str2int(s):
            if isinstance(s, basestring):
                return int(s) if s else 99999999
            elif isinstance(s, (int, np.integer, float, np.float)):
                return s
            else:
                raise NotImplementedError("type s = {}".format(type(s)))
        df_io.loc[:, 'in_date'] = df_io.loc[:, 'in_date'].apply(str2int)
        df_io.loc[:, 'out_date'] = df_io.loc[:, 'out_date'].apply(str2int)

        # df_io.set_index('symbol', inplace=True)
        dates = self.query_trade_dates(start_date=start_date, end_date=end_date)

        dic = dict()
        gp = df_io.groupby(by='symbol')
        for sec, df in gp:
            mask = np.zeros_like(dates, dtype=np.integer)
            for idx, row in df.iterrows():
                bool_index = np.logical_and(dates >= row['in_date'], dates <= row['out_date'])
                mask[bool_index] = 1
            dic[sec] = mask

        res = pd.DataFrame(index=dates, data=dic)
        res.index.name = 'trade_date'

        return res

    def query_lb_fin_stat(self, type_, symbol, start_date, end_date, fields, drop_dup_cols=False, report_type='408001000'):
        view_map = {'income': 'lb.income', 'cash_flow': 'lb.cashFlow', 'balance_sheet': 'lb.balanceSheet',
                    'fin_indicator': 'lb.finIndicator'}
        view_name = view_map.get(type_, None)
        if view_name is None:
            raise NotImplementedError("type_ = {:s}".format(type_))

        symbols = '("' + '","'.join(symbol.split(',')) + '")'

        if fields == "":
            fld = '*'
        else:
            fld = fields
            for i in ['report_date', 'symbol', 'ann_date']:
                if i not in fld:
                    fld += ',%s' % (i, )

        if view_name == 'lb.finIndicator':
            sql = '''SELECT %s FROM "%s" 
              WHERE ann_date>=%s 
              AND ann_date<=%s 
              AND symbol IN %s ''' % (fld, view_name, start_date, end_date, symbols)

        else:
            sql = '''SELECT %s FROM "%s" 
              WHERE ann_date>=%s 
              AND ann_date<=%s 
              AND symbol IN %s 
              AND report_type = "%s"''' % (fld, view_name, start_date, end_date, symbols, report_type)

        try:
            data = pd.read_sql(sql, self.conn)
        except Exception as e:
            raise SqlError('%s data not found' % (view_name,), e)

        if drop_dup_cols:
            data = data.drop_duplicates()
        data['ann_date'] = data['ann_date'].replace('', np.NaN).astype(float)
        return data, "0,"

    def query_inst_info(self, symbol, fields, inst_type=""):
        symbol = symbol.split(',')
        symbols = '("' + '","'.join(symbol) + '")'
        
        self.c.execute('PRAGMA table_info([jz.instrumentInfo])')
        cols = [i[1] for i in self.c.fetchall()]
        if 'setlot' not in cols:
            fields = fields.replace('setlot', 'selllot')
        
        if inst_type == "":
            inst_type = "1"
        
        self.c.execute('''SELECT %s FROM "jz.instrumentInfo"
                      WHERE symbol IN %s 
                     AND inst_type = "%s"''' % (fields, symbols, inst_type))
        data = pd.DataFrame([list(i) for i in self.c.fetchall()], columns=fields.split(','))
        return data.set_index('symbol')   
    
    def query_lb_dailyindicator(self, symbol, start_date, end_date, fields=""):
        return self.daily(symbol, start_date, end_date, fields=fields, view='SecDailyIndicator')

    def query_adj_factor_daily(self, symbol, start_date, end_date, div=False):
        """
        Get index components on each day during start_date and end_date.

        Parameters
        ----------
        symbol : str
            separated by ','
        start_date : int
        end_date : int
        div : bool
            False for normal adjust factor, True for diff.

        Returns
        -------
        res : pd.DataFrame
            index dates, columns symbols
            values are industry code

        """
        _flt = 'symbol=%s&start_date=%s&end_date=%s' % (symbol, start_date, end_date)

        # noinspection PyBroadException
        try:
            df_raw, msg = self.query('lb.secAdjFactor', _flt, '')
        except Exception:
            print('query adjust_factor from Stock_D')
            return self.query_adj_factor_daily_2(symbol, start_date, end_date)

        dic_sec = jutil.group_df_to_dict(df_raw, by='symbol')
        dic_sec = {sec: df.set_index('trade_date').loc[:, 'adjust_factor']
                   for sec, df in dic_sec.items()}

        # TODO: duplicate codes with dataview.py: line 512
        res = pd.concat(dic_sec, axis=1)  # TODO: fillna ?

        idx = np.unique(np.concatenate([df.index.values for df in dic_sec.values()]))
        symbol_arr = np.sort(symbol.split(','))
        res_final = pd.DataFrame(index=idx, columns=symbol_arr, data=np.nan)
        res_final.loc[res.index, res.columns] = res

        # align to every trade date
        s, e = df_raw.loc[:, 'trade_date'].min(), df_raw.loc[:, 'trade_date'].max()
        dates_arr = self.query_trade_dates(s, e)
        if not len(dates_arr) == len(res_final.index):
            res_final = res_final.reindex(dates_arr)

            res_final = res_final.fillna(method='ffill').fillna(method='bfill')

        if div:
            res_final = res_final.div(res_final.shift(1, axis=0)).fillna(1.0)

        # res = res.loc[start_date: end_date, :]
        res_final.index = res_final.index.astype(int)

        return res_final

    def query_adj_factor_daily_2(self, symbol_str, start_date, end_date, div=False):
        data, msg = self.daily(symbol_str, start_date, end_date, fields='adjust_factor')
        data = data.loc[:, ['trade_date', 'symbol', 'adjust_factor']]
        data = data.drop_duplicates()
        data = data.pivot_table(index='trade_date', columns='symbol', values='adjust_factor', aggfunc=np.mean)
        if div:
            pass
        return data

    def query_index_weights_range(self, universe, start_date, end_date):
        """
        Return all securities that have been in universe during start_date and end_date.
        
        Parameters
        ----------
        universe : str
            separated by ','
        start_date : int
        end_date : int

        Returns
        -------
        pd.DataFrame
        """
        universe = universe.split(',')
        if '000300.SH' in universe:
            universe.remove('000300.SH')
            universe.append('399300.SZ')
            
        if len(universe) == 1:
            universe = universe[0] 
            sql = '''SELECT * FROM "lb.indexWeightRange"
                      WHERE trade_date>=%s 
                      AND trade_date<=%s 
                      AND index_code = "%s" '''%(start_date, end_date, universe)
        else:
            universe = '("' + '","'.join(universe) + '")'
            sql = '''SELECT * FROM "lb.indexWeightRange"
                      WHERE trade_date>=%s 
                      AND trade_date<=%s 
                      AND index_code IN %s ''' % (start_date, end_date, universe)
            
        data = pd.read_sql(sql, self.conn).drop_duplicates()
        
        if len(data) > 0:
            # df_io = df_io.set_index('symbol')
            df_io = data.astype({'weight': float, 'trade_date': np.integer})
            df_io.loc[:, 'weight'] = df_io['weight'] / 100.
            df_io = df_io.pivot(index='trade_date', columns='symbol', values='weight')
            df_io = df_io.fillna(0.0)
            return df_io
        else:
            print('没有找到指数%s的权重数据' % self.universe)
            return data

    def query_index_weights_daily(self, index, start_date, end_date):
        """
        Return all securities that have been in index during start_date and end_date.
        
        Parameters
        ----------
        index : str
        start_date : int
        end_date : int

        Returns
        -------
        res : pd.DataFrame
            Index is trade_date, columns are symbols.

        """
        start_dt = jutil.convert_int_to_datetime(start_date)
        start_dt_extended = start_dt - pd.Timedelta(days=45)
        start_date_extended = jutil.convert_datetime_to_int(start_dt_extended)
        trade_dates = self.query_trade_dates(start_date_extended, end_date)
        
        df_weight_raw = self.query_index_weights_range(index, start_date=start_date_extended, end_date=end_date)
        res = df_weight_raw.reindex(index=trade_dates)
        res = res.fillna(method='ffill')
        res = res.loc[res.index >= start_date]
        res = res.loc[res.index <= end_date]
        
        mask_col = res.sum(axis=0) > 0
        return res
        res = res.loc[:, mask_col]

    def _walk_path(self, path=None):
        res = {}
        if not path:
            path = self.fp
        path = path[:-1] if path.endswith(os.path.sep) else path
        for a, b, c in os.walk(path):
            dr = a.replace(path, "")
            dr = dr[1:] if dr.startswith(os.path.sep) else dr
            depth = len(dr.split(os.path.sep))
            if not dr or depth != 1:
                continue
            lst = []
            for i in c:
                if '.hd5' in i:
                    lst.append(i[:-4].split(os.path.sep)[-1])
            res[dr] = lst
        return res

    def daily(self, symbol, start_date, end_date,
              fields="", adjust_mode=None, view='Stock_D'):

        if isinstance(fields, str):
            fields = fields.split(',')
        if isinstance(symbol, str):
            symbol = symbol.split(',')

        file_info = self._walk_path()
        exist_views = []
        for path, exists in file_info.items():
            if set(fields) & set(exists) == set(fields) and len(fields) > 0:
                exist_views.append(path)
        
        if "Stock_D" in set(exist_views):
            view = "Stock_D"
        elif exist_views:
            view = exist_views[0]

        if fields in [[''], []]:
            fields = file_info[view]
        exist_field = file_info[view]

        fields.remove('trade_date') if 'trade_date' in fields else None
        fields.remove('symbol') if 'symbol' in fields else None

        if view == 'Stock_D':
            basic_field = ['freq']
        else:
            basic_field = []
            adjust_mode = None

        fields = list(set(fields + basic_field))
        fld = list(set(exist_field) & set(fields))
        
        need_dates = self.query_trade_dates(start_date, end_date)
        start = need_dates[0]
        end = need_dates[-1]

        if adjust_mode:
            fld = list(set(fld + ['adjust_factor']))

        def query_by_field(field):
            _dir = os.path.join(self.fp, view, field + '.hd5')
            with h5py.File(_dir, 'r') as file:
                # noinspection PyBroadException
                try:
                    dset = file['data']
                    exist_symbol = file['symbol_flag'][:, 0].astype(str)
                    exist_dates = file['date_flag'][:, 0].astype(int)
                except Exception:
                    raise DataNotFoundError('empty hdf5 file')

                if start not in exist_dates or end not in exist_dates:
                    raise ValueError('起止日期超限')

                _symbol = [x for x in symbol if x in exist_symbol]
                symbol_index = [np.where(exist_symbol == i)[0][0] for i in _symbol]
                symbol_index.sort()
                sorted_symbol = [exist_symbol[i] for i in symbol_index]

                start_index = np.where(exist_dates == start)[0][0]
                end_index = np.where(exist_dates == end)[0][0] + 1

                if len(symbol_index) == 0:
                    return None

                data = dset[start_index:end_index, symbol_index]
                _index = exist_dates[start_index:end_index]

                if data.dtype not in ['float', 'float32', 'float16', 'int']:
                    data = data.astype(str)
                if field == 'trade_date' and data.dtype in ['float', 'float32', 'float16']:
                    data = data.astype(float).astype(int)
                cols_multi = pd.MultiIndex.from_product([[field], sorted_symbol], names=['fields', 'symbol'])
                return pd.DataFrame(columns=cols_multi, index=_index, data=data)
        df = pd.concat([query_by_field(f) for f in fld], axis=1)
        df.index.name = 'trade_date'
        df = df.stack(dropna=False).reset_index()
        if adjust_mode == 'post':
            if 'adjust_factor' not in df.columns:
                df['adjust_factor'] = 1

            for f in list(set(df.columns) & set(['open', 'high', 'low', 'close', 'vwap'])):
                df[f] = df[f]*df['adjust_factor']
            df = df.dropna()

        if adjust_mode == 'pre':
            if 'adjust_factor' not in df.columns:
                df['adjust_factor'] = 1

            for f in list(set(df.columns) & set(['open', 'high', 'low', 'close', 'vwap'])):
                df[f] = df[f]/df['adjust_factor']
            df = df.dropna()

        if ('adjust_factor' not in fields) and adjust_mode:
            df = df.drop(['adjust_factor'], axis=1)

        if len(set(df['symbol'])) == 1:
            df = df.set_index('trade_date').loc[need_dates, :].reset_index()
            df['symbol'] = df['symbol'].fillna(method='bfill')

        df = df.dropna(how='all')
        df = df[df['trade_date'] > 0]
        df = df.reset_index(drop=True)
        return df.sort_values(by=['symbol', 'trade_date']), "0,"
    
    def query_industry_raw(self, symbol_str, type_='ZZ', level=1):
        """
        Get daily industry of securities from ShenWanZhiShu or ZhongZhengZhiShu.
        
        Parameters
        ----------
        symbol_str : str
            separated by ','
        type_ : {'SW', 'ZZ'}
        level : {1, 2, 3, 4}
            Use which level of industry index classification.

        Returns
        -------
        df : pd.DataFrame

        """
        if type_ == 'SW':
            src = 'sw'
            if level not in [1, 2, 3, 4]:
                raise ValueError("For [SW], level must be one of {1, 2, 3, 4}")
        elif type_ == 'ZZ':
            src = 'zz'
            if level not in [1, 2, 3, 4]:
                raise ValueError("For [ZZ], level must be one of {1, 2}")
        else:
            raise ValueError("type_ must be one of SW of ZZ")
        
        symbol = symbol_str.split(',')
        symbols = '("' + '","'.join(symbol) + '")'
        sql = '''SELECT * FROM "lb.secIndustry"
                 WHERE symbol IN %s
                 AND industry_src == "%s" ''' % (symbols, src)

        df = pd.read_sql(sql, self.conn)
        df = df.astype(dtype={'in_date': np.integer,
                              # 'out_date': np.integer
                              })
        return df.drop_duplicates()

    def query_industry_daily(self, symbol, start_date, end_date, type_='SW', level=1):
        """
        Get index components on each day during start_date and end_date.
        
        Parameters
        ----------
        symbol : str
            separated by ','
        start_date : int
        end_date : int
        type_ : {'SW', 'ZZ'}

        Returns
        -------
        res : pd.DataFrame
            index dates, columns symbols
            values are industry code

        """
        def group_df_to_dict(df, by):
            gp = df.groupby(by=by)
            res = {key: value for key, value in gp}
            return res
        
        df_raw = self.query_industry_raw(symbol, type_=type_, level=level)
        
        dic_sec = group_df_to_dict(df_raw, by='symbol')
        dic_sec = {sec: df.sort_values(by='in_date', axis=0).reset_index()
                   for sec, df in dic_sec.items()}

        df_ann_tmp = pd.concat({sec: df.loc[:, 'in_date'] for sec, df in dic_sec.items()}, axis=1)
        df_value_tmp = pd.concat({sec: df.loc[:, 'industry{:d}_name'.format(level)]
                                  for sec, df in dic_sec.items()},
                                 axis=1)
        
        idx = np.unique(np.concatenate([df.index.values for df in dic_sec.values()]))
        symbol_arr = np.sort(symbol.split(','))
        df_ann = pd.DataFrame(index=idx, columns=symbol_arr, data=np.nan)
        df_ann.loc[df_ann_tmp.index, df_ann_tmp.columns] = df_ann_tmp
        df_value = pd.DataFrame(index=idx, columns=symbol_arr, data=np.nan)
        df_value.loc[df_value_tmp.index, df_value_tmp.columns] = df_value_tmp

        dates_arr = self.query_trade_dates(start_date, end_date)
        
        df_industry = align(df_value, df_ann, dates_arr)
        
        # TODO before industry classification is available, we assume they belong to their first group.
        df_industry = df_industry.fillna(method='bfill')
        df_industry = df_industry.astype(str)
        
        return df_industry

    def query_dividend(self, symbol, start_date, end_date):
        filter_argument = self._dic2url({'symbol': symbol,
                                         'start_date': start_date,
                                         'end_date': end_date})
        df, err_msg = self.query(view="lb.secDividend",
                                 fields="",
                                 filter=filter_argument,
                                 data_format='pandas')

        '''
        # df = df.set_index('exdiv_date').sort_index(axis=0)
        df = df.astype({'cash': float, 'cash_tax': float,
                        # 'bonus_list_date': np.integer,
                        # 'cashpay_date': np.integer,
                        'exdiv_date': np.integer,
                        'publish_date': np.integer,
                        'record_date': np.integer})
        '''
        return df, err_msg
