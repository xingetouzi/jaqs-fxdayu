# encoding=utf-8
from pathlib import Path

import pandas as pd

_path = Path(__file__).absolute().parent / "built_in_funcs_docs.csv"


def get_doc():
    f = open(str(_path),"rb")
    data = pd.read_csv(f)
    return data


class FuncDoc(object):
    def __init__(self):
        self.doc = get_doc()
        self.types = self.doc["分类"].drop_duplicates().values
        self.funcs = self.doc["公式"].values
        self.descriptions = self.doc["说明"].values

    def search_by_type(self, _type):
        result = self.doc["分类"].apply(lambda x: x.find(_type) > -1)
        return self.doc[result]

    def search_by_func(self, func, precise=False):
        if precise:
            result = self.doc["公式"].apply(lambda x: x.find(func) == 0)
        else:
            result = self.doc["公式"].apply(lambda x: x.lower().find(func.lower()) > -1)
        return self.doc[result]

    def search_by_description(self, description):
        result = self.doc["说明"].apply(lambda x: x.find(description) > -1)
        return self.doc[result]


if __name__ == "__main__":
    print(get_doc().to_dict)
