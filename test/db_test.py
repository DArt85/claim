
import unittest

from datab.db_manager import *
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

    def test_cmd_one(self):
        test_val = 5
        res = Util.safe_call(self.dbm.cmd_one, 0, lambda db: db.echo(test_val))
        self.assertTrue(not isinstance(res, Exception), "Exception calling method: %s" % res)
        self.assertEqual(res, test_val, "Got %s, expected %d" % (res, test_val))

    def test_cmd_all(self):
        res = Util.safe_call(self.dbm.add_driver, 1, DbManagerTestCase.TestDriver(1))
        self.assertTrue(not isinstance(res, Exception), "Exception adding new driver: %s" % res)
        arg = 1
        exp_vals = set(range(arg, len(self.dbm) + arg))
        res = Util.safe_call(self.dbm.cmd_all, lambda db: db.echo(arg))
        self.assertTrue(not isinstance(res, Exception), "Exception: %s" % res)
        self.assertTrue(not (set(res) ^ exp_vals), "Got %s, expected %s" % (res, exp_vals))

if __name__ == '__main__':
    unittest.main()
