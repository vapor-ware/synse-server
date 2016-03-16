#!/usr/bin/env python
"""
    Vapor Configuration Manager
    This module contains the configuration manager, a common component among
    Vapor projects. The configuration manager expects the config files which
    it operates on to be json files.

    Author: erick
    Date:   01/12/2016

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
import json


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
    def __init__(self, path=None):
        """ Constructor for the ConfigManager class.

        The constructor will attempt to read in and parse a configuration file,
        if specified. If the file does not exist, or the file contents are not
        JSON-parsable, an exception will be raised.

        Args:
            path (str): The path to the configuration file to read in. If no
                path is provided, no configuration is loaded, but the config
                manager still initializes and can update its context dynamically
                at runtime. (default: None)

        Raises:
            IOError: Specified file does not exist.
            ValueError: File contents are not JSON-parsable.
        """
        self.__path = path

        if self.__path:
            # no exception handling here because we want the exception to propagate
            # upwards. if a file is specified but doesn't exist, or if the file
            # contents are not json-parsable, its not a problem we can fix here.
            with open(self.__path, 'r') as f:
                json_config = json.load(f)
            self.add_config(json_config)

    def __getitem__(self, item):
        """ Get an item from the object __dict__ """
        try:
            return self.__dict__[item]
        except Exception:
            raise AttributeError

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

        Returns:
            None

        Raises:
            ValueError: No path is specified for the config file to write out to.
        """
        path = path if path else self.__path
        if not path:
            raise ValueError('No path specified for config write.')
        with open(path, 'w+') as f:
            f.seek(0)

            cfg_dict = {k: v for (k, v) in self.__dict__.copy().iteritems() if not k.startswith("_")}
            json.dump(cfg_dict, f)
