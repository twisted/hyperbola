
"""
This module contains public pages for the hyperbola application's public
presence.  (There is nothing too interesting here right now.)
"""

from zope.interface import implements

from twisted.python.util import sibpath

from nevow import tags, static

from axiom.item import Item
from axiom import attributes

from xmantissa.publicresource import PublicPage
from xmantissa import ixmantissa

class HyperbolaPublicPage(Item):
    """
    HyperbolaPublicPage is the public powerup that provides a
    L{PublicIndexPage} as the hyperbola application's public page.
    """
    implements(ixmantissa.IPublicPage)

    installedOn = attributes.reference()
    powerupInterfaces = (ixmantissa.IPublicPage,)

    def getResource(self):
        return PublicIndexPage(self,
                ixmantissa.IStaticShellContent(self.store, None))



class PublicIndexPage(PublicPage):
    """
    PublicIndexPage is the resource which provides static content (such as CSS)
    and a splash page.
    """
    implements(ixmantissa.ICustomizable)

    title = 'Hyperbola'

    def __init__(self, original, staticContent, forUser=None):
        """
        Create a PublicIndexPage.

        @param original: a L{HyperbolaPublicPage}.

        @param staticContent: an L{ixmantissa.IStaticShellContent} provider.

        @param forUser: a unicode string, the identifier of the user to
        customize this store for.
        """
        super(PublicIndexPage, self).__init__(
                original,
                original.store.parent,
                tags.h1['Welcome to Hyperbola!'],
                staticContent,
                forUser)


    def customizeFor(self, forUser):
        """
        Implement L{ICustomizable.customizeFor} to return a version of this page
        with appropriate login/logout.
        """
        return self.__class__(self.original, self.staticContent, forUser)
