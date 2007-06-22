"""
Tests for Hyperbola view logic
"""
from xml.dom import minidom

from zope.interface import directlyProvides

from twisted.trial.unittest import TestCase

from nevow import context, tags

from axiom.store import Store

from xmantissa.webtheme import getLoader
from xmantissa import sharing
from xmantissa.sharing import SharedProxy
from xmantissa.publicweb import LoginPage
from xmantissa.ixmantissa import IStaticShellContent

from hyperbola import hyperbola_view, hyperblurb, ihyperbola
from hyperbola.hyperblurb import FLAVOR
from hyperbola.hyperbola_view import BlurbViewer
from hyperbola.ihyperbola import IViewable
from hyperbola.test.util import HyperbolaTestMixin

from nevow.testutil import FakeRequest, FragmentWrapper, renderLivePage
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


    def test_bodyRenderer(self):
        """
        L{BlurbViewer.render_body} should return a well-formed XHTML document
        fragment even if the body of the blurb being rendered is not
        well-formed.
        """
        body = u'<i>hello'
        expectedBody = u'<i>hello</i><br />'
        view = BlurbViewer(self._makeBlurb(hyperblurb.FLAVOR.BLOG, None, body))
        result = flatten(view.render_body(None, None))
        self.assertEqual(result, expectedBody)


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


    def test_blogTags(self):
        """
        Test that the implementation of C{_getAllTags} on the view for a blog
        post returns all tags that have been applied to blurbs, without
        duplicates
        """
        postShare = self._shareAndGetProxy(
            self._makeBlurb(hyperblurb.FLAVOR.BLOG_POST))
        postShare.tag(u'foo')

        otherPostShare = self._shareAndGetProxy(
            self._makeBlurb(hyperblurb.FLAVOR.BLOG_POST))
        otherPostShare.tag(u'foo')
        otherPostShare.tag(u'bar')

        blogShare = self._shareAndGetProxy(
            self._makeBlurb(hyperblurb.FLAVOR.BLOG))
        blogView = hyperbola_view.blurbViewDispatcher(blogShare)

        self.assertEquals(
            list(sorted(blogView._getAllTags())),
            [u'bar', u'foo'])


    def test_editLinkIfEditable(self):
        """
        Test that L{hyperbola_view.BlogPostBlurbViewer} renders an 'edit' link
        if the underlying blurb is editable.
        """
        post = self._makeBlurb(hyperblurb.FLAVOR.BLOG_POST)

        authorShareID = sharing.shareItem(
            post, toRole=sharing.getSelfRole(self.store),
            interfaces=[ihyperbola.IEditable]).shareID
        authorPostShare = sharing.getShare(
            self.store, sharing.getSelfRole(self.store), authorShareID)

        authorPostView = hyperbola_view.blurbViewDispatcher(authorPostShare)
        THE_TAG = tags.invisible(foo='bar')
        result = authorPostView.render_editLink(
            context.WebContext(tag=THE_TAG), None)
        self.assertIdentical(result, THE_TAG)


class BlurbViewerTests(TestCase):
    """
    Tests for L{BlurbViewer}.
    """
    def test_postWithoutPrivileges(self):
        """
        Attempting to post to a blog should result in a L{LoginPage} which
        remembers the parameters of the attempted post.
        """
        class StubBlurb(object):
            """
            L{Blurb}-alike for testing purposes.
            """
            def __init__(self, store, flavor):
                self.store = store
                self.flavor = flavor

        store = Store()

        # XXX IStaticShellContent needs to go.
        class ParentStore(object):
            pass
        store.parent = ParentStore()
        directlyProvides(store.parent, IStaticShellContent)

        currentSegments = ['foo', 'bar']
        postSegments = ['post', 'baz']
        arguments = {'quux': ['1', '2']}
        request = FakeRequest(
            uri='/'.join([''] + currentSegments + postSegments),
            currentSegments=currentSegments, args=arguments)
        blurb = StubBlurb(store, FLAVOR.BLOG)
        sharedBlurb = SharedProxy(blurb, (IViewable,), 'abc')
        view = BlurbViewer(sharedBlurb)
        child, segments = view.locateChild(request, postSegments)
        self.assertTrue(isinstance(child, LoginPage))
        self.assertEqual(child.segments, currentSegments + postSegments[:1])
        self.assertEqual(child.arguments, arguments)
        self.assertEqual(segments, postSegments[1:])
        self.assertIdentical(child.staticContent, store.parent)
