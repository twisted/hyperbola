from epsilon.extime import Time

from axiom.store import Store
from axiom.dependency import installOn

from xmantissa import sharing

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
        store = Store()
        installOn(HyperbolaPublicPresence(store=store), store)
        self.role = sharing.Role(
            store=store,
            externalID=u'foo@host', description=u'foo')
        self.store = store

    def _makeBlurb(self, flavor):
        """
        Make a minimal nonsense blurb with flavor C{flavor}

        @param flavor: the blurb flavor
        @type flavor: one of the C{unicode} L{hyperbola.hyperblurb.FLAVOR}
        constants

        @rtype: L{hyperbola.hyperblurb.Blurb}
        """
        return hyperblurb.Blurb(
            store=self.store,
            title=flavor,
            body=flavor,
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
