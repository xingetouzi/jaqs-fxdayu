from .patch_util import patch_all

import matplotlib
import matplotlib.pyplot  # 防止被JAQS重载

with open(join(dirname(__file__), 'jaqs_fxdayu', 'VERSION.txt'), 'rb') as f:
    __version__ = f.read().decode('ascii').strip()
