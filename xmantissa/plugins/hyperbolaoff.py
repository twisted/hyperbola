from axiom import userbase

from xmantissa import website, offering

from hyperbola import hyperbola_model
from hyperbola.hyperbola_theme import HyperbolaTheme


plugin = offering.Offering(
    name = u"Hyperbola",

    description = u"""
    This is the wonderful Hyperbola application. Click me to install.
    """,

    siteRequirements = (
        (userbase.IRealm, userbase.LoginSystem),
        (None, website.WebSite)),

    appPowerups = (
        ),
    installablePowerups = (),
    loginInterfaces = (),
    themes = (HyperbolaTheme('base', 0),)
    )

