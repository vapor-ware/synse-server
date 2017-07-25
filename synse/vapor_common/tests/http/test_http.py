#!/usr/bin/env python
""" Tests for Vapor Common's HTTP wrapper

    Author: Erick Daniszewski
    Date:   12/23/2016
    
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

import unittest

import requests.exceptions as req
from vapor_common import http
from vapor_common.errors import VaporError, VaporHTTPError, VaporRequestError
from vapor_common.utils.cache import Cache


class MockResponse(object):
    """ Mock of the requests' Response object
    """
    def __init__(self, extra_headers={}, **kwargs):
        if 'headers' in kwargs:
            kwargs['headers'].update(extra_headers)
        else:
            self.headers = extra_headers

        self.status_code = 200

        # set the remaining values from kwargs
        for k, v in kwargs.iteritems():
            setattr(self, k, v)


class HTTPTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # re-initialize the cache for these tests.
        http._CACHE = Cache(ttl=300)

    def test_001_http(self):
        """ Test http get with mocked in responses giving back a
        "good" response.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse(**kwargs)

        http.requests.request = mock_request

        # run the test
        r = http.get('http://test.url')

        self.assertEqual(r.headers, {})
        self.assertEqual(r.status_code, 200)

    def test_002_http(self):
        """ Test http get with mocked in responses giving back a
        "good" response with headers.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse({'TEST_HEADER': 'value'}, **kwargs)

        http.requests.request = mock_request

        # run the test
        r = http.get('http://test.url')

        self.assertEqual(r.headers, {'TEST_HEADER': 'value'})
        self.assertEqual(r.status_code, 200)

    def test_003_http(self):
        """ Test http get with mocked in responses giving back a
        "bad" response.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            resp = MockResponse(**kwargs)
            resp.status_code = 500
            return resp

        http.requests.request = mock_request

        # run the test
        with self.assertRaises(VaporHTTPError):
            http.get('http://test.url')

    def test_004_http(self):
        """ Test http get with mocked in responses giving back a
        "bad" response with headers.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            resp = MockResponse({'TEST_HEADER': 'value'}, **kwargs)
            resp.status_code = 500
            return resp

        http.requests.request = mock_request

        # run the test
        with self.assertRaises(VaporHTTPError):
            http.get('http://test.url')

    def test_005_http(self):
        """ Test http get with mocked in responses giving back a
        "bad" response.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            resp = MockResponse(**kwargs)
            resp.status_code = 404
            return resp

        http.requests.request = mock_request

        # run the test
        with self.assertRaises(VaporHTTPError):
            http.get('http://test.url')

    def test_006_http(self):
        """ Test http get with mocked in responses giving back a
        "bad" response with headers.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            resp = MockResponse({'TEST_HEADER': 'value'}, **kwargs)
            resp.status_code = 404
            return resp

        http.requests.request = mock_request

        # run the test
        with self.assertRaises(VaporHTTPError):
            http.get('http://test.url')

    def test_007_http(self):
        """ Test http get with mocked in responses giving back a
        failed response.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            raise req.RequestException

        http.requests.request = mock_request

        # run the test
        with self.assertRaises(VaporRequestError):
            http.get('http://test.url')

    def test_008_http(self):
        """ Test http get with mocked in responses giving back a
        failed response with headers.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            raise req.RequestException

        http.requests.request = mock_request

        # run the test
        with self.assertRaises(VaporRequestError):
            http.get('http://test.url')

    def test_009_http(self):
        """ Test http get with mocked in responses giving back a
        failed response. In this case the failure is due to some
        unknown exception.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            raise Exception

        http.requests.request = mock_request

        # run the test
        with self.assertRaises(VaporError):
            http.get('http://test.url')

    def test_010_http(self):
        """ Test http get with mocked in responses giving back a
        failed response with headers. In this case the failure is
        due to some unknown exception.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            raise Exception

        http.requests.request = mock_request

        # run the test
        with self.assertRaises(VaporError):
            http.get('http://test.url')

    def test_011_http(self):
        """ Test http post with mocked in responses giving back a
        "good" response.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse(**kwargs)

        http.requests.request = mock_request

        # run the test
        r = http.post('http://test.url')

        self.assertEqual(r.headers, {})
        self.assertEqual(r.status_code, 200)

    def test_012_http(self):
        """ Test http post with mocked in responses giving back a
        "good" response with headers.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse({'TEST_HEADER': 'value'}, **kwargs)

        http.requests.request = mock_request

        # run the test
        r = http.post('http://test.url')

        self.assertEqual(r.headers, {'TEST_HEADER': 'value'})
        self.assertEqual(r.status_code, 200)

    def test_013_http(self):
        """ Test http post with mocked in responses giving back a
        "bad" response.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            resp = MockResponse(**kwargs)
            resp.status_code = 500
            return resp

        http.requests.request = mock_request

        # run the test
        with self.assertRaises(VaporHTTPError):
            http.post('http://test.url')

    def test_014_http(self):
        """ Test http post with mocked in responses giving back a
        "bad" response with headers.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            resp = MockResponse({'TEST_HEADER': 'value'}, **kwargs)
            resp.status_code = 500
            return resp

        http.requests.request = mock_request

        # run the test
        with self.assertRaises(VaporHTTPError):
            http.post('http://test.url')

    def test_015_http(self):
        """ Test http post with mocked in responses giving back a
        "bad" response.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            resp = MockResponse(**kwargs)
            resp.status_code = 404
            return resp

        http.requests.request = mock_request

        # run the test
        with self.assertRaises(VaporHTTPError):
            http.post('http://test.url')

    def test_016_http(self):
        """ Test http post with mocked in responses giving back a
        "bad" response with headers.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            resp = MockResponse({'TEST_HEADER': 'value'}, **kwargs)
            resp.status_code = 404
            return resp

        http.requests.request = mock_request

        # run the test
        with self.assertRaises(VaporHTTPError):
            http.post('http://test.url')

    def test_017_http(self):
        """ Test http post with mocked in responses giving back a
        failed response.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            raise req.RequestException

        http.requests.request = mock_request

        # run the test
        with self.assertRaises(VaporRequestError):
            http.post('http://test.url')

    def test_018_http(self):
        """ Test http post with mocked in responses giving back a
        failed response with headers.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            raise req.RequestException

        http.requests.request = mock_request

        # run the test
        with self.assertRaises(VaporRequestError):
            http.post('http://test.url')

    def test_019_http(self):
        """ Test http post with mocked in responses giving back a
        failed response. In this case the failure is due to some
        unknown exception.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            raise Exception

        http.requests.request = mock_request

        # run the test
        with self.assertRaises(VaporError):
            http.post('http://test.url')

    def test_020_http(self):
        """ Test http post with mocked in responses giving back a
        failed response with headers. In this case the failure is
        due to some unknown exception.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            raise Exception

        http.requests.request = mock_request

        # run the test
        with self.assertRaises(VaporError):
            http.post('http://test.url')

    def test_021_http(self):
        """ Test issuing an http call without providing the needed args.
        """
        with self.assertRaises(TypeError):
            http.get()

    def test_022_http(self):
        """ Test issuing an http call without providing the needed args.
        """
        with self.assertRaises(TypeError):
            http.post()

    def test_023_http(self):
        """ Test http get, passing in some kwargs as well. While not
        typically the case, we will have the response "echo" back all the
        kwargs to test that all the kwargs we set are making it to the
        request call.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse(**kwargs)

        http.requests.request = mock_request

        # run the test
        r = http.get('http://test.url', key1='test', timeout=10)

        self.assertEqual(r.headers, {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.key1, 'test')
        self.assertEqual(r.timeout, 10)
        self.assertEqual(r.method, http.GET)
        self.assertEqual(r.url, 'http://test.url')

    def test_024_http(self):
        """ Test http post, passing in some kwargs as well. While not
        typically the case, we will have the response "echo" back all the
        kwargs to test that all the kwargs we set are making it to the
        request call.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse(**kwargs)

        http.requests.request = mock_request

        # run the test
        r = http.post('http://test.url', key1='test', timeout=10)

        self.assertEqual(r.headers, {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.key1, 'test')
        self.assertEqual(r.timeout, 10)
        self.assertEqual(r.method, http.POST)
        self.assertEqual(r.url, 'http://test.url')
