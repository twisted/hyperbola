from axiom.store import Store

from twisted.trial import unittest
from hyperbola import hyperbola_model

class BasicTest(unittest.TestCase):
    def setUp(self):
        self.store = Store()

    def testUserWroteTests(self):
        o = hyperbola_model.HyperbolaPublicPresence(
            store=self.store)

    def tearDown(self):
        self.store.close()

