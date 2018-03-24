# encoding: utf-8
from jaqs_fxdayu import patch_all
patch_all()

from jaqs.data.dataview import DataView
from jaqs.data import RemoteDataService
from tests.data_config import data_config


def test_hs300_dataview():
    ds = RemoteDataService()

    ds.init_from_config(data_config)
    dv = DataView()
    print(DataView)
    start = 20180104
    end = 20180320
    props = {'start_date': start, 'end_date': end, 'universe': '000300.SH',
             "prepare_fields": True,
             'fields': 'DDNBT,close,pe_ttm,ps_ttm,pb,pcf_ocfttm,ebit,roe,roa,price_div_dps',
             'freq': 1}

    dv.init_from_config(props, ds)
    dv.prepare_data()
    print(dv.get_ts("DDNBT").head())
    print(dv.fields)
    dv.add_field("CMRA")
    print(dv.get_ts("CMRA").head())
    print(dv.fields)


def test_gem_dataview():
    ds = RemoteDataService()

    ds.init_from_config(data_config)
    dv = DataView()
    start = 20180104
    end = 20180320
    props = {'start_date': start, 'end_date': end, 'universe': '399606.SZ',
             "prepare_fields": True,
             'fields': 'pe_ttm,ps_ttm,pb,pcf_ocfttm,ebit,roe,roa,price_div_dps',
             'freq': 1}

    dv.init_from_config(props, ds)
    dv.prepare_data()
    print(dv.get_ts("DDNBT").head())
    print(dv.fields)
    dv.add_field("CMRA")
    print(dv.get_ts("CMRA").head())
    print(dv.fields)


if __name__ == "__main__":
    test_hs300_dataview()
    test_gem_dataview()
