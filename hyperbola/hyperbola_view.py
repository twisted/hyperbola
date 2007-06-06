# -*- test-case-name: hyperbola.test -*-

"""
This module contains web-based views onto L{hyperbola.hyperblurb.Blurb}
objects published by Hyperbola.
"""

from zope.interface import implements

from twisted.python.components import registerAdapter

from axiom.tags import Catalog, Tag

from nevow import athena, inevow, page, tags, rend, loaders
from nevow.url import URL
from nevow.flat import flatten

from xmantissa import ixmantissa, webtheme, websharing, website, webapp, publicresource
from xmantissa.publicweb import LoginPage
from xmantissa import sharing, liveform

from hyperbola.hyperblurb import FLAVOR, Blurb
from hyperbola import ihyperbola

class HyperbolaView(athena.LiveFragment):
    """
    Fragment responsible for rendering the initial hyperbola page
    """
    # This is a Fragment of a Page
    implements(ixmantissa.INavigableFragment)

    # This View will use the hyperbola-start.html template
    fragmentName = 'hyperbola-start'

    iface = {}

    def head(self):
        """
        Override L{ixmantissa.INavigableFragment.head} to do nothing, since we
        don't have to add anything to the header.
        """
        # XXX somebody kill this framework requirement please --glyph


    def render_listBlogs(self, ctx, data):
        """
        Render a list of all blogs.
        """
        return BlogListFragment(self.page, self.original)


    def render_addBlog(self, ctx, data):
        """
        Render an add blog form.
        """
        return BlogAddingFragment(self.page, self.original)



class BlurbPostingResource(publicresource.PublicAthenaLivePage):
    """
    L{nevow.inevow.IResource} which wraps and renders the appropriate add
    comment fragment for the blurb it is passed
    """
    def __init__(self, store, parentBlurb, forUser):
        blurbView = blurbViewDispatcher(parentBlurb)
        blurbView.customizeFor(forUser)

        super(BlurbPostingResource, self).__init__(
            store.parent,
            addCommentDialogDispatcher(blurbView),
            forUser=forUser)



class BlogListFragment(webtheme.ThemedElement):
    """
    Fragment which renders a list of all blogs
    """
    fragmentName = 'hyperbola-blog-list'

    def __init__(self, page, hyperbola):
        """
        @type hyperbola: L{hyperbola.hyperbola_model.HyperbolaPublicPresence
        """
        self.setFragmentParent(page)
        self.hyperbola = hyperbola
        super(BlogListFragment, self).__init__()

    def _getPostURL(self, blog):
        """
        Figure out a URL which could be used for posting to C{blog}

        @type blog: L{xmantissa.sharing.SharedProxy}
        @rtype: C{unicode}
        """
        ws = self.hyperbola.store.parent.findUnique(website.WebSite)
        return str(ws.encryptedRoot()) + websharing.linkTo(blog)[1:] + '/post'

    def blogs(self, req, tag):
        """
        Render all blogs
        """
        p = inevow.IQ(self.docFactory).patternGenerator('blog')
        webapp = ixmantissa.IWebTranslator(self.hyperbola.store)
        blogs = list()
        primaryRole = sharing.getSelfRole(self.hyperbola.store)
        for blog in self.hyperbola.getTopLevelFor(primaryRole):
            blogs.append(p.fillSlots(
                    'title', blog.title).fillSlots(
                    'link', websharing.linkTo(blog)).fillSlots(
                    'post-url', self._getPostURL(blog)))
        return tag[blogs]
    page.renderer(blogs)



class BlogAddingFragment(liveform.LiveForm):
    """
    Fragment which renders a form for adding a new blog
    """
    fragmentName = 'hyperbola-add-blog'
    jsClass = u'Hyperbola.AddBlog'

    def __init__(self, page, hyperbola):
        super(BlogAddingFragment, self).__init__(
            hyperbola.createBlog,
            [liveform.Parameter(
                'title',
                liveform.TEXT_INPUT,
                unicode,
                "A title for your blog",
                "A Blog"),
             liveform.Parameter(
                'description',
                liveform.TEXT_INPUT,
                unicode,
                "A description of your blog",
                "A Blog that I write")])
        self.setFragmentParent(page)
        self.hyperbola = hyperbola
        self.docFactory = webtheme.getLoader(self.fragmentName)



