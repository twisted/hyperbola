# -*- test-case-name: hyperbola.test.test_theme -*-

"""
This module contains a Mantissa web theme plugin which includes Hyperbola's
style information.
"""

from xmantissa import webtheme
from nevow import tags

class HyperbolaTheme(webtheme.XHTMLDirectoryTheme):
    """
    Hyperbola's style information, which resides in the 'static' directory.
    """
    def head(self, req, website):
        root = website.cleartextRoot(req.getHeader('host'))
        static = root.child('Hyperbola').child('static')
        yield tags.link(
            href=static.child('hyperbola.css'),
            rel='stylesheet',
            type='text/css')
