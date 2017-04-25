#!/usr/bin/env python
""" General argument checking not specific to OpenDCRE.

    \\//
     \/apor IO
"""

import logging

logger = logging.getLogger(__name__)


class ArgumentChecker(object):
    """The intention of this class is provide static methods for checking
    input parameters in functions or methods and kick the caller out if the
    argument is not usable by the called function or method.
    If a parameter is invalid:
        - TypeError is thrown if the input type is unexpected.
        - ValueError is thrown if the type is correct but the input value is
        unexpected."""
    @staticmethod
    def check_instance(expected_type, variable):
        """If the variable is not an instance of the specified type, raise a ValueError."""
        if not isinstance(variable, expected_type):
            raise TypeError('Expected instance {}, got {}'.format(expected_type, variable.__class__))
        return variable

    @staticmethod
    def check_type(expected_type, variable):
        """If the type(variable) is not the specified type, raise a ValueError."""
        if not type(variable) != expected_type:
            raise TypeError('Expected type {}, got {}'.format(expected_type, type(variable)))
        return variable
