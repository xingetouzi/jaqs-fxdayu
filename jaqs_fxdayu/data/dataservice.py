# noinspection PyUnresolvedReferences
from jaqs.data.dataservice import *

import os
import bcolz
import numpy as np
import pandas as pd
import sqlite3 as sql
from jaqs.data.align import align
import jaqs.util as jutil

class LocalDataService():
    def __init__(self,fp):
        conn = sql.connect(fp + '//' + 'data.sqlite')
        self.c = conn.cursor()
        self.tb = bcolz.open(fp + '//' + 'data_d')

    def _raise_error_if_no_file(self,path):
        if not os.path.exists(path):
            raise FileNotFoundError("File not found at {}".format(path))

#------------------------q-----------------------------------
    def query(self, view, filter, fields, data_format='pandas'):
        #"help.apiParam", "api=factor&ptype=OUT", "param"
        self.c.execute('select * from sqlite_master where type="table";')
        sql_tables = [i[1] for i in self.c.fetchall()]
        
        if view in sql_tables:
            flt = filter.split('&')
            if flt[0] != '':  
                k,v = flt[0].split('=')
                if 'start_date' in flt[0]:
                    condition = '''SELECT %s FROM "%s" WHERE trade_date >= "%s"'''%(fields ,view, v)
                elif 'end_date' in flt[0]:
                    condition = '''SELECT %s FROM "%s" WHERE trade_date <= "%s"'''%(fields ,view, v)
                else:
                    condition = '''SELECT %s FROM "%s" WHERE %s = "%s"'''%(fields ,view, k, v)
                
                for i in flt[1:]:
                    k,v = i.split('=')
                    if k == 'start_date':
                        condition += ''' AND trade_date >= "%s"'''%(v)
                    elif k == 'end_date':
                        condition += ''' AND trade_date <= "%s"'''%(v) 
                    else:
                        condition += ''' AND %s = "%s"'''%(k,v)
                condition = condition + ';'
            
            else:
                condition = '''SELECT %s FROM "%s";'''%(fields ,view)
                
            self.c.execute(condition)
            
            if data_format == 'list':
                data = [i[0] for i in self.c.fetchall()]
                return  data , '0, '
            elif data_format == 'pandas':
                data = pd.DataFrame([i for i in self.c.fetchall()],columns = fields.split(','))
                return data , "0,"
          
        elif view == 'factor':      
            dic = {}
            for i in filter.split('&'):
                k,v = i.split('=')
                dic[k] = v
            return self.daily(dic['symbol'], dic['start'],dic['end'],fields, adjust_mode=None) 
     
    def query_trade_dates(self,start_date, end_date):
        self.c.execute('''SELECT * FROM "jz.secTradeCal" 
                      WHERE trade_date>=%s 
                      AND trade_date<=%s '''%(start_date,end_date))

        data = pd.DataFrame([list(i) for i in self.c.fetchall()])
        
        self.c.execute('PRAGMA table_info([jz.secTradeCal])')
        cols = [i[1] for i in self.c.fetchall()]
        data.columns = cols
        return data['trade_date'].values
        
    
    
    def query_index_member(self, universe, start_date, end_date,data_format='list'):
        self.c.execute('''SELECT * FROM "lb.indexCons"
                          WHERE index_code == "%s" '''%(universe))
        
        data = pd.DataFrame([list(i) for i in self.c.fetchall()])
        
        self.c.execute('PRAGMA table_info([lb.indexCons])')
        cols = [i[1] for i in self.c.fetchall()]
        data.columns = cols
        
        data['out_date'][data['out_date'] == ''] = '20990101'
        data['in_date'] = data['in_date'].astype(int)
        data['out_date'] = data['out_date'].astype(int)
        data = data[(data['in_date'] <= end_date)&(data['out_date'] >= start_date)]
        if data_format == 'list':
            return data['symbol'].values
        elif data_format == 'pandas':
            return data , "0,"
 
    
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
        df_io, err_msg = self.query_index_member(index, start_date, end_date ,data_format='pandas')
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
                bool_index = np.logical_and(dates > row['in_date'], dates < row['out_date'])
                mask[bool_index] = 1
            dic[sec] = mask
            
        res = pd.DataFrame(index=dates, data=dic)
        res.index.name = 'trade_date'
        
        return res
    
    def query_lb_fin_stat(self, type_, symbol, start_date, end_date, field, drop_dup_cols):
        #fld = ','.join(set(field) - set(drop_dup_cols))
        view_map = {'income': 'lb.income', 'cash_flow': 'lb.cashFlow', 'balance_sheet': 'lb.balanceSheet',
                    'fin_indicator': 'lb.finIndicator'}
        view_name = view_map.get(type_, None)
        if view_name is None:
            raise NotImplementedError("type_ = {:s}".format(type_))
        
        fld = field
        symbols =  '("' + '","'.join(symbol.split(',')) + '")'
        report_type = '408001000'
        
        if view_name == 'lb.finIndicator':
            self.c.execute('''SELECT %s FROM "%s" 
              WHERE report_date>=%s 
              AND report_date<=%s 
              AND symbol IN %s '''%(fld ,view_name ,start_date ,end_date ,symbols))
            
        else:
            self.c.execute('''SELECT %s FROM "%s" 
              WHERE report_date>=%s 
              AND report_date<=%s 
              AND symbol IN %s 
              AND report_type = "%s"'''%(fld ,view_name ,start_date ,end_date ,symbols ,report_type))

        data = pd.DataFrame([list(i) for i in self.c.fetchall()],columns = fld.split(','))
        return data , "0,"
 
    
    def query_inst_info(self ,symbol, fields, inst_type=""):
        symbol = symbol.split(',')
        symbols =  '("' + '","'.join(symbol) + '")'
        
        self.c.execute('PRAGMA table_info([jz.instrumentInfo])')
        cols = [i[1] for i in self.c.fetchall()]
        if 'setlot' not in cols:
            fields = fields.replace('setlot','selllot')
        
        if inst_type == "":
            inst_type = "1"
        
        self.c.execute('''SELECT %s FROM "jz.instrumentInfo"
                      WHERE symbol IN %s 
                     AND inst_type = "%s"'''%(fields ,symbols ,inst_type))
        data = pd.DataFrame([list(i) for i in self.c.fetchall()],columns = fields.split(','))
        return data.set_index('symbol')   
    
    def query_lb_dailyindicator(self, symbol, start_date, end_date, fields=""):
        special_fields = set(['pb','pe','ps'])
        field = fields.split(',')
        sf = list(set(field)&special_fields)
        
        dic = {}
        if sf:      
            bz_sf = [i + '_' for i in sf]
            for i in range(len(sf)):
               field.remove(sf[i])
               field.append(bz_sf[i])
               dic[bz_sf[i]] = sf[i]
               
            df , msg = self.daily(symbol, start_date, end_date,fields = field)
            df = df.rename(dic,axis=1)
            return df ,msg
        else:    
            return self.daily(symbol, start_date, end_date,fields = fields)

    def query_adj_factor_daily(self, symbol_str, start_date, end_date, div=False):
        return self.daily(symbol_str, start_date, end_date,fields = 'adjust_factor')


    def query_index_weights_range(self, index, start_date, end_date):
        """
        Return all securities that have been in index during start_date and end_date.
        
        Parameters
        ----------
        index : str
            separated by ','
        trade_date : int

        Returns
        -------
        pd.DataFrame

        """
        index = index.split(',')
        if '000300.SH' in index:
            index.remove('000300.SH')
            index.append('399300.SZ')
            
        if len(index) == 1:
            index = index[0] 
            self.c.execute('''SELECT * FROM "lb.indexWeightRange"
                      WHERE trade_date>=%s 
                      AND trade_date<=%s 
                      AND index_code = "%s" '''%(start_date ,end_date, index))          
        else:
            index =  '("' + '","'.join(index.split(',')) + '")'
            self.c.execute('''SELECT * FROM "lb.indexWeightRange"
                      WHERE trade_date>=%s 
                      AND trade_date<=%s 
                      AND index_code IN %s '''%(start_date ,end_date, index))
            
        data = pd.DataFrame([list(i) for i in self.c.fetchall()])
        
        self.c.execute('PRAGMA table_info([lb.indexWeightRange])')
        cols = [i[1] for i in self.c.fetchall()]
        data.columns = cols     
        
        # df_io = df_io.set_index('symbol')
        df_io = data.astype({'weight': float, 'trade_date': np.integer})
        df_io.loc[:, 'weight'] = df_io['weight'] / 100.
        df_io = df_io.pivot(index='trade_date', columns='symbol', values='weight')
        df_io = df_io.fillna(0.0)
        return df_io


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
        res = res.loc[:, mask_col]
        
        return res

    def index_daily(self, universe, start_date, end_date, fields):

        self.c.execute('''SELECT %s FROM "index_d"
                          WHERE trade_date>=%s 
                          AND trade_date<=%s 
                          AND symbol = "%s" '''%(fields ,start_date ,end_date, universe[0]))
        data = pd.DataFrame([list(i) for i in self.c.fetchall()],columns = fields.split(','))        
        
        return data , "0,"


    def daily(self, symbol, start_date, end_date,
              fields="", adjust_mode=None):
        
        if type(symbol) == str:
            symbol = symbol.split(',')    
        
        if type(fields) == str:
            fields = fields.split(',')
            
        symbols = [x for x in symbol if x in self.tb.attrs['index'].keys()]
        fld = [x for x in fields if x in self.tb.cols.names] + ['trade_date','symbol']
        
        need_dates = self.query_trade_dates(start_date, end_date)
        start = need_dates[0]
        end = need_dates[-1]
        
        if symbols == []:
            return self.index_daily(symbol, start_date, end_date , ','.join(fields))
        
        if adjust_mode == 'post':
            fld.extend(['open_adj', 'high_adj', 'low_adj', 'close_adj'])
            fld = list(set(fld) - set(['open','high','low','close']))

        index = self.tb.attrs['index']
        dates = np.array(list(set(self.tb['trade_date'])))
        dates.sort()
        _s = np.argwhere(dates == start)[0][0]
        _e = np.argwhere(dates == end)[0][0]
        
        def func(df,symbol):
            s,e = index[symbol].split(',')
            begin = int(s) + _s
            finish = int(s) + _e + 1
            return df[begin:finish]
            
        res = {}
        for f in fld:
            df = self.tb[f]
            res[f] = np.concatenate([func(df,sb) for sb in symbols])                             

        return pd.DataFrame(res) , "0,"
    
    
    def query_industry_raw(self, symbol_str, type_='ZZ', level=1):
        """
        Get daily industry of securities from ShenWanZhiShu or ZhongZhengZhiShu.
        
        Parameters
        ----------
        symbol : str
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
        symbols =  '("' + '","'.join(symbol) + '")'
        self.c.execute('''SELECT * FROM "lb.secIndustry"
                          WHERE symbol IN %s
                          AND industry_src == "%s" '''%(symbols, src))
        
        
        df = pd.DataFrame([list(i) for i in self.c.fetchall()]) 
        
        self.c.execute('PRAGMA table_info([lb.secIndustry])')
        cols = [i[1] for i in self.c.fetchall()]
        df.columns = cols
        
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
        df_value_tmp = pd.concat({sec: df.loc[:, 'industry{:d}_code'.format(level)]
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
        