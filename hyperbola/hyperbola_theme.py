# -*- test-case-name: hyperbola.test.test_theme -*-
from xmantissa import webtheme
from nevow import tags

class HyperbolaTheme(webtheme.XHTMLDirectoryTheme):
    def head(self, req, website):
        root = website.cleartextRoot(req.getHeader('host'))
        static = root.child('Hyperbola').child('static')
        yield tags.link(
            href=static.child('hyperbola.css'),
            rel='stylesheet',
            type='text/css')
        yield tags.script(
            src=static.child('hyperbola.js'),
            type='text/javascript')
