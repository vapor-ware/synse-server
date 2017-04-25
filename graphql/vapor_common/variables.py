#!/usr/bin/env python
""" Common variable values which can be used by all Vapor Services.

    Author: Erick Daniszewski
    Date:   08/26/2016
    
    \\//
     \/apor IO
"""

# the ENV variable name in containers which support multi-modal execution (e.g.
# chamber mode vs. ipmi mode).
VAPOR_EXEC_MODE = 'VAPOR_EXEC_MODE'

# name of the service - this is primarily used for identifying services when
# attempting to pull down remotely-defined configuration overrides.
VAPOR_SERVICE_NAME = 'VAPOR_SERVICE_NAME'

# the ENV variable name which is used to specify the blocking behavior of
# container bootstrap on startup.
VAPOR_BOOTSTRAP_BLOCK = 'VAPOR_BOOTSTRAP_BLOCK'
