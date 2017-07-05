#!/usr/bin/env python
""" Vapor Configuration Manager

This module contains the configuration manager, a common component among
Vapor projects. The configuration manager expects the config files which
it operates on to be json files.

    Author: Erick Daniszewski
    Date:   01/12/2016

    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

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
import json
import logging
import os
import re

logger = logging.getLogger()


class ConfigManager(object):
    """ The config manager reads and writes JSON-formatted configuration files.

    The contents of a read-in JSON file become attributes of the object. No
    validation is done on the contents of the JSON (e.g. for value type/value).
    The config options are then accessible via dot notation on the config
    object.

    Configuration files can also be written out, using the internal object dict
    to generate the JSON file.

    Note that when writing out the config JSON, the ConfigManager will ignore
    any attribute which starts with "_" (reserved for object private members).
    Accordingly, values in the config JSON should never start with "_".
    """
    def __init__(self, default, override=None):
        """ Constructor for the ConfigManager class.

        The constructor will attempt to read in and parse a configuration file,
        if specified. If the file does not exist, or the file contents are not
        JSON-parsable, an exception will be raised.

        Args:
            default (str): the default path to the configuration file to read in.
            override (str): the path to the directory containing the user-defined config.
                the config manager will search the directory for a file with the string
                'config' (case insensitive) in it with a JSON file extension. if no such
                file exists, nothing will be used as the override config. if multiple files
                match, nothing will be used as the override config.

        Raises:
            IOError: Specified file does not exist.
            ValueError: File contents are not JSON-parsable.
        """
        self._default = default
        self._override = override

        if self._default:
            # no exception handling here because we want the exception to propagate
            # upwards. if a file is specified but doesn't exist, or if the file
            # contents are not json-parsable, its not a problem we can fix here.
            with open(self._default, 'r') as f:
                default_config = json.load(f)
            self.add_config(default_config)
        else:
            raise ValueError('No/invalid default configuration provided: {}'.format(default))

        if self._override:
            try:
                dir_contents = os.listdir(self._override)
                matching = self._find_config_matches(dir_contents)

                match_count = len(matching)
                if match_count == 1:
                    with open(os.path.join(self._override, matching[0]), 'r') as f:
                        override_config = json.load(f)
                    self.add_config(override_config)

                elif match_count > 1:
                    logger.warning(
                        'Found {} files for override config, but was expecting 1: {}'.format(match_count, matching)
                    )

            except OSError as e:
                logger.error('Given override path is invalid: {}'.format(e))
            except Exception as e:
                logger.error('Unexpected exception when searching for override file: {}'.format(e))

    def __getitem__(self, item):
        """ Get an item from the object __dict__ """
        try:
            return self.__dict__[item]
        except Exception:
            raise AttributeError

    @staticmethod
    def _find_config_matches(dir_contents):
        """ Apply the regex search to the list of directory contents to get
        a list of items which match.

        Args:
            dir_contents (list): a list of strings, each of which the regex will
                be applied to.

        Returns:
            list: a list of items which match the regex. an empty list if nothing
                matches the regex.
        """
        return [i for i in dir_contents if re.search(r'.*(config).*\.json', i, re.IGNORECASE)]

    def add_config(self, to_add):
        """ Batch add values to the config manager.

        All values specified in the given dictionary will be added as attributes
        of the object, accessible through dot notation. Note that if a key defined
        in the given dictionary already exists as an attribute of the object, the
        existing value will be overwritten.

        Args:
            to_add (dict): A dictionary of values to add to the config manager's
                context.

        Returns:
            None
        """
        for k, v in to_add.iteritems():
            setattr(self, k, v)

    def write(self, path=None):
        """ Write the ConfigManager's context to a json config file.

        Args:
            path (str): The path of the configuration file to write to. If no
                path is given, the class' path member is used. (default: None)

        Raises:
            ValueError: No path is specified for the config file to write out to.
        """
        path = path if path else self._default
        if not path:
            raise ValueError('No path specified for config write.')
        with open(path, 'w+') as f:
            f.seek(0)

            cfg_dict = {k: v for (k, v) in self.__dict__.copy().iteritems() if not k.startswith("_")}
            json.dump(cfg_dict, f)
