from jaqs.data.py_expression_eval import Parser as OriginParser

from jaqs_fxdayu.patch_util import auto_register_patch
from . import signal_function_mod as sfm


@auto_register_patch(parent_level=1)
class Parser(OriginParser):
    def __init__(self):
        super(Parser, self).__init__()
        self.functions.update({
            'Ta': self.ta,
            'Ts_Argmax': self.ts_argmax,
            'Ts_Argmin': self.ts_argmin,
        })

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
