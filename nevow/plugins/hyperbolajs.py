
from twisted.python import filepath

from nevow import athena

import hyperbola

hyperbolaJS = athena.JSPackage({
        u'Hyperbola': filepath.FilePath(hyperbola.__file__).parent(
            ).child('static').child('hyperbola.js').path})
