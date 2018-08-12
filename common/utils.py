
import numpy as np

class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls,*args,**kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance

class Util():

    @staticmethod
    def safe_call(func, *args):
        try:
            res = func(*args)
        except Exception as e:
            res = e
        return res

    @staticmethod
    def get_random_set(dtype, meta, size):
        data_set = []
        if (dtype == bool):
            data_set = [(i > 0) for i in np.random.randint(0, 2, size)]
        elif (dtype == int):
            (minv, maxv) = meta
            data_set = [int(i) for i in np.random.randint(minv, maxv + 1, size)]
        elif (dtype == float):
            (minv, delta) = meta
            data_set = [minv + x * delta for x in np.random.ranf(size)]
        elif (dtype == str):
            maxv = len(meta) - 1
            data_set = [meta[i] for i in np.random.randint(0, maxv + 1, size)]
        return data_set

    @staticmethod
    def list_diff(list1, list2):
        return list(set(list1) ^ set(list2))
