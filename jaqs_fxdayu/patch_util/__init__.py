import importlib
import logging
import warnings
import sys
from collections import defaultdict

from jaqs_fxdayu.patch_util.postimport import when_imported

_patch_hooks = defaultdict(list)
_module = "jaqs"
_patched = False

logger = logging.getLogger(__name__)


def register_patch(fullname=_module):
    def decorator(func):
        if _patched:
            raise RuntimeWarning("Patch %s is registered after jaqs_fxdayu.patch method be called." % func)
        _patch_hooks[fullname].append(func)
        return func

    return decorator


def reload_jaqs():
    reload_lst = []
    for m in list(sys.modules.keys()):
        if m.startswith("jaqs."):
            del sys.modules[m]
            reload_lst.append(m)
    for m in reload_lst:
        importlib.import_module(m)


def patch_all():
    import matplotlib
    import matplotlib.pyplot
    global _patched
    if _patched:
        warnings.warn("jaqs_fxdayu.patch method should be called only once!")
        return
    importlib.import_module("jaqs_fxdayu.data")
    importlib.import_module("jaqs_fxdayu.research.signaldigger")
    for fullname, hooks in _patch_hooks.items():
        for func in hooks:
            when_imported(fullname)(func)
    _patched = True
    logger.debug("Finish Patch.")


def auto_register_patch(fullname=None, name=None, parent_level=0):
    def decorator(obj):
        def _patch_module(m):
            attr = obj.__name__ if name is None else name
            logger.debug("Patch %s:%s ." % (m.__name__, attr))
            setattr(m, attr, obj)

        module_name = obj.__module__.replace("jaqs_fxdayu", "jaqs") if fullname is None else fullname
        module_path = module_name.split(".") + [""]
        for level in range(parent_level + 1):
            register_patch(".".join(module_path[:-(level + 1)]))(_patch_module)
        return obj

    return decorator
