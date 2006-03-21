
from zope.interface import implements

from nevow import athena

from xmantissa import ixmantissa, webtheme

from xmantissa import tdbview, sharing, liveform

from hyperbola.hyperblurb import Blurb, FLAVOR
from hyperbola import ihyperbola

class HyperbolaView(athena.LiveFragment):
    # This is a Fragment of a Page
    implements(ixmantissa.INavigableFragment)

    # This View will use the hyperbola-start.html template
    fragmentName = 'hyperbola-start'

    live = 'athena'
    iface = {}

    def head(self):
        # Add tags in the page <head>
        pass


    def render_blogs(self, ctx, data):
        view = tdbview.TabularDataView(
            self.original.getTDM(),
            [tdbview.ColumnViewBase('title', displayName='Title')])
        view.page = self.page
        view.docFactory = webtheme.getLoader(view.fragmentName)
        return ctx.tag[view]


    def render_addBlog(self, ctx, data):
        return BlogAddingFragment(self.page, self.original)



class BlogAddingFragment(liveform.LiveForm):
    #fragmentName = 'hyperbola-add-blog'
    fragmentName = None
    jsClass = u'Hyperbola.AddBlog'

    def __init__(self, page, hyperbola):
        super(BlogAddingFragment, self).__init__(self.addBlog,
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
                    "A Blog that I write") ])
        self.setFragmentParent(page)
        self.hyperbola = hyperbola
        # ideally, self.docFactory = webtheme.getLoader(self.fragmentName)

    def addBlog(self, title, description):
        store = self.hyperbola.store

        blog = self.hyperbola.topPost(title, description, FLAVOR.BLOG)

        authorsRole = sharing.getPrimaryRole(store, title + u' blog', True)
        sharing.getSelfRole(store).becomeMemberOf(authorsRole)

        sharing.shareItem(blog, authorsRole, shareID=u'blog')
        sharing.shareItem(blog, sharing.getEveryoneRole(store), shareID=u'blog',
                          interfaces=[ihyperbola.IViewer])


class BlurbViewer(athena.LiveFragment):
    implements(ixmantissa.INavigableFragment)
    fragmentName = 'hyperbola-view-blurb'
    jsClass = u'Hyperbola.ViewBlurb'

    def __init__(self, frag):
        super(athena.LiveFragment, self).__init__(frag)

    def customizeFor(self, username):
        print 'blurb viewer customized for', username
        self.customizedFor = username
        return self

    def head(self):
        pass

from twisted.python.components import registerAdapter
registerAdapter(BlurbViewer, Blurb, ixmantissa.INavigableFragment)