flavorNames = {
    FLAVOR.BLOG_POST: 'Post',
    FLAVOR.BLOG_COMMENT: 'Comment',
    FLAVOR.BLOG: 'Blog',
    FLAVOR.FORUM: 'Forum',
    FLAVOR.FORUM_TOPIC: 'Forum Topic',
    FLAVOR.FORUM_POST: 'Forum Post',
    FLAVOR.WIKI: 'Wiki',
    FLAVOR.WIKI_NODE: 'Wiki Node'}



def parseTags(tagString):
    """
    Turn a comma delimited string of tag names into a list of tag names

    @type tagString: C{unicode}
    @rtype: C{list} of C{unicode}
    """
    tags = list()
    for tag in tagString.split(','):
        tag = tag.strip()
        if tag:
            tags.append(tag)
    return tags



class AddCommentFragment(liveform.LiveForm):
    """
    Base/default fragment which renders into some UI for commenting on a blub
    """
    fragmentName = 'add-comment/default'
    jsClass = u'Hyperbola.AddComment'

    def __init__(self, parent):
        self.parent = parent
        self._commentTypeName = flavorNames[
            FLAVOR.commentFlavors[parent.original.flavor]]

        super(AddCommentFragment, self).__init__(
            self.addComment,
            (liveform.Parameter(
                'title',
                liveform.TEXT_INPUT,
                unicode,
                'Title'),
             liveform.Parameter(
                'body',
                liveform.TEXT_INPUT,
                unicode,
                'Body'),
             liveform.Parameter(
                'tags',
                liveform.TEXT_INPUT,
                parseTags)))

        self.docFactory = webtheme.getLoader(self.fragmentName)


    def addComment(self, title, body, tags):
        """
        Add a comment blurb to our parent blurb

        @param title: the title of the comment
        @type title: C{unicode}

        @param body: the body of the comment
        @type body: C{unicode}

        @param tags: tags to apply to the comment
        @type tags: iterable of C{unicode}

        @rtype: C{None}
        """
        shareID = self.parent.original.post(title, body, self.parent.getRole())
        role = self.parent.getRole()
        # is role.store correct?
        post = sharing.getShare(role.store, role, shareID)
        for tag in tags:
            post.tag(tag)

    def commentTypeName(self, req, tag):
        """
        Figure out what this type of comment would be called (e.g. a comment
        on a blog is a 'blog post')
        """
        return self._commentTypeName
    page.renderer(commentTypeName)

    def head(self):
        return None


class AddBlogCommentFragment(AddCommentFragment):
    """
    L{AddCommentFragment} subclass for making comments of type
    L{FLAVOR.BLOG_COMMENT}
    """
    fragmentName = 'add-comment/' + FLAVOR.BLOG_COMMENT

class AddBlogPostFragment(AddCommentFragment):
    """
    L{AddCommentFragment} subclass for making comments of type
    L{FLAVOR.BLOG_POST}
    """
    jsClass = u'Hyperbola.AddBlogPost'
    fragmentName = 'add-comment/' + FLAVOR.BLOG_POST

    def _getAllTags(self):
        """
        Get all the tags in the same store as the underlying item of our
        parent blurb

        @rtype: C{list} of C{unicode}
        """
        store = sharing.itemFromProxy(self.parent.original).store
        return list(store.findOrCreate(Catalog).tagNames())

    def getInitialArguments(self):
        """
        Override default implementation to include the list of all tags
        """
        return (self._getAllTags(),)



class AddBlogPostDialogFragment(AddBlogPostFragment):
    """
    L{AddBlogPostFragment} subclass for making comments of type L{FLAVOR.BLOG_POST}
    """
    jsClass = u'Hyperbola.AddBlogPostDialog'
    fragmentName = 'add-comment/' + FLAVOR.BLOG_POST + '-dialog'

    def title(self, req, tag):
        """
        Determine a preset value for the title of the comment, by looking at the
        C{title} argument in the request.
        """
        return req.args['title'][0]
    page.renderer(title)

    def body(self, req, tag):
        """
        Determine a preset value for the body of the comment, by looking at the
        C{body} argument in the request, and inserting a link to the url
        specified in the C{url} argument.
        """
        body = req.args['body'][0]
        url = req.args['url'][0]
        link = tags.a(href=url)[self.title(req, tag)]
        return flatten((link, tags.br, body))
    page.renderer(body)


