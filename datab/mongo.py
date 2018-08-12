
import os
import pymongo

from pandas import DataFrame

from datab.db_manager import *
from common.utils import Util

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

    def __del__(self):
        if self._client:
            try:
                self._client.drop_database(self._active_db)
                self._client.close()
            except:
                pass

    @init_check
    def add_db(self, name):
        """
        Add database and initialize it.
        """
        if (name in self._dbs):
            raise DbException("DB %s already exists")

        db = self._client[name]
        db_init_data = {'user':    os.getlogin(),
                        'created': Util.datetime()}
        db['init'].insert_one(db_init_data)
        self._dbs.append(name)

    @property
    @init_check
    def active_db(self):
        if not self._active_db:
            raise DbException("Set active DB first")
        return self._client[self._active_db]

    @active_db.setter
    def active_db(self, value):
        if (value not in self._dbs):
            raise DbException("DB %s doesn't exist" % value)
        self._active_db = value

    @init_check
    def fill_random(self, table_name, data_template, size):
        """
        Fill it random data based on a simple template.

                {'field_1': (type, metdata), ...}

        Type can be int, float or str. Metadata depends on type and is used as a guideline for generating
        random entries and should adhere to the following rules:

                int     -> (min_value, max_value)
                float   -> (min_value, range)
                str     -> (list of all possible string values)     
        """
        keys = list(data_template.keys())
        # randomly generated vectors are zipped together and map function is used to build a dict object
        gen_data = list(map(lambda _: {keys[i]:data[i] for i in range(len(keys)) 
                                        for data in zip(*(Util.get_random_set(v[0], v[1], size) if v else None for v in data_template.values()))
                                      }, 
                            range(size))
                        )

        res = self.active_db[table_name].insert_many(gen_data)
        return (len(gen_data) == len(res.inserted_ids)) if res else False

    @init_check
    def read(self, table_name, keys=None, filt=None):
        query_res = self.active_db[table_name].find(filt, keys)
        if not query_res:
            return DataFrame()

        if not keys:
            keys = list(query_res[0].keys())
            keys.remove('_id')

        data = {k:[] for k in keys}
        for doc in query_res:
            [data[k].append(doc[k]) for k in keys]
        query_res.close()
        return DataFrame(data)
