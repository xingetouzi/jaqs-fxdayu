from jaqs.data.py_expression_eval import *
from jaqs.data.py_expression_eval import Parser as OriginParser

from jaqs_fxdayu.patch_util import auto_register_patch
from jaqs_fxdayu.util import fillinf
from . import signal_function_mod as sfm


@auto_register_patch(parent_level=1)
class Parser(OriginParser):
    def __init__(self):
        super(Parser, self).__init__()
        self.functions.update({
            'Ta': self.ta,
            'Ts_Argmax': self.ts_argmax,
            'Ts_Argmin': self.ts_argmin
        })

    def evaluate(self, values, ann_dts=None, trade_dts=None, index_member=None):
        """
        Evaluate the value of expression using. Data of different frequency will be automatically expanded.

        Parameters
        ----------
        values : dict
            Key is variable name, value is pd.DataFrame (index is date, column is symbol)
        ann_dts : pd.DataFrame
            Announcement dates of financial statements of securities.
        trade_dts : np.ndarray
            The date index of result.
        index_member : pd.DataFrame

        Returns
        -------
        pd.DataFrame

        """

        def _fillinf(df):
            try:
                df = fillinf(df)
            except:
                pass
            return df

        self.ann_dts = ann_dts
        self.trade_dts = trade_dts
        self.index_member = index_member

        values = values or {}
        nstack = []
        L = len(self.tokens)
        for i in range(0, L):
            item = self.tokens[i]
            type_ = item.type_
            if type_ == TNUMBER:
                nstack.append(item.number_)
            elif type_ == TOP2:
                n2 = nstack.pop()
                n1 = nstack.pop()
                f = self.ops2[item.index_]
                nstack.append(_fillinf(f(n1, n2)))
            elif type_ == TVAR:
                if item.index_ in values:
                    nstack.append(_fillinf(values[item.index_]))
                elif item.index_ in self.functions:
                    nstack.append(self.functions[item.index_])
                else:
                    raise Exception('undefined variable: ' + item.index_)
            elif type_ == TOP1:
                n1 = nstack.pop()
                f = self.ops1[item.index_]
                nstack.append(_fillinf(f(n1)))
            elif type_ == TFUNCALL:
                n1 = nstack.pop()
                f = nstack.pop()
                if callable(f):
                    if type(n1) is list:
                        nstack.append(_fillinf(f(*n1)))
                    else:
                        nstack.append(_fillinf(f(n1)))  # call(f, n1)
                else:
                    raise Exception(f + ' is not a function')
            else:
                raise Exception('invalid Expression')
        if len(nstack) > 1:
            raise Exception('invalid Expression (parity)')
        return _fillinf(nstack[0])

    # -----------------------------------------------------
    # functions
    # ta function
    def ta(self,
           ta_method,
           ta_column,
           Open,
           High,
           Low,
           Close,
           Volume,
           *args,
           **kwargs):
        return sfm.ta(ta_method,
                      ta_column,
                      Open,
                      High,
                      Low,
                      Close,
                      Volume,
                      *args,
                      **kwargs)

    def ts_argmax(self, *args,
                  **kwargs):
        return sfm.ts_argmax(*args, **kwargs)

    def ts_argmin(self, *args,
                  **kwargs):
        return sfm.ts_argmin(*args, **kwargs)

    def std_dev(self, df, n):
        return df.rolling(n).std()

    def ts_sum(self, df, n):
        return df.rolling(n).sum()

    def count_nans(self, df, n):
        return n - df.rolling(n).count()

    def ts_mean(self, df, n):
        return df.rolling(n).mean()

    def ts_min(self, df, n):
        return df.rolling(n).min()

    def ts_max(self, df, n):
        return df.rolling(n).max()

    def ts_kurt(self, df, n):
        return df.rolling(n).kurt()

    def ts_skew(self, df, n):
        return df.rolling(n).skew()

    def ts_product(self, df, n):
        return df.rolling(n).apply(np.product)

    def corr(self, x, y, n):
        (x, y) = self._align_bivariate(x, y)
        return x.rolling(n).corr(y)

    def cov(self, x, y, n):
        (x, y) = self._align_bivariate(x, y)
        return x.rolling(n).cov(y)

    def decay_linear(self, x, n):
        return x.rolling(n).apply(self.decay_linear_array)

    def decay_exp(self, x, f, n):
        return x.rolling(n).apply(self.decay_exp_array, args=[f])


