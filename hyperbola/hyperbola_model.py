# -*- test-case-name: hyperbola.test.test_hyperbola -*-


from zope.interface import implements

from epsilon.extime import Time

from axiom.item import Item, InstallableMixin
from axiom.attributes import integer, reference

from xmantissa import ixmantissa, website, webapp, webnav, tdb, sharing

from twisted.python.components import registerAdapter

from hyperbola.hyperbola_view import HyperbolaView
from hyperbola.hyperblurb import Blurb

class HyperbolaBenefactor(Item):
    '''i am responsible for granting priveleges to avatars,
       which equates to installing stuff in their store'''
    implements(ixmantissa.IBenefactor)

    typeName = 'hyperbola_benefactor'
    schemaVersion = 1

    # Number of users this benefactor has endowed
    endowed = integer(default = 0)

    def installOn(self, other):
        other.powerUp(self, ixmantissa.IBenefactor)


    def endow(self, ticket, avatar):
        self.endowed += 1
        # The user will be able to access the application using the
        # HTTP Protocol
        avatar.findOrCreate(website.WebSite).installOn(avatar)

        # The user will be able to use private applications written for
        # Mantissa and installed in his substore.
        avatar.findOrCreate(webapp.PrivateApplication).installOn(avatar)

        # Install this new application in the user substore (avatar) so that
        # he will be able to use it.
        avatar.findOrCreate(HyperbolaPublicPresence).installOn(avatar)


    def deprive(self, ticket, avatar):
        app = avatar.findFirst(HyperbolaPublicPresence)
        app.deleteFromStore()



class HyperbolaPublicPresence(Item, InstallableMixin):
    # This object can be browsed from the web
    implements(ixmantissa.INavigableElement)

    schemaVersion = 1                  # First version of this object.
    typeName = 'hyperbola_start'       # Database table name.

    installedOn = reference()

    def installOn(self, other):
        super(HyperbolaPublicPresence, self).installOn(other)
        other.powerUp(self, ixmantissa.INavigableElement)

    def getTabs(self):
        return [webnav.Tab('Hyperbola', self.storeID, 0)]

    def getTDM(self):
        """
        Return a TabularDataModel listing all the blogs in this store.
        """
        return tdb.TabularDataModel(self.store, Blurb,
                                    [Blurb.title, Blurb.dateCreated],
                                    Blurb.parent == None)

    def topPost(self, title, description, flavor):
        now = Time()
        return Blurb(
            store=self.store,
            dateCreated=now,
            dateLastEdited=now,
            title=title,
            body=description,
            flavor=flavor,
            author=sharing.getSelfRole(self.store))

# Notify the system that this Fragment class will be responsible of
# rendering the model. The 'self.original' attribute of the HyperbolaView
# instance is actually an instance of the HyperbolaPublicPresence class.
registerAdapter(HyperbolaView, HyperbolaPublicPresence, ixmantissa.INavigableFragment)

