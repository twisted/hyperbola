
from epsilon.extime import Time

from axiom.item import Item
from axiom.attributes import text, reference, integer, timestamp

from xmantissa.sharing import Role, allow

class FLAVOR:
    BLOG = u'FLAVOR.BLOG'
    BLOG_POST = u'FLAVOR.BLOG_POST'

    BLOG_COMMENT = u'FLAVOR.BLOG_COMMENT'

    FORUM = u'FLAVOR.FORUM'
    FORUM_TOPIC = u'FLAVOR.FORUM_TOPIC'
    FORUM_POST = u'FLAVOR.FORUM_POST'

    WIKI = u'FLAVOR.WIKI'
    WIKI_NODE = u'FLAVOR.WIKI_NODE'

    commentFlavors = {

        BLOG: BLOG_POST,
        BLOG_POST: BLOG_COMMENT,
        BLOG_COMMENT: BLOG_COMMENT,

        FORUM_POST: FORUM_POST,
        FORUM_TOPIC: FORUM_POST,
        FORUM: FORUM_TOPIC,

        WIKI: WIKI_NODE,
        WIKI_NODE: WIKI_NODE,

        }

    def ofCommentOn(cls, entry):
        return cls.commentFlavors.get(entry)

    ofCommentOn = classmethod(ofCommentOn)



class MetaBlurb(Item):
    """
    I am an association of metadata with blurbs.

    The difference between "core" metadata -- metadata which lives in L{Blurb}
    -- and "extension" metadata -- metadata that lives in L{MetaBlurb} -- is
    that MetaBlurb metadata should never be processed by Hyperbola itself.  It
    is a mechanism which can be used for display purposes ("Mood", "Music",
    "Current Obsession") or as a way to relay semi-structured information
    ("Current Weather", "Relevance") to *other* software which will be
    accessing Hyperbola publications as clients.
    """

    typeName = 'hyperbola_metablurb'
    schemaVersion = 1

    blurb = reference()

    key = text()
    value = text()


class Blurb(Item):
    """
    I am some text written by a user.

    'Blurb' is the super-generic term used to refer to all forms of publishing
    and commentary within Hyperbola.  Traditionally entirely different software
    packages have been constructed to handle 'forums', 'blogs', 'posts',
    'comments', 'articles', etc.  In hyperbola, text written by a user in any
    context becomes a blurb; whether it is displayed as forum software or blog
    software would display it (and how: as a comment, as a topic, as a post) is
    determined by its 'flavor'.

    Flavors are described by L{FLAVOR}.
    """

    typeName = 'hyperbola_blurb'
    schemaVersion = 1

    dateCreated = timestamp()
    dateLastEdited = timestamp()

    title = text()
    body = text()

    hits = integer(doc="The number of times that this blurb has been displayed to users.",
                   default=0)
    author = reference(reftype=Role,
                       allowNone=False)

    parent = reference()        # to Blurb, but you can't spell that AGGUGHH
    flavor = text(doc="One of FLAVOR's capitalized attributes.")

    def edit(self, newTitle, newBody, newAuthor):
        # Edit is only called on subsequent edits, not the first time, so we
        # need to save our current contents as history.
        editDate = Time()
        PastBlurb(store=self.store,
                  title=self.title,
                  body=self.body,
                  author=self.author,
                  blurb=self,
                  dateEdited=self.dateLastEdited,
                  hits=self.hits)
        self.title = newTitle
        self.body = newBody
        self.dateLastEdited = editDate
        self.author = newAuthor


    allow(edit,
          'title', 'body', 'dateCreated', 'dateLastEdited', 'author',
          'flavor', 'hits',
          'parent')


class PastBlurb(Item):
    """
    This is an old version of a blurb.  It contains the text as it used to be
    at a particular point in time.
    """

    typeName = 'hyperbola_past_blurb'
    schemaVersion = 1

    dateEdited = timestamp()

    title = text()
    body = text()

    hits = integer(doc="The number of times that this blurb has been displayed to users.")
    author = reference(reftype=Role,
                       allowNone=False)

    blurb = reference(Blurb)
