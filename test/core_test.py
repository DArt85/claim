
import unittest

from common.utils import *
from core.handlers import *
from core.manager import *

class CoreTestCase(unittest.TestCase):

    def setUp(self):
        self.mgr = ModelManager()

    def test_add(self):
        res = Util.safe_call(self.mgr.set_default, BasicClaimHandler)
        self.assertTrue(isinstance(res, ModelException), "Model was set before been added")
        res = Util.safe_call(self.mgr.set_default, AbstractClaimHandler)
        self.assertTrue(isinstance(res, ModelException), "Abstract model shouldn't be allowed")

        res = Util.safe_call(self.mgr.add, BasicClaimHandler())
        self.assertTrue(not isinstance(res, ModelException), "failed to add model: %s" % res)
        res = Util.safe_call(self.mgr.add, BasicClaimHandler())
        self.assertTrue(isinstance(res, ModelException), "adding same model twice is not allowed: %s" % res)
        self.assertEqual(len(self.mgr), 1, "Wrong model count")

    def test_default(self):
        self.mgr.add(ChallengerClaimHandler(25, 250))
        res = Util.safe_call(self.mgr.set_default, BasicClaimHandler)
        self.assertTrue(not isinstance(res, ModelException))

    def test_classify_claims(self):
        pass
