import pandas as pd
from pandas.core.internals import BlockManager, BlockPlacement
import numpy as np


def block_concat(dfs, idx, columns):
    manager = BlockManager(iter_blocks(dfs), [columns, idx])
    return pd.DataFrame(manager).copy()


def iter_blocks(dfs):
    l = 0
    for df in dfs:
        for block in df._data.blocks:
            # yield Block(block.values, block._mgr_locs.add(l))
            yield block.__class__(block.values, placement=block._mgr_locs.add(l))
        l += len(df.columns)


def quick_concat(dfs, level, index_name="trade_date", how="outer"):
    columns = join_columns(dfs, level)
    if how == "outer":
        index = join_indexes([df.index for df in dfs], index_name)
    else:
        index = intersect1d_indexes([df.index for df in dfs], index_name)
    return block_concat(
        [pd.DataFrame(df, index) for df in dfs],
        index, columns
    )


def join_indexes(idxes, name=None):
    return pd.Index(np.concatenate([index.values for index in idxes]), name=name).sort_values().drop_duplicates()


def intersect1d_indexes(idxes, name=None):
    return pd.Index(intersect1d(idxes), name=name).sort_values().drop_duplicates()


def intersect1d(idxes):
    if len(idxes) == 2:
        return np.intersect1d(*idxes)
    elif len(idxes) > 2:
        return np.intersect1d(intersect1d(idxes[:-1]), idxes[-1])



def join_columns(dfs, level=None):
    return pd.MultiIndex.from_tuples(np.concatenate([df.columns.values for df in dfs]), names=level)