ADD_COMMENT_VIEWS = {FLAVOR.BLOG: AddBlogPostFragment,
                     FLAVOR.BLOG_COMMENT: AddCommentFragment}

def addCommentDispatcher(parent):
    """
    Figure out the view class that should render an add comment form for the
    parent blurb C{parent}

    @type parent: L{BlurbViewer}
    @rtype: L{AddCommentFragment}
    """
    return ADD_COMMENT_VIEWS.get(
        parent.original.flavor, AddCommentFragment)(parent)

ADD_COMMENT_DIALOG_VIEWS = {FLAVOR.BLOG: AddBlogPostDialogFragment}

def addCommentDialogDispatcher(parent):
    """
    Figure out the view class that should render an add comment dialog form
    for the parent blurb C{parent}

    @type parent: L{BlurbViewer}
    @rtype: L{AddCommentDialogFragment}
    """
    return ADD_COMMENT_DIALOG_VIEWS.get(
        # this isn't a sensible default
        parent.original.flavor, AddCommentFragment)(parent)



class BlurbViewer(athena.LiveFragment, rend.ChildLookupMixin):
    """
    Base/default class for rendering blurbs
    """
    implements(ixmantissa.INavigableFragment)
    fragmentName = 'view-blurb/default'

    customizedFor = None

    def __init__(self, original, *a, **k):
        super(BlurbViewer, self).__init__(original, *a, **k)
        self._childTypeName = flavorNames[
            FLAVOR.commentFlavors[original.flavor]]

    def customizeFor(self, username):
        """
        This method is invoked with the viewing user's identification when being
        viewed publicly.
        """
        self.customizedFor = username
        return self


    def getRole(self):
        """
        Retrieve the role currently viewing this blurb viewer.
        """
        item = sharing.itemFromProxy(self.original)
        if self.customizedFor is None:
            # If this hasn't been customized, it's public.
            return sharing.getEveryoneRole(item.store)
        else:
            # Otherwise, get the primary role of the current observer.
            return sharing.getPrimaryRole(item.store, self.customizedFor)

    def child_post(self, ctx):
        """
        If the user is authorized, return a L{BlurbPostingResource}
        """
        store = sharing.itemFromProxy(self.original).store
        if ihyperbola.ICommentable.providedBy(self.original):
            return BlurbPostingResource(
                store, self.original, self.customizedFor)
        return LoginPage.fromRequest(store.parent, inevow.IRequest(ctx))

    def head(self):
        pass

    def render_title(self, ctx, data):
        """
        @return: title of our blurb
        """
        return self.original.title

    def _htmlifyLineBreaks(self, body):
        """
        Replace line breaks with <br> elements
        """
        return [(tags.xml(line), tags.br) for line
                    in self.original.body.splitlines()]

    def render_body(self, ctx, data):
        """
        @return: body of our blurb
        """
        return self._htmlifyLineBreaks(self.original.body)

    def render_dateCreated(self, ctx, data):
        """
        @return: creation date of our blurb
        """
        return self.original.dateCreated.asHumanly()

    def render_childCount(self, ctx, data):
        """
        @return: child count of our blurb
        """
        # XXX
        return sum(1 for ign in self.original.view(self.getRole()))

    def render_childTypeName(self, ctx, data):
        """
        @return: the name of the type of our child blurbs
        """
        return self._childTypeName

    def _getChildBlurbs(self, ctx):
        """
        Get the child blurbs of this blurb

        @rtype: C{list} of L{xmantissa.sharing.SharedProxy}
        """
        return list(self.original.view(self.getRole()))

    def render_view(self, ctx, data):
        """
        Render the child blurbs of this blurb
        """
        blurbs = self._getChildBlurbs(ctx)
        if 0 < len(blurbs):
            for blurb in blurbs:
                f = blurbViewDispatcher(blurb)
                f.setFragmentParent(self)
                f.docFactory = webtheme.getLoader(f.fragmentName)
                yield f
        else:
            p = inevow.IQ(self.docFactory).onePattern('no-child-blurbs')
            yield p.fillSlots('child-type-name', self._childTypeName)

    def render_addComment(self, ctx, data):
        """
        Render some UI for commenting on this blurb
        """
        if not ihyperbola.ICommentable.providedBy(self.original):
            return ''
        f = addCommentDispatcher(self)
        f.setFragmentParent(self)
        f.docFactory = webtheme.getLoader(f.fragmentName)
        return f

    def render_author(self, ctx, data):
        """
        Render the author of this blurb
        """
        # XXX this returns 'Everyone'
        return self.original.author.externalID


