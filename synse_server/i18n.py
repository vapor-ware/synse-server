"""Localization and internationalization helpers for Synse Server."""

import gettext
import os

# TODO (etd): see if there is a better way of defining this.. perhaps
#  in the Synse obj in server.py?
#  could also look at how other projects handle this

_here = os.path.dirname(os.path.realpath(__file__))

# Here, we are not setting the translation to fall back onto anything.
# The default value that will be picked up via config is en_US. The only
# time the locale will change is if it is configured by the user -- if
# the given locale is incorrect or unsupported, we want this to fail so
# they know right away.
t = gettext.translation('synse_server', os.path.join(_here, 'locale'))
_ = t.gettext
