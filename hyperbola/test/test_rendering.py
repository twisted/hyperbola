"""
Test that the Hyperbola view classes can be rendered
"""
from twisted.trial.unittest import TestCase
from twisted.internet import defer

from xmantissa import ixmantissa, webtheme

from nevow.testutil import renderLivePage, FragmentWrapper

from hyperbola import hyperblurb, hyperbola_view
from hyperbola.test.util import HyperbolaTestMixin


class RenderingTestCase(TestCase, HyperbolaTestMixin):
    """
    Test that the Hyperbola view classes can be rendered
    """
    def setUp(self):
        self._setUpStore()

    def _renderFragment(self, fragment):
        """
        Render the fragment C{fragment}

        @rtype: L{twisted.internet.defer.Deferred} firing with string
        rendering result
        """
        fragment.docFactory = webtheme.getLoader(fragment.fragmentName)
        return renderLivePage(FragmentWrapper(fragment))

    def test_adaption(self):
        """
        Test that we can adapt a blurb of any flavor to
        L{xmantissa.ixmantissa.INavigableFragment} and then render the result
        """
        deferreds = list()
        for flavor in hyperblurb.ALL_FLAVORS:
            proxy = self._shareAndGetProxy(self._makeBlurb(flavor))
            deferreds.append(self._renderFragment(
                ixmantissa.INavigableFragment(proxy)))
        return defer.gatherResults(deferreds)

    def test_blurbViewDispatch(self):
        """
        Test that we can pass a blurb of any flavor to
        L{hyperbola.hyperbola_view.blurbViewDispatcher} and then render the
        result
        """
        deferreds = list()
        for flavor in hyperblurb.ALL_FLAVORS:
            proxy = self._shareAndGetProxy(self._makeBlurb(flavor))
            deferreds.append(self._renderFragment(
                hyperbola_view.blurbViewDispatcher(proxy)))
        return defer.gatherResults(deferreds)

    def test_addCommentDispatch(self):
        """
        Test that we can pass a blurb of any flavor to
        L{hyperbola.hyperbola_view.addCommentDispatcher} and then render the
        result
        """
        deferreds = list()
        for flavor in hyperblurb.ALL_FLAVORS:
            proxy = self._shareAndGetProxy(self._makeBlurb(flavor))
            deferreds.append(self._renderFragment(
                hyperbola_view.addCommentDispatcher(
                    hyperbola_view.blurbViewDispatcher(proxy))))
        return defer.gatherResults(deferreds)
