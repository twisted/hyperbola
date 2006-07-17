from xmantissa import webtheme
from nevow import tags

class HyperbolaTheme(webtheme.XHTMLDirectoryTheme):
    def head(self, website):
        root = website.cleartextRoot()
        yield tags.link(
            href=root + '/Hyperbola/static/hyperbola.css',
            rel='stylesheet',
            type='text/css')
        yield tags.script(
            src=root + '/Hyperbola/static/hyperbola.js',
            type='text/javascript')
