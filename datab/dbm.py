
import os
import pymongo
import numpy as np

from datetime import datetime

class DbManager():
    """
    Proxy-like class providing some high level logic over MongoDB.
    """

    class DbException(Exception):
        def __init__(self, msg):
            super().__init__(msg)

    def __init__(self):
        self._client = pymongo.MongoClient('mongodb://localhost:27017/')
        self._dbs = []
        self._active_db = None

    def add_db(self, name):
        """
        Add database and initialize it.
        """
        if (name in self._dbs):
            raise DbException("DB %s already exists")

        db = self._client[name]
        db_init_data = {'user':    os.getlogin(),
                        'created': datetime.utcnow()}
        db.init.insert_one(db_init_data)
        self._dbs.append(name)

    @property
    def active_db(self):
        return self._client[self._active_db]
        return None

    @active_db.setter
    def active_db(self, value):
        if (value not in self._dbs):
            raise DbException("DB %s doesn't exist" % value)
        self._active_db = value

    def fill_in_random(self, name, data_template, size):
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
            if (dtype == int):
                (minv, maxv) = meta
                data_set = [int(i) for i in np.random.randint(minv, maxv, size)]
            elif (dtype == float):
                (minv, delta) = meta
                data_set = [minv + x * delta for x in np.random.ranf(size)]
            elif (dtype == str):
                maxv = len(meta) - 1
                data_set = [meta[i] for i in np.random.random_integers(0, maxv, size)]
            return data_set

        if not self._active_db:
            raise DbException("Set active DB first")

        keys = list(data_template.keys())
        # randomly generated vectors are zipped together and map function is used to build a dict object
        gen_data = list(map(lambda _: {keys[i]:data[i] for i in range(len(keys)) 
                                        for data in zip(*(get_random_set(v[0], v[1]) for v in data_template.values()))
                                      }, 
                            range(size))
                        )

        res = self.active_db[name].insert_many(gen_data)
        return (len(gen_data) == len(res.inserted_ids))

if __name__ == '__main__':
    dbm = DbManager()
    dbm.add_db('test')
    dbm.active_db = 'test'

    claim_temp = {'name': (str, ['Jon','Ola','Kari','Bente']), 'age': (int, (18, 75)), 'income_knok': (float, (100, 1000))}
    if not dbm.fill_in_random('claims', claim_temp, 10):
        print("Failed to fill in database")

