
from common.utils import Singleton

class DbException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class BaseDriver():
    def init(self):
        raise NotImplementedError("init")

    def add_db(self, name):
        raise NotImplementedError("add_db")

    def fill_random(self, name, data_template, size):
        raise NotImplementedError("fill_random")

class DbManager(metaclass=Singleton):

    def __init__(self):
        self._dbs = {}

    def __len__(self):
        return len(self._dbs)

    def add_driver(self, db_id, driver):
        if self._dbs.get(db_id):
            raise DbException("Driver with ID = %s already exists" % db_id)
        if not issubclass(type(driver), BaseDriver):
            raise DbException("Invalid DB driver type: %s" % type(driver))
        self._dbs[db_id] = driver

    def cmd_one(self, db_id, clojure):
        db = self._dbs.get(db_id)
        if not db:
            raise DbException("No DB with id = %s" % db_id)
        return clojure(db)

    def cmd_all(self, clojure):
        res = []
        for db in self._dbs.values():
            res.append(clojure(db))
        return res
