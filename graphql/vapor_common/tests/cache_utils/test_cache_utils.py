#!/usr/bin/env python
""" Tests for Vapor Common's Trust Utils

    Author: Erick Daniszewski
    Date:   12/22/2016
    
    \\//
     \/apor IO
"""
import unittest
import time

from vapor_common.utils.cache import Cache


class CacheUtilsTestCase(unittest.TestCase):

    def test_001_test_cache(self):
        """ Test the vapor common simple cache object

        In this case, we test getting a value that is not in the cache.
        """
        c = Cache(ttl=3)

        with self.assertRaises(KeyError):
            c['not_in_cache']

    def test_002_test_cache(self):
        """ Test the vapor common simple cache object

        In this case, we test getting a value that is not in the cache.
        """
        c = Cache(ttl=3)
        val = c.get('not-in-cache')

        self.assertEqual(val, None)

    def test_003_test_cache(self):
        """ Test the vapor common simple cache object

        In this case, we test getting a value that is not in the cache.
        """
        c = Cache(ttl=3)
        val = c.get('not-in-cache', 'default')

        self.assertEqual(val, 'default')

    def test_004_test_cache(self):
        """ Test the vapor common simple cache object

        In this case, we test adding an item to the cache
        """
        c = Cache(ttl=3)

        self.assertEqual(len(c), 0)

        c['key'] = 'value'

        self.assertEqual(len(c), 1)

    def test_005_test_cache(self):
        """ Test the vapor common simple cache object

        In this case, we test adding an item to the cache
        """
        c = Cache(ttl=3)

        self.assertEqual(len(c), 0)

        c.set('key', 'value')

        self.assertEqual(len(c), 1)

    def test_006_test_cache(self):
        """ Test the vapor common simple cache object

        In this case, we test checking inclusion in the cache
        """
        c = Cache(ttl=3)

        self.assertEqual(len(c), 0)

        c.set('key', 'value')

        self.assertEqual(len(c), 1)

        self.assertTrue('key' in c)

    def test_007_test_cache(self):
        """ Test the vapor common simple cache object

        In this case, we test getting an item from the cache
        """
        c = Cache(ttl=3)

        self.assertEqual(len(c), 0)

        c['key'] = 'value'

        self.assertEqual(len(c), 1)

        value = c['key']

        self.assertEqual(value, 'value')
        self.assertEqual(len(c), 1)

    def test_008_test_cache(self):
        """ Test the vapor common simple cache object

        In this case, we test getting an item from the cache
        """
        c = Cache(ttl=3)

        self.assertEqual(len(c), 0)

        c.set('key', 'value')

        self.assertEqual(len(c), 1)

        value = c.get('key')

        self.assertEqual(value, 'value')
        self.assertEqual(len(c), 1)

    def test_009_test_cache(self):
        """ Test the vapor common simple cache object

        In this test, we put it all together.
        """
        c = Cache(ttl=2)

        self.assertEqual(len(c), 0)

        c['key1'] = 1

        self.assertEqual(len(c), 1)

        value = c['key1']

        self.assertEqual(len(c), 1)
        self.assertEqual(value, 1)

        # now sleep 3s to get over the cache ttl
        time.sleep(3)

        # since items are removed lazily, we should still have
        # the entry in the cache.
        self.assertEqual(len(c), 1)

        with self.assertRaises(KeyError):
            value = c['key1']

        # now that we tried getting it, it should be removed
        self.assertEqual(len(c), 0)

    def test_010_test_cache(self):
        """ Test the vapor common simple cache object

        In this case, no ttl is specified.
        """
        c = Cache()

        self.assertEqual(len(c), 0)

        c['key2'] = 2

        self.assertEqual(len(c), 1)

        value = c['key2']

        self.assertEqual(len(c), 1)
        self.assertEqual(value, 2)

        # now sleep some time
        time.sleep(3)

        self.assertEqual(len(c), 1)

        value = c['key2']

        self.assertEqual(len(c), 1)
        self.assertEqual(value, 2)

    def test_011_test_cache(self):
        """ Test the vapor common simple cache object

        In this test, we put it all together.
        """
        c = Cache(ttl=2)

        self.assertEqual(len(c), 0)

        c.set('key1', 1)

        self.assertEqual(len(c), 1)

        value = c.get('key1')

        self.assertEqual(len(c), 1)
        self.assertEqual(value, 1)

        # now sleep 3s to get over the cache ttl
        time.sleep(3)

        # since items are removed lazily, we should still have
        # the entry in the cache.
        self.assertEqual(len(c), 1)

        value = c.get('key1')
        self.assertEqual(value, None)

        # now that we tried getting it, it should be removed
        self.assertEqual(len(c), 0)

    def test_012_test_cache(self):
        """ Test the vapor common simple cache object

        In this case, no ttl is specified.
        """
        c = Cache()

        self.assertEqual(len(c), 0)

        c.set('key2', 2)

        self.assertEqual(len(c), 1)

        value = c.get('key2')

        self.assertEqual(len(c), 1)
        self.assertEqual(value, 2)

        # now sleep some time
        time.sleep(3)

        self.assertEqual(len(c), 1)

        value = c.get('key2')

        self.assertEqual(len(c), 1)
        self.assertEqual(value, 2)

    def test_013_test_cache(self):
        """ Test the vapor common simple cache object

        In this test, we put it all together with multiple values
        """
        c = Cache(ttl=2)

        self.assertEqual(len(c), 0)

        c['key1'] = 1
        c['key2'] = 2
        c['key3'] = 3

        self.assertEqual(len(c), 3)

        value1 = c['key1']
        value2 = c['key2']
        value3 = c['key3']

        self.assertEqual(len(c), 3)
        self.assertEqual(value1, 1)
        self.assertEqual(value2, 2)
        self.assertEqual(value3, 3)

        # now sleep 3s to get over the cache ttl
        time.sleep(3)

        # since items are removed lazily, we should still have
        # the entry in the cache.
        self.assertEqual(len(c), 3)

        for k in ['key1', 'key2', 'key3']:
            with self.assertRaises(KeyError):
                value = c[k]

        # now that we tried getting it, it should be removed
        self.assertEqual(len(c), 0)

    def test_014_test_cache(self):
        """ Test the vapor common simple cache object

        In this test, we put it all together with multiple values
        """
        c = Cache(ttl=2)

        self.assertEqual(len(c), 0)

        c.set('key1', 1)
        c.set('key2', 2)
        c.set('key3', 3)

        self.assertEqual(len(c), 3)

        value1 = c.get('key1')
        value2 = c.get('key2')
        value3 = c.get('key3')

        self.assertEqual(len(c), 3)
        self.assertEqual(value1, 1)
        self.assertEqual(value2, 2)
        self.assertEqual(value3, 3)

        # now sleep 3s to get over the cache ttl
        time.sleep(3)

        # since items are removed lazily, we should still have
        # the entry in the cache.
        self.assertEqual(len(c), 3)

        for k in ['key1', 'key2', 'key3']:
            value = c.get(k)
            self.assertEqual(value, None)

        # now that we tried getting it, it should be removed
        self.assertEqual(len(c), 0)
