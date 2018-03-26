from os.path import join, dirname

import matplotlib
import matplotlib.pyplot  # 防止被JAQS重载

from .patch_util import patch_all

with open(join(dirname(__file__), 'VERSION.txt'), 'rb') as f:
    __version__ = f.read().decode('ascii').strip()
