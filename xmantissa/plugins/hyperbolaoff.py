from axiom import iaxiom, userbase

from xmantissa import website, offering, provisioning

import hyperbola

from hyperbola import hyperbola_model
from hyperbola.hyperbola_theme import HyperbolaTheme

hyperbolaer = provisioning.BenefactorFactory(
    name = u'hyperbolaer',
    description = u'A wonderful ready to use application named Hyperbola',
    benefactorClass = hyperbola_model.HyperbolaBenefactor)

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

    benefactorFactories = (hyperbolaer,),
    loginInterfaces = (),
    themes = (HyperbolaTheme('base', 0),)
    )

