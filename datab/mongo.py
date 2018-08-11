
import os
import pymongo
import numpy as np

from datetime import datetime

from datab.db_manager import *

def init_check(func):
    def wrap(*args, **kwargs):
        if not args[0]._client:
            raise DbException("Not initialized")
        return func(*args, **kwargs)
    return wrap

class Mongo(BaseDriver):
    """
    Provides some high level logic over MongoDB.
    """

    def __init__(self):
        self._client = None
        self._dbs = []
        self._active_db = None

    def init(self):
        try:
            self._client = pymongo.MongoClient('mongodb://localhost:27017/')
        except Exception as e:
            raise DbException("Failed to connect to mongodb server: %s" % e)

    @init_check
    def add_db(self, name):
        """
        Add database and initialize it.
        """
        if (name in self._dbs):
            raise DbException("DB %s already exists")

        db = self._client[name]
        db_init_data = {'user':    os.getlogin(),
                        'created': datetime.utcnow()}
        db.insert_one(db_init_data)
        self._dbs.append(name)

    @property
    @init_check
    def active_db(self):
        return self._client[self._active_db]

    @active_db.setter
    def active_db(self, value):
        if (value not in self._dbs):
            raise DbException("DB %s doesn't exist" % value)
        self._active_db = value

    @init_check
    def fill_random(self, name, data_template, size):
        """
        Fill it random data based on a simple template.

                {'field_1': (type, metdata), ...}

        Type can be int, float or str. Metadata depends on type and is used as a guideline for generating
        random entries and should adhere to the following rules:

                int     -> (min_value, max_value)
                float   -> (min_value, range)
                str     -> (list of all possible string values)     
        """
        def get_random_set(dtype, meta):
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

        if not self._active_db:
            raise DbException("Set active DB first")

        keys = list(data_template.keys())
        # randomly generated vectors are zipped together and map function is used to build a dict object
        gen_data = list(map(lambda _: {keys[i]:data[i] for i in range(len(keys)) 
                                        for data in zip(*(get_random_set(v[0], v[1]) if v else None for v in data_template.values()))
                                      }, 
                            range(size))
                        )

        res = self.active_db[name].insert_many(gen_data)
        return (len(gen_data) == len(res.inserted_ids))

if __name__ == '__main__':
    dbm = Mongo()
    dbm.add_db('test')
    dbm.active_db = 'test'

    claim_temp = {'name': (str, ['Jon','Ola','Kari','Bente']), 'age': (int, (18, 75)), 'income_knok': (float, (100, 1000)),
                  'auto_handler': None, 'check_needed': (bool, ())}
    if not dbm.fill_in_random('claims', claim_temp, 10):
        print("Failed to fill in database")

