import unittest


class TestPatchAll(unittest.TestCase):
    prefix = "jaqs_fxdayu."

    @classmethod
    def setUpClass(cls):
        from jaqs_fxdayu import patch_all
        patch_all()

    def test_dataview(self):
        from jaqs.data import DataView
        assert DataView.__module__.startswith(self.prefix)
        from jaqs.data.dataview import DataView
        assert DataView.__module__.startswith(self.prefix)

    def test_parser(self):
        from jaqs.data import Parser
        assert Parser.__module__.startswith(self.prefix)
        from jaqs.data.py_expression_eval import Parser
        assert Parser.__module__.startswith(self.prefix)

    def test_signaldigger(self):
        from jaqs.research import SignalDigger
        assert SignalDigger.__module__.startswith(self.prefix)
        from jaqs.research.signaldigger import SignalDigger
        assert SignalDigger.__module__.startswith(self.prefix)

    def test_performance(self):
        from jaqs.research.signaldigger import performance
        assert performance.calc_signal_ic.__module__.startswith(self.prefix)
        assert performance.calc_quantile_return_mean_std.__module__.startswith(self.prefix)
        assert performance.mean_information_coefficient.__module__.startswith(self.prefix)
        assert performance.price2ret.__module__.startswith(self.prefix)

    def test_plotting(self):
        from jaqs.research.signaldigger import plotting
        assert hasattr(plotting, "plot_ic_by_group")


if __name__ == "__main__":
    unittest.main()
