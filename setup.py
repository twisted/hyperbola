from epsilon import setuphelper

from hyperbola import version

setuphelper.autosetup(
    name="Hyperbola",
    version=version.short(),
    maintainer="Divmod, Inc.",
    maintainer_email="support@divmod.org",
    url="http://divmod.org/trac/wiki/DivmodHyperbola",
    license="MIT",
    platforms=["any"],
    description=
        """
        Divmod Hyperbola is a blogging platform developed as an Offering for
        Divmod Mantissa.
        """,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Internet"],
    )
