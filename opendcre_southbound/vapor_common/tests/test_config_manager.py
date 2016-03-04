#!/usr/bin/env python
"""
    Crate Manifest Endpoint endurance tests

    Author:  erick
    Date:    10/16/2015

        \\//
         \/apor IO
"""
import json
import os
import unittest

from vapor_config import ConfigManager


class ConfigurationManagerTestCase(unittest.TestCase):
    """ Tests for the vapor common configuration manager
    """
    test_cfg = {
        "none_value": None,
        "bool_value": True,
        "string_value": "value1",
        "int_value": 5000,
        "float_value": 1.234,
        "list_value": [1, 2, 3, 4],
        "dict_value": {
            "val1": 1,
            "val2": 2
        }
    }

    @classmethod
    def setUpClass(cls):
        cls.nonexistent_file = './tests/data/not_a_file.json'
        cls.invalid_file = './tests/data/invalid_contents.json'
        cls.valid_file = './tests/data/config.json'
        cls.out_file = './tests/data/out.json'

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.out_file):
            os.remove(cls.out_file)

    def tearDown(self):
        with open(self.valid_file, 'w') as f:
            f.seek(0)
            json.dump(self.test_cfg, f)

    def test_000_config_manager(self):
        """ Test initializing the config manager with a nonexistent file.
        """
        with self.assertRaises(IOError):
            ConfigManager(self.nonexistent_file)

    def test_001_config_manager(self):
        """ Test initializing the config manager with an invalid json file.
        """
        with self.assertRaises(ValueError):
            ConfigManager(self.invalid_file)

    def test_002_config_manager(self):
        """ Test initializing the config manager with a valid file.
        """
        cfg = ConfigManager(self.valid_file)

        self.assertEqual(cfg.none_value, None)
        self.assertEqual(cfg.bool_value, True)
        self.assertEqual(cfg.string_value, 'value1')
        self.assertEqual(cfg.int_value, 5000)
        self.assertEqual(cfg.float_value, 1.234)
        self.assertEqual(cfg.list_value, [1, 2, 3, 4])
        self.assertEqual(cfg.dict_value, {'val1': 1, 'val2': 2})

        self.assertEqual(cfg['none_value'], None)
        self.assertEqual(cfg['bool_value'], True)
        self.assertEqual(cfg['string_value'], 'value1')
        self.assertEqual(cfg['int_value'], 5000)
        self.assertEqual(cfg['float_value'], 1.234)
        self.assertEqual(cfg['list_value'], [1, 2, 3, 4])
        self.assertEqual(cfg['dict_value'], {'val1': 1, 'val2': 2})

        with self.assertRaises(AttributeError):
            cfg['not_a_key']

        with self.assertRaises(AttributeError):
            cfg.not_a_key

        # should be of len 8 -> 7 for the number of values in the config file,
        # plus 1 for internally tracked state.
        self.assertEqual(len(cfg.__dict__), 8)

    def test_003_config_manager(self):
        """ Test initializing the config manager with no file.
        """
        cfg = ConfigManager()

        # should be of len 1 -> 0 for the number of values in the config file,
        # plus 1 for internally tracked state.
        self.assertEqual(len(cfg.__dict__), 1)

    def test_004_config_manager(self):
        """ Test initializing the config manager with invalid arguments.
        """
        ConfigManager(None)

    def test_005_config_manager(self):
        """ Test adding to the config context, adding single values that do not
        overwrite existing.
        """
        cfg = ConfigManager()

        self.assertNotIn('value1', cfg.__dict__)
        cfg.value1 = 5000
        self.assertIn('value1', cfg.__dict__)

    def test_006_config_manager(self):
        """ Test adding to the config context, adding single values that do
        overwrite existing.
        """
        cfg = ConfigManager()

        self.assertNotIn('value1', cfg.__dict__)
        cfg.value1 = 5000
        self.assertIn('value1', cfg.__dict__)
        self.assertEqual(cfg.value1, 5000)
        cfg.value1 = 'new-value'
        self.assertIn('value1', cfg.__dict__)
        self.assertEqual(cfg.value1, 'new-value')

    def test_007_config_manager(self):
        """ Test adding to the config context, adding multiple values that do not
        overwrite existing.
        """
        cfg = ConfigManager()

        to_add = {
            'value1': 5000,
            'value2': 'test',
            'value3': False
        }

        for k, v in to_add.iteritems():
            self.assertNotIn(k, cfg.__dict__)

        cfg.add_config(to_add)

        for k, v in to_add.iteritems():
            self.assertIn(k, cfg.__dict__)
            self.assertEqual(cfg.__dict__[k], v)

    def test_008_config_manager(self):
        """ Test adding to the config context, adding multiple values that do
        overwrite existing.
        """
        cfg = ConfigManager()

        to_add = {
            'value1': 5000,
            'value2': 'test',
            'value3': False
        }

        for k, v in to_add.iteritems():
            self.assertNotIn(k, cfg.__dict__)

        cfg.add_config(to_add)

        for k, v in to_add.iteritems():
            self.assertIn(k, cfg.__dict__)
            self.assertEqual(cfg.__dict__[k], v)

        new_add = {
            'value2': 'test2',
            'value3': True,
            'value4': None
        }

        cfg.add_config(new_add)

        expected = {
            'value1': 5000,
            'value2': 'test2',
            'value3': True,
            'value4': None
        }

        for k, v in expected.iteritems():
            self.assertIn(k, cfg.__dict__)
            self.assertEqual(cfg.__dict__[k], v)

    def test_009_config_manager(self):
        """ Test writing config to a specified output file.
        """
        with open(self.valid_file, 'r') as f:
            old_json = json.load(f)

        cfg = ConfigManager(self.valid_file)
        cfg.write(self.valid_file)

        with open(self.valid_file, 'r') as f:
            new_json = json.load(f)

        self.assertEqual(old_json, new_json)

    def test_010_config_manager(self):
        """ Test writing config out, using the internally-specified config file.
        """
        with open(self.valid_file, 'r') as f:
            old_json = json.load(f)

        cfg = ConfigManager(self.valid_file)
        cfg.write()

        with open(self.valid_file, 'r') as f:
            new_json = json.load(f)

        self.assertEqual(old_json, new_json)

    def test_011_config_manager(self):
        """ Test writing config out, with no output file specified.
        """
        cfg = ConfigManager()
        with self.assertRaises(ValueError):
            cfg.write()
