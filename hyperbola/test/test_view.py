"""
Tests for Hyperbola view logic
"""
from xml.dom import minidom

from twisted.trial.unittest import TestCase

from hyperbola import hyperbola_view, hyperblurb
from hyperbola.test.util import HyperbolaTestMixin

from nevow.testutil import FragmentWrapper, renderLivePage
from nevow import loaders, tags
from nevow.flat import flatten

class ViewTestCase(TestCase, HyperbolaTestMixin):
    """
    Tests for Hyperbola view logic
    """
    def setUp(self):
        self._setUpStore()

    def test_addComment(self):
        """
        Test adding a comment to a blurb of each flavor through
        L{hyperbola.hyperbola_view.addCommentDispatcher}
        """
        for flavor in hyperblurb.ALL_FLAVORS:
            share = self._shareAndGetProxy(self._makeBlurb(flavor))

            parent = hyperbola_view.blurbViewDispatcher(share)
            parent.customizeFor(self.role.externalID)

            frag = hyperbola_view.addCommentDispatcher(parent)
            frag.addComment(u'title', u'body!', ())

            (comment,) = share.view(self.role)
            self.assertEquals(comment.title, 'title')
            self.assertEquals(comment.body, 'body!')
            self.assertEquals(list(comment.tags()), [])

    def test_addCommentWithTags(self):
        """
        Same as L{test_addComment}, but specify some tags to be applied to the
        comment
        """
        for flavor in hyperblurb.ALL_FLAVORS:
            share = self._shareAndGetProxy(self._makeBlurb(flavor))

            parent = hyperbola_view.blurbViewDispatcher(share)
            parent.customizeFor(self.role.externalID)

            frag = hyperbola_view.addCommentDispatcher(parent)
            frag.addComment(u'title', u'body!', (u't', u'a', u'gs'))

            (comment,) = share.view(self.role)
            self.assertEquals(set(comment.tags()), set(('t', 'a', 'gs')))

    def test_blurbPostingResourceCustomized(self):
        """
        Test that the L{hyperbola.hyperbola_view.BlurbPostingResource} is
        customized so that the blurb that is created will have the correct
        author
        """
        blog = self._shareAndGetProxy(
            self._makeBlurb(hyperblurb.FLAVOR.BLOG))

        bpr = hyperbola_view.BlurbPostingResource(
            self.store, blog, self.role.externalID)

        bpr.fragment.addComment(u'', u'', ())

        (comment,) = blog.view(self.role)
        self.assertEquals(comment.author, self.role)

    def test_parseTagsExtraneousWhitespace(self):
        """
        Test that L{hyperbola.hyperbola_view.parseTags}
        removes any whitespace surrounding the tags it is passed
        """
        self.assertEquals(
            hyperbola_view.parseTags(' a , b,c,d,  '), ['a', 'b', 'c', 'd'])

    def test_parseTagsAllWhitespace(self):
        """
        Test that L{hyperbola.hyperbola_view.AddCommentFragment.parseTags}
        returns the empty list when given a string of whitespace
        """
        self.assertEquals(
            hyperbola_view.parseTags('  '), [])

    def test_htmlifyLineBreaks(self):
        """
        Test that L{hyperbola.hyperbola_view.BlurbViewer._htmlifyLineBreaks}
        replaces new lines with <br> elements
        """
        share = self._shareAndGetProxy(
            self._makeBlurb(
                hyperblurb.FLAVOR.BLOG_POST,
                body=u'foo\nbar\r\nbaz'))

        frag = hyperbola_view.blurbViewDispatcher(share)
        self.assertEquals(
            flatten(frag._htmlifyLineBreaks(frag.original.body)),
            'foo<br />bar<br />baz<br />')

    def test_htmlBlurbBody(self):
        """
        Test that we can set and retrieve a blurb body containing HTML through
        the view APIs
        """
        share = self._shareAndGetProxy(
            self._makeBlurb(
                hyperblurb.FLAVOR.BLOG))

        parent = hyperbola_view.blurbViewDispatcher(share)
        parent.customizeFor(self.role.externalID)

        commenter = hyperbola_view.addCommentDispatcher(parent)
        commenter.addComment(u'title', u'<div>body</div>', ())

        (post,) = share.view(self.role)
        postFragment = hyperbola_view.blurbViewDispatcher(post)

        postFragment.docFactory = loaders.stan(tags.directive('body'))
        def gotHTML(html):
            doc = minidom.parseString(html)
            divs = doc.getElementsByTagName('div')
            self.assertEquals(len(divs), 1)
            self.assertEquals(divs[0].firstChild.nodeValue, 'body')
        D = renderLivePage(FragmentWrapper(postFragment))
        D.addCallback(gotHTML)
        return D
