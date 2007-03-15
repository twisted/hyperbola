"""
Tests for Hyperbola view logic
"""
from twisted.trial.unittest import TestCase

from hyperbola import hyperbola_view, hyperblurb
from hyperbola.test.util import HyperbolaTestMixin

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
        Test that L{hyperbola.hyperbola_view.AddCommentFragment.parseTags}
        removes any whitespace surrounding the tags it is passed
        """
        share = self._shareAndGetProxy(
            self._makeBlurb(hyperblurb.FLAVOR.BLOG))

        parent = hyperbola_view.blurbViewDispatcher(share)
        parent.customizeFor(self.role.externalID)

        frag = hyperbola_view.AddCommentFragment(parent)
        self.assertEquals(
            frag.parseTags(' a , b,c,d,  '), ['a', 'b', 'c', 'd'])

    def test_parseTagsAllWhitespace(self):
        """
        Test that L{hyperbola.hyperbola_view.AddCommentFragment.parseTags}
        returns the empty list when given a string of whitespace
        """
        share = self._shareAndGetProxy(
            self._makeBlurb(hyperblurb.FLAVOR.BLOG))

        parent = hyperbola_view.blurbViewDispatcher(share)
        parent.customizeFor(self.role.externalID)

        frag = hyperbola_view.AddCommentFragment(parent)
        self.assertEquals(
            frag.parseTags('  '), [])
