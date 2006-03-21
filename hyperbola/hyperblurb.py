# -*- test-case-name: hyperbola.test.test_hyperbola -*-

from twisted.python.reflect import qual, namedAny

from epsilon.extime import Time

from axiom.item import Item
from axiom.attributes import text, reference, integer, timestamp, AND

from xmantissa.sharing import Role, shareItem

from hyperbola import ihyperbola

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


class FlavorPermission(Item):
    """ I am associated with a top-level Blurb and specify the associated roles for
    all of its children.  For example: if there is a top-level blurb
    representing a blog, there might be a FlavorPermission associated with it
    that makes reference to a 'commenter' role for the BLOG_POST flavor, which
    has permissions
    'post,title,body,dateCreated,dateLastEdited,author,flavor,parent' - but
    conspicuously omits 'edit' and 'hits'.
    """

    typeName = 'hyperbola_flavor_permission'
    flavor = text()
    blurb = reference()
    role = reference()
    permissions = text()        # comma-separated list of attributes

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
    flavor = text(doc="One of FLAVOR's capitalized attributes.", allowNone=False)

    def edit(self, newTitle, newBody, newAuthor):
        """ Edit an existing blurb, saving a PastBlurb of its current state for
        rollback purposes.
        """
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

    def post(self, childTitle, childBody, childAuthor):
        """
        Create a new child of this Blurb, with a flavor derived from the
        mapping into FLAVOR.commentFlavors of self.flavor, shared to every role
        specified by FlavorPermission items that refer to the new flavor of
        blurb that will be created, and this blurb or any of my parents.

        For example, if I am a FLAVOR.BLOG, the child will be a
        FLAVOR.BLOG_POST.  If the FlavorPermissions are set up correctly for
        me, one role will be able to view that post, another to comment on it.

        By using FlavorPermissions appropriately, you can have a blog that
        allows public posting, and a blog that allows private posting and no
        public viewing, and a blog that allows public viewing but only
        permissioned posting and commenting, all in the same store.

        @return: A share ID.
        """

        newFlavor = FLAVOR.commentFlavors[self.flavor]
        newBlurb = Blurb(
            store=self.store,
            flavor=newFlavor,
            parent=self,
            body=childBody,
            title=childTitle,
            author=childAuthor,
            dateLastEdited=Time(),
            hits=0)

        roleToPerms = {childAuthor: [ihyperbola.IAuthor]}
        currentBlurb = self
        while currentBlurb is not None:
            currentBlurb.updateFlavorPermissions(roleToPerms, newFlavor)
            currentBlurb = currentBlurb.parent
        firstShareID = None     # we want the shareIDs to all be the same -
                                # since "None" will allocate a new one, we just
                                # use this value regardless
        for role, interfaceList in roleToPerms.items():
            shareObj = shareItem(newBlurb, interfaces=interfaceList,
                                 toRole=role, shareID=firstShareID)
            firstShareID = shareObj.shareID
        return firstShareID

    def permitChildren(self, role, flavor, *interfaces):
        FlavorPermission(
            store=self.store,
            flavor=flavor,
            role=role,
            permissions=u','.join(map(qual, interfaces)),
            blurb=self)

    def updateFlavorPermissions(self, permsdict, flav):
        for fp in self.store.query(FlavorPermission,
                                   AND(FlavorPermission.flavor == flav,
                                       FlavorPermission.blurb == self)):
            if fp.role not in permsdict:
                # Children supersede their parents.  For example, if you want
                # to lock comments on a particular entry, you can give it a new
                # FlavorPermission and its parents will no longer override.
                permsdict[fp.role] = map(namedAny, fp.permissions.split(","))




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

    blurb = reference(reftype=Blurb)