class _BlogPostBlurbViewer(BlurbViewer):
    """
    L{BlurbViewer} subclass for rendering blurbs of type L{FLAVOR.BLOG_POST}
    """
    fragmentName = 'view-blurb/' + FLAVOR.BLOG_POST
    jsClass = u'Hyperbola.BlogPostBlurbController'

    NO_TAGS_MARKER = u'Uncategorized'

    def _getSelectedTag(self, ctx):
        """
        Figure out which tag the user is filtering by, by looking at the URL

        @rtype: C{None} or C{unicode}
        """
        req = inevow.IRequest(ctx)
        tag = req.args.get('tag', [None])[0]
        if not tag:
            return None
        return tag

    def render_titleLink(self, ctx, data):
        """
        @return: title of our blurb
        """
        url = websharing.linkTo(self.original)
        return ctx.tag.fillSlots(
            'link', url + '/detail').fillSlots(
            'title', self.original.title)

    def render_tags(self, ctx, data):
        """
        Render the tags of this blurb
        """
        iq = inevow.IQ(self.docFactory)
        separatorPattern = iq.patternGenerator('tag-separator')
        tags = list()
        selectedTag = self._getSelectedTag(ctx)
        for tag in self.original.tags():
            if tag == selectedTag:
                p = 'selected-tag'
            else:
                p = 'tag'
            tagPattern = iq.onePattern(p)
            tags.extend((tagPattern.fillSlots('name', tag),
                         separatorPattern()))
        if tags:
            return tags[:-1]
        return self.NO_TAGS_MARKER

    def render_editor(self, ctx, data):
        f = editBlurbDispatcher(self.original)
        f.setFragmentParent(self)
        f.docFactory = webtheme.getLoader(f.fragmentName)
        return f

    def render_editLink(self, ctx, data):
        if ihyperbola.IEditable.providedBy(self.original):
            return ctx.tag
        return ''

    def render_deleteLink(self, ctx, data):
        """
        Render a delete link or not, depending on whether the user has the
        appropriate permissions
        """
        if ihyperbola.IEditable.providedBy(self.original):
            return ctx.tag
        return ''

    def delete(self):
        """
        Unshare and delete our blurb, and all of its children
        """
        self.original.delete()
    athena.expose(delete)



class BlogPostBlurbViewer(_BlogPostBlurbViewer):
    def child_detail(self, ctx):
        """
        Return a L{BlogPostBlurbViewerDetail} for this blog post
        """
        f = blurbViewDetailDispatcher(self.original)
        f.customizeFor(self.customizedFor)
        f.docFactory = webtheme.getLoader(f.fragmentName)

        return publicresource.PublicAthenaLivePage(
            sharing.itemFromProxy(self.original).store.parent,
            f,
            forUser=self.customizedFor)



class BlogPostBlurbViewerDetail(_BlogPostBlurbViewer):
    """
    L{_BlogPostBlurbViewer} subclass which includes renderers specific to the
    detail page
    """
    fragmentName = 'view-blurb/detail/' + FLAVOR.BLOG_POST

    def render_blogTitle(self, ctx, data):
        """
        Return the title of the blog our blurb was posted in
        """
        return self.original.parent.title

    def render_blogBody(self, ctx, data):
        """
        Return the body (subtitle) of the blog our blurb was posted in
        """
        return self.original.parent.body



class BlogPostBlurbEditor(liveform.LiveForm):
    """
    Fragment for rendering blog post editing UI
    """
    jsClass = u'Hyperbola.BlogPostBlurbEditorController'
    fragmentName = 'edit-blog-post'

    def __init__(self, blogPost):
        super(BlogPostBlurbEditor, self).__init__(
            lambda *a, **k: blogPost.edit(newAuthor=blogPost.author, *a, **k),
            (liveform.Parameter(
                'newTitle',
                liveform.TEXT_INPUT,
                unicode),
             liveform.Parameter(
                'newBody',
                liveform.TEXT_INPUT,
                unicode),
             liveform.Parameter(
                'newTags',
                liveform.TEXT_INPUT,
                parseTags)))
        self.blogPost = blogPost


    def title(self, req, tag):
        """
        @return: title of our blurb
        """
        return self.blogPost.title
    page.renderer(title)


    def body(self, req, tag):
        """
        @return: body of our blurb
        """
        return self.blogPost.body
    page.renderer(body)


    def tags(self, req, tag):
        """
        @return tags of our blurb
        """
        return ', '.join(self.blogPost.tags())
    page.renderer(tags)



