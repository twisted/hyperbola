# -*- test-case-name: hyperbola.test.test_view.ViewTestCase.test_scrollViewRenderer -*-
"""
Tests for Hyperbola view logic
"""
from xml.dom import minidom

from zope.interface import directlyProvides

from twisted.trial.unittest import TestCase

from epsilon.extime import Time

from axiom.store import Store

from nevow import context, tags, loaders, athena, flat, inevow
from nevow.testutil import FakeRequest, FragmentWrapper, renderLivePage
from nevow.flat import flatten

from xmantissa import sharing, port, websharing, scrolltable
from xmantissa.sharing import SharedProxy
from xmantissa.publicweb import LoginPage
from xmantissa.ixmantissa import IStaticShellContent, IWebTranslator
from xmantissa.website import WebSite

from hyperbola import hyperbola_view, hyperblurb, ihyperbola
from hyperbola.hyperblurb import FLAVOR
from hyperbola.hyperbola_view import BlurbViewer
from hyperbola.ihyperbola import IViewable
from hyperbola.test.util import HyperbolaTestMixin



class ScrollerTestCase(TestCase, HyperbolaTestMixin):
    """
    Tests for L{hyperbola_view.ShareScrollingElement} and related
    functionality.
    """
    def setUp(self):
        """
        Set up an environment suitable for testing the share-handling
        functionality of L{hyperbola_view.ShareScrollingElement}.
        """
        self._setUpStore()

        blogShare = self._shareAndGetProxy(self._makeBlurb(FLAVOR.BLOG))
        EVERYBODY = sharing.getEveryoneRole(self.store)
        sharing.itemFromProxy(blogShare).permitChildren(
            EVERYBODY, FLAVOR.BLOG_POST, ihyperbola.IViewable)

        # For sanity's sake, let's not have the role of the view and the role
        # implicitly chosen by not calling 'customizeFor' disagree.  (This
        # shouldn't be possible anyway, and in the future getRole should just
        # be looking at its proxy.)
        self.publicBlogShare = sharing.getShare(
            self.store, EVERYBODY, blogShare.shareID)
        selfRole = sharing.getSelfRole(self.store)
        blogPostShareID = blogShare.post(u'', u'', selfRole)
        self.blogPostSharedToEveryone = sharing.getShare(
            self.store, EVERYBODY, blogPostShareID)
        self.blogPostItem = sharing.itemFromProxy(self.blogPostSharedToEveryone)


    def _getRenderViewScroller(self):
        """
        Get a L{hyperbola_view.ShareScrollingElement} by way of
        L{hyperbola_view.BlogBlurbViewer.render_view}.
        """
        fragment = hyperbola_view.BlogBlurbViewer(self.publicBlogShare)
        hyperbola_view._docFactorify(fragment)
        ctx = context.WebContext(tag=tags.invisible())
        ctx.remember(FakeRequest(), inevow.IRequest)
        return fragment.render_view(ctx, None)


    def test_scrollViewRenderer(self):
        """
        Verify that L{hyperbola_view.BlogBlurbViewer.render_view} returns a
        L{hyperbola.hyperbola_view.ShareScrollTable} when posts are available.
        """
        scroller = self._getRenderViewScroller()
        self.failUnless(isinstance(scroller,
                                   hyperbola_view.ShareScrollingElement))


    def test_renderedScrollerInitializedCorrectly(self):
        """
        L{hyperbola_view.BlogBlurbViewer.render_view} should return a
        L{hyperbola.hyperbola_view.ShareScrollTable} that is aware of
        all of the posts that have been made to the blog.
        """
        scroller = self._getRenderViewScroller()
        rows = scroller.rowsAfterValue(None, 10)
        self.assertEqual(len(rows), 1)
        theRow = rows[0]
        self.assertEqual(
            theRow['dateCreated'],
            self.blogPostItem.dateCreated.asPOSIXTimestamp())
        self.assertEqual(
            theRow['__id__'],
            IWebTranslator(self.store).toWebID(self.blogPostItem))
        blogPostFragment = theRow['blurbView']
        # the scrolltable fragment is not customized, so we want to
        # ensure that the proxy passed to the IColumns is the facet
        # shared to Everyone
        self.assertEqual(
            list(blogPostFragment.original.sharedInterfaces),
            list(self.blogPostSharedToEveryone.sharedInterfaces))
        self.assertIdentical(
            sharing.itemFromProxy(blogPostFragment.original),
            self.blogPostItem)


    def test_renderedScrollerRenderable(self):
        """
        L{hyperbola_view.BlogBlurbViewer.render_view} should return a
        L{hyperba.hyperbola_view.ShareScrollTable} that is renderable
        - i.e. has a docFactory and is not an orphan.
        """
        scroller = self._getRenderViewScroller()
        self.failUnless(scroller.fragmentParent is not None)
        return renderLivePage(FragmentWrapper(scroller))


    def test_blurbTimestampColumn(self):
        """
        Verify the L{xmantissa.ixmantissa.IColumn} implementation of
        L{hyperbola_view._BlurbTimestampColumn}.
        """
        col = hyperbola_view._BlurbTimestampColumn()
        self.assertEqual(col.attributeID, 'dateCreated')
        self.assertEqual(col.getType(), 'timestamp')
        self.blogPostItem.dateCreated = Time.fromPOSIXTimestamp(345)
        value = col.extractValue(None, self.blogPostItem)
        self.assertEqual(value, 345)
        self.assertIdentical(col.sortAttribute(), hyperblurb.Blurb.dateCreated)
        comparable = col.toComparableValue(345)
        self.assertEqual(comparable, self.blogPostItem.dateCreated)


    def test_blurbViewColumn(self):
        """
        Verify the L{xmantissa.ixmantissa.IColumn} implementation of
        L{hyperbola_view.BlurbViewColumn}.
        """
        col = hyperbola_view.BlurbViewColumn()
        self.assertEqual(col.attributeID, 'blurbView')
        self.assertEqual(col.getType(), scrolltable.TYPE_WIDGET)
        model = athena.LivePage()
        frag = col.extractValue(model, self.blogPostSharedToEveryone)
        fragClass = hyperbola_view.blurbViewDispatcher(
            self.blogPostSharedToEveryone).__class__
        self.failUnless(isinstance(frag, fragClass))
        self.assertIdentical(frag.fragmentParent, model)
        self.failUnless(frag.docFactory)
        self.assertIdentical(col.sortAttribute(), None)
        self.assertRaises(NotImplementedError, col.toComparableValue, None)



