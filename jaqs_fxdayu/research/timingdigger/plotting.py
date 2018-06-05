from jaqs_fxdayu.research.signaldigger.plotting import *


def plot_event_table(event_summary_table):
    print("Event Analysis")
    plot_table(event_summary_table.apply(lambda x: x.round(3)).T)