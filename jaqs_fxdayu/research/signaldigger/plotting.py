from jaqs_fxdayu.patch_util import auto_register_patch
from jaqs.research.signaldigger.plotting import *


@auto_register_patch()
def plot_ic_by_group(ic_group, ax=None):
    """
    Plots Spearman Rank Information Coefficient for a given
    factor over provided forward returns.
    Separates by group.

    Parameters
    ----------
    ic_group : pd.DataFrame
        group-wise mean period wise returns.
    ax : matplotlib.Axes, optional
        Axes upon which to plot.

    Returns
    -------
    ax : matplotlib.Axes
        The axes that were plotted on.
    """
    if ax is None:
        f, ax = plt.subplots(1, 1, figsize=(18, 6))
    ic_group.plot(kind='bar', ax=ax)

    ax.set(title="Information Coefficient By Group", xlabel="")
    ax.set_xticklabels(ic_group.index, rotation=45)

    return ax
