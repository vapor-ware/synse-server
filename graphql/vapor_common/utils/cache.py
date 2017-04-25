#!/usr/bin/env python
""" Vapor Common caching utilities

    Author: Erick Daniszewski
    Date:   22 Dec 2016
    
    \\//
     \/apor IO
"""
import collections
import time


class Cache(collections.MutableMapping):
    """ Simple implementation of a TTL cache.

    The Cache object wraps an internal dictionary that is used to
    store the cache data. A TTL can also be specified. If the TTL
    is specified as `None`, the cache entries will live there
    indefinitely.

    Items from the cache are checked and removed lazily on `get`.
    """
    def __init__(self, ttl=None):
        super(Cache, self).__init__()
        self._cache = dict()
        self.ttl = ttl

    def __getitem__(self, key):
        v, t = self._cache[key]

        if self.ttl is not None and time.time() - t > self.ttl:
            self.__delitem__(key)
            raise KeyError

        return v

    def __setitem__(self, key, value):
        self._cache[key] = (value, time.time())

    def __delitem__(self, key):
        del self._cache[key]

    def __iter__(self):
        return iter(self._cache)

    def __len__(self):
        return len(self._cache)

    def set(self, key, value):
        self.__setitem__(key, value)
