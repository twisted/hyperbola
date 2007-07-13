
"""
This module is a plugin for Mantissa which provides a Hyperbola offering.
"""


from axiom import userbase

from xmantissa import website, offering

from hyperbola import hyperbola_model
from hyperbola.hyperbola_theme import HyperbolaTheme
from hyperbola.publicpage import HyperbolaPublicPage


plugin = offering.Offering(
    name = u"Hyperbola",

    description = u"""
    A basic weblog system.
    """,

    siteRequirements = (
        (userbase.IRealm, userbase.LoginSystem),
        (None, website.WebSite)),

    appPowerups = (HyperbolaPublicPage,),
    installablePowerups = [(
        u'Publisher',
        u'Allows publishing of posts in a weblog format.',
        hyperbola_model.HyperbolaPublicPresence)],
    loginInterfaces = (),
    themes = (HyperbolaTheme('base', 0),)
    )

