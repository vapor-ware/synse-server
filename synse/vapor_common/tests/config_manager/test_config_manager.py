#!/usr/bin/env python
""" Vapor Common Configuration Manager Tests

    Author:  Erick Daniszewski
    Date:    10/16/2015

    \\//
     \/apor IO
"""
import json
import os
import unittest

from vapor_common.constants import PACKAGE_INSTALL_DIR
from vapor_common.vapor_config import ConfigManager


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
        base_dir = os.path.join(PACKAGE_INSTALL_DIR, 'vapor_common', 'tests')

        cls.nonexistent_file = os.path.join(base_dir, 'data/not_a_file.json')
        cls.invalid_file = os.path.join(base_dir, 'data/invalid_contents.json')
        cls.valid_file = os.path.join(base_dir, 'data/config.json')
        cls.out_file = os.path.join(base_dir, 'data/out.json')

        cls.default_file = os.path.join(base_dir, 'data/default/default.json')
        cls.empty_override = os.path.join(base_dir, 'data/override1')
        cls.invalid_override = os.path.join(base_dir, 'data/override2')
        cls.valid_override = os.path.join(base_dir, 'data/override3')

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
        # plus 2 for internally tracked state.
        self.assertEqual(len(cfg.__dict__), 9)

    def test_003_config_manager(self):
        """ Test initializing the config manager with no file.
        """
        with self.assertRaises(ValueError):
            ConfigManager('')

    def test_004_config_manager(self):
        """ Test initializing the config manager with invalid arguments.
        """
        with self.assertRaises(ValueError):
            ConfigManager(None)

    def test_005_config_manager(self):
        """ Test adding to the config context, adding single values that do not
        overwrite existing.
        """
        cfg = ConfigManager(self.default_file)

        self.assertNotIn('value10', cfg.__dict__)
        cfg.value10 = 5000
        self.assertIn('value10', cfg.__dict__)

    def test_006_config_manager(self):
        """ Test adding to the config context, adding single values that do
        overwrite existing.
        """
        cfg = ConfigManager(self.default_file)

        self.assertNotIn('value10', cfg.__dict__)
        cfg.value10 = 5000
        self.assertIn('value10', cfg.__dict__)
        self.assertEqual(cfg.value10, 5000)
        cfg.value10 = 'new-value'
        self.assertIn('value10', cfg.__dict__)
        self.assertEqual(cfg.value10, 'new-value')

    def test_007_config_manager(self):
        """ Test adding to the config context, adding multiple values that do not
        overwrite existing.
        """
        cfg = ConfigManager(self.default_file)

        to_add = {
            'value10': 5000,
            'value20': 'test',
            'value30': False
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
        cfg = ConfigManager(self.default_file)

        to_add = {
            'value10': 5000,
            'value20': 'test',
            'value30': False
        }

        for k, v in to_add.iteritems():
            self.assertNotIn(k, cfg.__dict__)

        cfg.add_config(to_add)

        for k, v in to_add.iteritems():
            self.assertIn(k, cfg.__dict__)
            self.assertEqual(cfg.__dict__[k], v)

        new_add = {
            'value20': 'test2',
            'value30': True,
            'value40': None
        }

        cfg.add_config(new_add)

        expected = {
            'value10': 5000,
            'value20': 'test2',
            'value30': True,
            'value40': None
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
        """ Test initializing with only a default file.
        """
        with open(self.default_file, 'r') as f:
            default = json.load(f)

        cfg = ConfigManager(self.default_file)

        for k, v in default.iteritems():
            self.assertIn(k, cfg.__dict__)
            self.assertEqual(v, cfg.__dict__[k])

    def test_012_config_manager(self):
        """ Test initializing with a default file and empty override.
        """
        with open(self.default_file, 'r') as f:
            default = json.load(f)

        cfg = ConfigManager(self.default_file, self.empty_override)

        for k, v in default.iteritems():
            self.assertIn(k, cfg.__dict__)
            self.assertEqual(v, cfg.__dict__[k])

    def test_013_config_manager(self):
        """ Test initializing with a default file and invalid override.
        """
        with open(self.default_file, 'r') as f:
            default = json.load(f)

        cfg = ConfigManager(self.default_file, self.invalid_override)

        for k, v in default.iteritems():
            self.assertIn(k, cfg.__dict__)
            self.assertEqual(v, cfg.__dict__[k])

    def test_014_config_manager(self):
        """ Test initializing with a default file and valid override.
        """
        with open(self.default_file, 'r') as f:
            default = json.load(f)

        with open(os.path.join(self.valid_override, 'test_config.json'), 'r') as f:
            override = json.load(f)

        cfg = ConfigManager(self.default_file, self.valid_override)

        default.update(override)
        for k, v in default.iteritems():
            self.assertIn(k, cfg.__dict__)
            self.assertEqual(v, cfg.__dict__[k])

    def test_015_config_manager(self):
        """ Test initializing with a default file and override which does not exist.
        """
        with open(self.default_file, 'r') as f:
            default = json.load(f)

        cfg = ConfigManager(self.default_file, './not/a/path')

        for k, v in default.iteritems():
            self.assertIn(k, cfg.__dict__)
            self.assertEqual(v, cfg.__dict__[k])

    def test_016_config_manager(self):
        """ Test regex filename matching. In this case, all supplied names should match.
        """
        cfg = ConfigManager(self.default_file)

        filenames = [
            'config.json',
            'CONFIG.json',
            'config.JSON',
            'CONFIG.JSON',
            'CoNfIg.JsOn',
            'test_config.json',
            'config_test.json',
            'configuration.json',
            'service-config.json',
            'service.config.json'
        ]

        results = cfg._find_config_matches(filenames)

        self.assertEqual(len(results), len(filenames))
        self.assertEqual(results, filenames)

    def test_017_config_manager(self):
        """ Test regex filename matching. In this case, none of the supplied names should match.
        """
        cfg = ConfigManager(self.default_file)

        filenames = [
            'config',
            'configuration',
            'CONFIG',
            'CONFIGURATION',
            'CoNfIg',
            'config.yml',
            'config.jsn',
            'cfg.json',
            'test_confg.json',
            'cfg_test.json'
        ]

        results = cfg._find_config_matches(filenames)

        self.assertEqual(len(results), 0)
