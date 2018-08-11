
from claim.datab.mongo import Mongo
from common.utils import Singleton

class DbException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class DbBase():
    def add_db(self, name):
        raise NotImplementedError("add_db")

    def fill_random(self, name, data_template, size):
        raise NotImplementedError("fill_random")

class DbManager(metaclass=Singleton):

    def __init__(self):
        self._dbs = {}

    def cmd_one(self, db_id, clojure):
        db = self._dbs.get(db_id)
        if not db:
            raise DbException("No DB with id = %s" % db_id)
        clojure(db)

    def cmd_all(self, clojure):
        for db in self._dbs.values():
            clojure(db)
