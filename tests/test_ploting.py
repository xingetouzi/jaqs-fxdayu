import matplotlib as mpl

_old = mpl.get_backend()

from jaqs_fxdayu.data import DataView

assert mpl.get_backend() == _old

import importlib
importlib.reload(mpl)

from jaqs_fxdayu import patch_all

patch_all()
assert mpl.get_backend() == _old