class BlogCommentBlurbViewer(BlurbViewer):
    """
    L{BlurbViewer} subclass for rendering blurbs of type L{FLAVOR.BLOG_COMMENT}
    """
    fragmentName = 'view-blurb/' + FLAVOR.BLOG_COMMENT

class BlogBlurbViewer(BlurbViewer):
    """
    L{BlurbViewer} subclass for rendering blurbs of type L{FLAVOR.BLOG}
    """
    fragmentName = 'view-blurb/' + FLAVOR.BLOG
    jsClass = u'Hyperbola.BlogBlurbController'

    def _getAllTags(self):
        """
        Get all the tags which have been applied to blurbs in the same store
        as the underlying item of our blurb.

        @rtype: C{list} of C{unicode}
        """
        store = sharing.itemFromProxy(self.original).store
        # query instead of using Catalog so that tags only applied to
        # PastBlurb items don't get included
        return list(store.query(
            Tag, Tag.object == Blurb.storeID).getColumn('name').distinct())

    def _getSelectedTag(self, ctx):
        """
        Figure out which tag the user is filtering by, by looking at the URL

        @rtype: C{None} or C{unicode}
        """
        req = inevow.IRequest(ctx)
        tag = req.args.get('tag', [None])[0]
        if not tag:
            return None
        return tag

    def _getChildBlurbs(self, ctx):
        """
        Get the child blurbs of this blurb, filtering by the selected tag

        @rtype: C{list} of L{xmantissa.sharing.SharedProxy}
        """
        tag = self._getSelectedTag(ctx)
        if tag is not None:
            return list(self.original.viewByTag(
                self.getRole(), tag.decode('utf-8')))
        return list(self.original.view(self.getRole()))


    def render_tags(self, ctx, data):
        """
        Render all tags
        """
        iq = inevow.IQ(self.docFactory)
        selTag = self._getSelectedTag(ctx)
        for tag in self._getAllTags():
            if tag == selTag:
                pattern = 'selected-tag'
            else:
                 pattern = 'tag'
            yield iq.onePattern(pattern).fillSlots('name', tag)



BLURB_VIEWS = {FLAVOR.BLOG_POST: BlogPostBlurbViewer,
               FLAVOR.BLOG: BlogBlurbViewer,
               FLAVOR.BLOG_COMMENT: BlogCommentBlurbViewer}



def blurbViewDispatcher(blurb):
    """
    Figure out the view class that should render the blurb C{blurb}

    @type blurb: L{xmantissa.sharing.SharedProxy}
    @rtype: L{BlurbViewer}
    """
    return BLURB_VIEWS.get(blurb.flavor, BlurbViewer)(blurb)



registerAdapter(
    blurbViewDispatcher,
    ihyperbola.IViewable,
    ixmantissa.INavigableFragment)



BLURB_DETAIL_VIEWS = {FLAVOR.BLOG_POST: BlogPostBlurbViewerDetail}



def blurbViewDetailDispatcher(blurb):
    """
    Figure out the view class that should render the blurb detail for C{blurb}

    @type blurb: L{xmantissa.sharing.SharedProxy}
    @rtype: L{BlurbViewer}
    """
    return BLURB_DETAIL_VIEWS.get(blurb.flavor, BlurbViewer)(blurb)



EDIT_BLURB_VIEWS = {FLAVOR.BLOG_POST: BlogPostBlurbEditor}



def editBlurbDispatcher(blurb):
    """
    Figure out the view class that should render the edit blurb form for
    C{blurb}

    @type blurb: L{xmantissa.sharing.SharedProxy}
    @rtype: L{BlogPostBlurbEditor}
    """
    # not a great default for now
    return EDIT_BLURB_VIEWS.get(blurb.flavor, BlogPostBlurbEditor)(blurb)
