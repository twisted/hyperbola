from xmantissa import webtheme
from nevow import tags

class HyperbolaTheme(webtheme.XHTMLDirectoryTheme):
    def head(self):
        yield tags.link(href='/static/hyperbola/hyperbola.css',
                        rel='stylesheet', type='text/css')
        yield tags.script(src='/static/hyperbola/hyperbola.js',
                          type='text/javascript')

