
import unittest

from datab.db_manager import *
from datab.mongo import *
from common.utils import Util

class DbManagerTestCase(unittest.TestCase):

    class TestDriver(BaseDriver):
        def __init__(self, dr_id):
            self._id = dr_id

        def echo(self, val):
            return self._id + val

    def setUp(self):
        # DbManager is a singletone and thus only one instance will be created
        self.dbm = DbManager()

    def test_add(self):
        self.assertEqual(len(self.dbm), 0, "DB Manager not empty")
        res = Util.safe_call(self.dbm.add_driver, 0, DbManagerTestCase.TestDriver(0))
        self.assertTrue(not isinstance(res, Exception), "Exception adding driver: %s" % res)
        self.assertEqual(len(self.dbm), 1, "DB Manager is still empty")

    def test_add_fail(self):
        res = Util.safe_call(self.dbm.add_driver, 1, {})
        self.assertTrue(isinstance(res, DbException), "Expected exception when adding invalid driver, got %s" % res)
        # check that we can't insert driver with existing id
        res = Util.safe_call(self.dbm.add_driver, 0, DbManagerTestCase.TestDriver(0))
        self.assertTrue(isinstance(res, DbException), "Expected exception, but got %s" % res)
        self.assertEqual(len(self.dbm), 1, "DB manager size changed")

    def test_cmd_one(self):
        test_val = 5
        res = Util.safe_call(self.dbm.cmd_one, 0, lambda db: db.echo(test_val))
        self.assertTrue(not isinstance(res, Exception), "Exception calling method: %s" % res)
        self.assertEqual(res, test_val, "Got %s, expected %d" % (res, test_val))

    def test_cmd_all(self):
        res = Util.safe_call(self.dbm.add_driver, 1, DbManagerTestCase.TestDriver(1))
        self.assertTrue(not isinstance(res, Exception), "Exception adding new driver: %s" % res)
        arg = 1
        exp_vals = range(arg, len(self.dbm) + arg)
        res = Util.safe_call(self.dbm.cmd_all, lambda db: db.echo(arg))
        self.assertTrue(not isinstance(res, Exception), "Exception: %s" % res)
        self.assertTrue(not Util.list_diff(res, exp_vals), "Got %s, expected %s" % (res, exp_vals))

class MongoTestCase(unittest.TestCase):

    class MongoClientMock():
        
        class DbMock():
            def __init__(self):
                self._sz = 0
            def __getitem__(self, _):
                return self
            def insert_one(self, _):
                self._sz += 1
            def insert_many(self, iter):
                self._sz += len(list(iter))
            def count(self):
                return self._sz

        def __init__(self):
            self._db = {}

        def __getitem__(self, name):
            if not self._db.get(name):
                self._db[name] = MongoTestCase.MongoClientMock.DbMock()
            return self._db[name]

        #def __setitem__(self, name, val):
        #    self._db[name] = val

    def setUp(self):
        self.modb = Mongo()
        self.modb._client = MongoTestCase.MongoClientMock()

    def test_add(self):
        db_name = 'test'
        res = Util.safe_call(self.modb.add_db, db_name)
        self.assertTrue(not isinstance(res, Exception), "Exception adding database: %s" % res)
        # try adding DB with same name again
        res = Util.safe_call(self.modb.add_db, db_name)
        self.assertTrue(isinstance(res, DbException), "Didn't get exception adding same DB name twice")
        # try accessing database that wasn't added        
        try:
            self.modb.active_db = 'test1'
        except Exception as e:
            self.assertTrue(isinstance(e, DbException), "Expected DB error, but got %s" % e)
        else:
            self.assertTrue(False)

        self.modb.active_db = db_name
        cnt = self.modb.active_db.count()
        self.assertEqual(cnt, 1, "Expected 1 table, got %d" % cnt)

    def test_fill_random(self):
        db_name = 'test'
        self.modb.add_db(db_name)
        self.modb.active_db = db_name

        exp_cnt = 5
        test_temp = {'name': (str, ['n1', 'n2']), 'ival': (int, (0, 10)), 'fval': (float, (0, 100)), 'bval': (bool, ())}
        res = Util.safe_call(self.modb.fill_random, 'check', test_temp, exp_cnt)
        self.assertTrue(not isinstance(res, DbException), "Exception filling DB: %s" % res)
        self.assertTrue(res)

        cnt = self.modb.active_db['check'].count()
        self.assertEqual(cnt, exp_cnt + 1, "Expected %d entries, got %d" % (exp_cnt + 1, cnt))


if __name__ == '__main__':  
    unittest.main()