class ViewTestCase(TestCase, HyperbolaTestMixin):
    """
    Tests for Hyperbola view logic
    """
    def setUp(self):
        self._setUpStore()


    def test_blogView(self):
        """
        L{hyperbola_view.BlogBlurbViewer.render_view} should render a
        pattern indicating that there are no blog posts, if it has no
        children.
        """
        blogShare = self._shareAndGetProxy(self._makeBlurb(FLAVOR.BLOG))
        fragment = hyperbola_view.BlogBlurbViewer(blogShare)
        fragment.docFactory = loaders.stan(
            tags.div(pattern='no-child-blurbs', foo='bar')[
            tags.slot(name='child-type-name')])
        ctx = context.WebContext(tag=tags.invisible)
        ctx.remember(FakeRequest(), inevow.IRequest)
        result = fragment.render_view(ctx, None)
        markup = flat.flatten(result)
        doc = minidom.parseString(markup)
        self.assertEqual(doc.firstChild.getAttribute('foo'), 'bar')
        self.assertEqual(
            doc.firstChild.firstChild.nodeValue, fragment._childTypeName)


    def test_blogsRenderer(self):
        """
        Test that L{hyperbola_view.BlogListFragment.blogs} renders a list of blogs.
        """
        ws = self.store.parent.findUnique(WebSite)
        ws.hostname = u'blogs.renderer'
        port.SSLPort(store=self.store.parent,
                     portNumber=443,
                     factory=ws)
        blog1 = self._shareAndGetProxy(self._makeBlurb(FLAVOR.BLOG))
        blog2 = self._shareAndGetProxy(self._makeBlurb(FLAVOR.BLOG))
        blf = hyperbola_view.BlogListFragment(
            athena.LivePage(), self.publicPresence)
        blf.docFactory = loaders.stan(
            tags.div(pattern='blog')[
                tags.span[tags.slot('title')],
                tags.span[tags.slot('link')],
                tags.span[tags.slot('post-url')]])
        tag = tags.invisible
        markup = flat.flatten(tags.div[blf.blogs(None, tag)])
        doc = minidom.parseString(markup)
        blogNodes = doc.firstChild.getElementsByTagName('div')
        self.assertEqual(len(blogNodes), 2)

        for (blogNode, blog) in zip(blogNodes, (blog1, blog2)):
            (title, blogURL, postURL) = blogNode.getElementsByTagName('span')
            blogURL = blogURL.firstChild.nodeValue
            expectedBlogURL = str(websharing.linkTo(blog))
            self.assertEqual(blogURL, expectedBlogURL)
            postURL = postURL.firstChild.nodeValue
            self.assertEqual(
                postURL, 'https://blogs.renderer' + expectedBlogURL + '/post')


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


    def test_bodyRendererEmptyBody(self):
        """
        L{BlurbViewer.render_body} should be able to render Blurbs
        with empty bodies.
        """
        body = u''
        view = BlurbViewer(self._makeBlurb(hyperblurb.FLAVOR.BLOG, None, body))
        result = flatten(view.render_body(None, None))
        self.assertEqual(result, body)


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


    def test_titleLink(self):
        """
        Verify that L{hyperbola_view.BlogPostBlurbViewer.render_titleLink}
        links to the correct url.
        """
        share = self._shareAndGetProxy(self._makeBlurb(FLAVOR.BLOG_POST))
        ctx = context.WebContext(tag=tags.div[tags.slot('link')])
        frag = hyperbola_view.BlogPostBlurbViewer(share)
        markup = flat.flatten(frag.render_titleLink(ctx, None))
        doc = minidom.parseString(markup)
        self.assertEqual(
            doc.firstChild.firstChild.nodeValue,
            str(websharing.linkTo(share).child('detail')))



class BlurbViewerTests(TestCase, HyperbolaTestMixin):
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


    def test_absoluteURL(self):
        """
        Verify that L{BlurbViewer._absoluteURL} returns something that looks
        correct.
        """
        self._setUpStore()
        ws = self.store.parent.findUnique(WebSite)
        ws.hostname = u'absolute.url'
        port.SSLPort(store=self.store.parent,
                     portNumber=443,
                     factory=ws)
        share = self._shareAndGetProxy(self._makeBlurb(FLAVOR.BLOG_POST))
        frag = BlurbViewer(share)
        self.assertEqual(
            frag._absoluteURL(), 'https://absolute.url' + str(websharing.linkTo(share)))
