"""
Test that the Hyperbola view classes can be rendered
"""
from xml.dom import minidom

from twisted.trial.unittest import TestCase
from twisted.internet import defer

from xmantissa import ixmantissa, webtheme

from nevow.testutil import renderLivePage, FragmentWrapper, AccumulatingFakeRequest

from hyperbola import hyperblurb, hyperbola_view
from hyperbola.test.util import HyperbolaTestMixin


class RenderingTestCase(TestCase, HyperbolaTestMixin):
    """
    Test that the Hyperbola view classes can be rendered
    """
    def setUp(self):
        self._setUpStore()

    def _renderFragment(self, fragment, *a, **k):
        """
        Render the fragment C{fragment}

        @rtype: L{twisted.internet.defer.Deferred} firing with string
        rendering result
        """
        fragment.docFactory = webtheme.getLoader(fragment.fragmentName)
        return renderLivePage(FragmentWrapper(fragment), *a, **k)

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

    def test_blurbViewDetailDispatch(self):
        """
        Test that we can pass a blurb of any flavor to
        L{hyperbola.hyperbola_view.blurbViewDetailDispatcher} and then render
        the result
        """
        deferreds = list()
        for parentFlavor in hyperblurb.ALL_FLAVORS:
            childFlavor = hyperblurb.FLAVOR.commentFlavors[parentFlavor]

            parent = self._makeBlurb(parentFlavor)
            child = self._makeBlurb(childFlavor)
            child.parent = parent

            childProxy = self._shareAndGetProxy(child)
            deferreds.append(self._renderFragment(
                hyperbola_view.blurbViewDetailDispatcher(childProxy)))
        return defer.gatherResults(deferreds)

    def test_blogPostDetailRendering(self):
        """
        Test that we can pass a blog post blurb to
        L{hyperbola.hyperbola_view.blurbViewDetailDispatcher} and that the
        rendered result contains the title and body of the parent
        """
        child = self._makeBlurb(hyperblurb.FLAVOR.BLOG_POST)
        child.parent = self._makeBlurb(
            hyperblurb.FLAVOR.BLOG, title=u'Parent Title', body=u'Parent Body')

        childProxy = self._shareAndGetProxy(child)
        D = self._renderFragment(
            hyperbola_view.blurbViewDetailDispatcher(childProxy))

        def rendered(xml):
            elements = {}
            doc = minidom.parseString(xml)
            for elt in doc.getElementsByTagName('*'):
                cls = elt.getAttribute('class')
                if not cls:
                    continue
                if cls not in elements:
                    elements[cls] = []
                elements[cls].append(elt)

            self.assertEquals(
                len(elements['hyperbola-blog-main-title']), 1)
            self.assertEquals(
                elements['hyperbola-blog-main-title'][0].firstChild.nodeValue,
                'Parent Title')
            self.assertEquals(
                len(elements['hyperbola-blog-sub-title']), 1)
            self.assertEquals(
                elements['hyperbola-blog-sub-title'][0].firstChild.nodeValue,
                'Parent Body')

        D.addCallback(rendered)
        return D

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

    def test_addCommentDialogDispatch(self):
        """
        Test that we can pass a blurb of any flavor to
        L{hyperbola.hyperbola_view.addCommentDialogDispatcher} and then render
        the result
        """
        class RequestWithArgs(AccumulatingFakeRequest):
            def __init__(self, *a, **k):
                AccumulatingFakeRequest.__init__(self, *a, **k)
                self.args = {'title': [''], 'body': [''], 'url': ['']}

        deferreds = list()
        for flavor in hyperblurb.ALL_FLAVORS:
            proxy = self._shareAndGetProxy(self._makeBlurb(flavor))
            deferreds.append(self._renderFragment(
                hyperbola_view.addCommentDialogDispatcher(
                    hyperbola_view.blurbViewDispatcher(proxy)),
                reqFactory=RequestWithArgs))
        return defer.gatherResults(deferreds)
