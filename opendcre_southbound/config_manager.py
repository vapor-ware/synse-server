#!/usr/bin/env python
"""
OpenDCRE Configuration Manager
Author:  erick
Date:    9/13/2015

    \\//
     \/apor IO

Copyright (C) 2015-16  Vapor IO

This file is part of OpenDCRE.

OpenDCRE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

OpenDCRE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenDCRE.  If not, see <http://www.gnu.org/licenses/>.
"""
import ConfigParser
import logging
import os
import sys

logger = logging.getLogger()

__all__ = ['ConfigManager']

# define default configurations for items which may be missing from the opendcre
# config file. Note that in the default dict, everything is a string.
DEFAULT_CONFIG = {
    'opendcre-southbound': {
        'endpoint_prefix': '/opendcre/',
        'port':            '5000',
        'lockfile':        '/tmp/OpenDCRE.lock',
        'debug':           'False',
        'serial_default':  '/dev/ttyAMA0',
        'bus_baud':        '115200',
        'ssl_enable':      'False',
        'retry_limit':     '3',
        'time_slice':      '75'
    }
}


class ConfigManager(ConfigParser.SafeConfigParser, object):
    """
    The ConfigManager class acts as an interface to the OpenDCRE configuration
    file for read only operations. The class provides a set of convenience functions
    which wrap the operations of Python's ConfigParser.SafeConfigParser.

    If no section is provided, a value of 'DEFAULT' is used.
    """
    def __init__(self, config_file, section=None):
        super(ConfigManager, self).__init__()

        self.config_file = [config_file, '../opendcre_config.json', 'opendcre_config.json']
        self.current_section = section if section else 'DEFAULT'

        self.__validate_config()
        self.read(config_file)

    def __validate_config(self):
        """
        Validate that a file exists at the specified config file path. If the
        file does not exist, log an error and exit the program.
        """
        if isinstance(self.config_file, basestring):
            self.config_file = [self.config_file]
        has_valid_config = False
        for cfg in self.config_file:
            if os.path.isfile(cfg):
                has_valid_config = True
                break
        if not has_valid_config:
            self.__no_file_error()

    def get_value(self, name, type=None):
        """
        Get the value for a named identifier in the config file. This uses the
        ConfigManager's current_section member, which should either be specified
        on initialization, or can be set with the set_section method. If no value
        was specified for the current section, None is returned.

        The default return type is string. If a different return type is desired,
        it should be specified with the type argument. Supported alternative types
        are `int`, `float`, `bool`.

        In cases where it may be more convenient to provide both section and
        name for a given value, use SafeConfigParser's get(section, name)
        """
        if type is not None:
            if type == int:
                return self.getint(self.current_section, name)
            if type == float:
                return self.getfloat(self.current_section, name)
            if type == bool:
                return self.getboolean(self.current_section, name)

        return self.get(self.current_section, name)

    def set_section(self, section):
        """
        Set the current working section
        """
        if section in self.sections():
            self.current_section = section
        else:
            self.__no_section_error(section)

    def dump_config_state(self):
        """
        Dumps the current state of the configuration.

        This method is intended to be used for debugging purposes to gain visibility
        into the state of OpenDCRE configurations at any given time. This method
        returns a list of (name, value) pairs for each section in the configuration.
        """
        dump = []
        for section in self.sections():
            dump.append(('SECTION', section))
            for name_vale in self.items(section):
                dump.append(name_vale)
        return dump

    def _fallback_lookup(self, section, option):
        """
        A fallback method to lookup config option values from a default configuration
        in the event that the specified option was not found in the specified config
        file.
        """
        logger.info('executing fallback lookup for section:option > {}:{}'.format(section, option))
        if section in DEFAULT_CONFIG:
            section_defaults = DEFAULT_CONFIG[section]
            if option in section_defaults:
                default_option = section_defaults[option]
                logger.info('using default value "{}" for option "{}"'.format(default_option, option))
                return default_option
            else:
                self.__no_option_error(section, option)
        else:
            self.__no_section_error(section)

    # -----------------------------------------------------
    # Overridden methods for custom exception handling
    # -----------------------------------------------------

    def get(self, section, option, raw=False, vars=None):
        """ Override SafeConfigParser's get() method to include opendcre error handling """
        try:
            result = super(ConfigManager, self).get(section, option, raw, vars)
            if not result:
                result = self._fallback_lookup(section, option)
            return result

        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            return self._fallback_lookup(section, option)

    def getboolean(self, section, option):
        """ Override SafeConfigParser's getboolean() method to include opendcre error handling """
        try:
            result = super(ConfigManager, self).getboolean(section, option)
            # need to check strict equality to the boolean literals, or else valid responses
            # will enter the conditional
            if not result == True and not result == False:
                result = self._fallback_lookup(section, option)
            return result

        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            return self._fallback_lookup(section, option)

    def getfloat(self, section, option):
        """ Override SafeConfigParser's getfloat() method to include opendcre error handling """
        try:
            result = super(ConfigManager, self).getfloat(section, option)
            if not result:
                result = self._fallback_lookup(section, option)
            return result

        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            return self._fallback_lookup(section, option)

    def getint(self, section, option):
        """ Override SafeConfigParser's getint() method to include opendcre error handling """
        try:
            result = super(ConfigManager, self).getint(section, option)
            if not result:
                result = self._fallback_lookup(section, option)
            return result

        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            return self._fallback_lookup(section, option)

    # -----------------------------------------------------
    # class methods for handling common errors
    # -----------------------------------------------------

    def __no_file_error(self):
        """
        The specified config file does not exist - log an error and exit.
        """
        err_msg = 'Specified config file does not exist: "{}"'.format(self.config_file)
        logger.error(err_msg)
        sys.exit(err_msg)

    def __no_section_error(self, section):
        """
        The specified section does not exist within the config file - log an error and exit.
        """
        err_msg = 'Specified config section name "{}" not found within config file.'.format(section)
        logger.error(err_msg)
        sys.exit(err_msg)

    def __no_option_error(self, section, option):
        """
        The specified option within the specified section does not exist. For the ConfigManager
        class, this should only be used within the fallback lookup method if a specified option
        was not found in the default configuration.
        """
        err_msg = 'Specified option "{0}" not found in section "{1}" within the config file'.format(option, section)
        logger.error(err_msg)
        sys.exit(err_msg)
