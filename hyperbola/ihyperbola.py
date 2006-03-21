
from zope.interface import Interface, Attribute

class IViewer(Interface):
    title = Attribute('')
    body = Attribute('')

    dateLastEdited = Attribute('')
    dateCreated = Attribute('')

    author = Attribute('')
    flavor = Attribute('')
    hits = Attribute('')

    parent = Attribute('')

class ICommenter(IViewer):
    def post():
        pass

class IAuthor(ICommenter):
    def edit():
        pass

