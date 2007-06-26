from epsilon.extime import Time

from axiom.store import Store
from axiom.dependency import installOn
from axiom.userbase import LoginSystem

from xmantissa import sharing, website

from hyperbola import hyperblurb
from hyperbola.hyperbola_model import HyperbolaPublicPresence

class HyperbolaTestMixin:
    """
    Mixin class providing various Hyperbola-specific test utilities
    """

    def _setUpStore(self):
        """
        Set up a store, install a L{HyperbolaPublicPresence} and its
        dependencies, and create a role
        """
        store = Store(self.mktemp())
        installOn(website.WebSite(store=store), store)

        self.loginSystem = LoginSystem(store=store)
        installOn(self.loginSystem, store)

        acct = self.loginSystem.addAccount(
            u'user', u'localhost', u'asdf', internal=True)
        self.store = acct.avatars.open()
        self.publicPresence = HyperbolaPublicPresence(store=self.store)
        installOn(self.publicPresence, self.store)

        self.role = sharing.Role(
            store=self.store,
            externalID=u'foo@host', description=u'foo')


    def _makeBlurb(self, flavor, title=None, body=None):
        """
        Make a minimal nonsense blurb with flavor C{flavor}

        @param flavor: the blurb flavor
        @type flavor: one of the C{unicode} L{hyperbola.hyperblurb.FLAVOR}
        constants

        @param title: the blurb title.  defaults to C{flavor}
        @type title: C{unicode}

        @param body: the blurb body.  defaults to C{flavor}
        @type body: C{unicode}

        @rtype: L{hyperbola.hyperblurb.Blurb}
        """
        if title is None:
            title = flavor
        if body is None:
            body = flavor
        return hyperblurb.Blurb(
            store=self.store,
            title=title,
            body=body,
            flavor=flavor,
            dateCreated=Time(),
            author=self.role)

    def _shareAndGetProxy(self, blurb):
        """
        Share C{blurb} to everyone and return a shared proxy

        @param blurb: a blurb
        @type blurb: L{hyperbola.hyperblurb.Blurb}

        @rtype: L{xmantissa.sharing.SharedProxy}
        """
        share = sharing.shareItem(blurb)
        return sharing.getShare(
            self.store,
            sharing.getEveryoneRole(self.store),
            share.shareID)
