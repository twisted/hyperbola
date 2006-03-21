from axiom.store import Store

from twisted.trial import unittest
from epsilon.extime import Time
from xmantissa.sharing import Role, getShare, itemFromProxy
from hyperbola import hyperbola_model, hyperblurb, ihyperbola

class BasicTest(unittest.TestCase):
    def setUp(self):
        self.store = Store()

    def testUserWroteTests(self):
        o = hyperbola_model.HyperbolaPublicPresence(
            store=self.store)

    def tearDown(self):
        self.store.close()



class BlurbTests(unittest.TestCase):
    def setUp(self):
        self.store = Store()

    def testPost(self):
        me = Role(store=self.store,
                  externalID=u'armstrong@example.com', description=u'foobar')
        you = Role(store=self.store,
                   externalID=u'radix@example.com', description=u'rad yo')
        blog = hyperblurb.Blurb(store=self.store, title=u"Hello World",
                                body=u"Hello World!~!!", author=me, hits=0,
                                dateCreated=Time(), dateLastEdited=Time(),
                                flavor=hyperblurb.FLAVOR.BLOG)

        blog.permitChildren(
            you, hyperblurb.FLAVOR.BLOG_POST, ihyperbola.ICommenter)

        blog.permitChildren(
            you, hyperblurb.FLAVOR.BLOG_COMMENT, ihyperbola.ICommenter)

        postShareID = blog.post(u'My First Post', u'Hello, Viewers', me)
        self.assertNotIdentical(postShareID, None)
        sharedPost = getShare(self.store, you, postShareID)
        commentShareID = sharedPost.post(u'My Comemnt To Your Post',
                                         u'Your Bolg Sucks, man', you)
        self.assertNotIdentical(commentShareID, None)
        sharedComment = getShare(self.store, you, commentShareID)
        self.assertIdentical(sharedComment.parent, itemFromProxy(sharedPost))

        self.assertRaises(AttributeError, lambda: sharedPost.edit(u'Ima Haxer',
                                                                  u'Haxed u',
                                                                  you))

        newTitle = u'My Comment To Your Post'
        newBody = u'Your Blog Sucks, man'
        sharedComment.edit(newTitle, newBody, you)
        self.assertEquals(sharedComment.body, newBody)
        self.assertEquals(sharedComment.title, newTitle)


    def tearDown(self):
        self.store.close()
