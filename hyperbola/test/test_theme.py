from twisted.trial.unittest import TestCase

from xmantissa.test.test_theme import testHead
from hyperbola.hyperbola_theme import HyperbolaTheme

class HyperbolaThemeTestCase(TestCase):
    def test_head(self):
        testHead(HyperbolaTheme(''))
