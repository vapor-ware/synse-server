#!/usr/bin/env python
""" Tests for Vapor Common's HTTP wrapper

    Author: Erick Daniszewski
    Date:   12/23/2016
    
    \\//
     \/apor IO
"""
import os
import hashlib
import unittest
import requests.exceptions as req

from vapor_common import http
from vapor_common.constants import LICENSE_PATH
from vapor_common.errors import VaporHTTPError, VaporRequestError, VaporError
from vapor_common.headers import VAPOR_IDENTITY_HASH
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


class HTTPTrustedTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        http._trust_enabled = True

        cls.cert_data = 'abcdefghi1234567'
        cls.cert_hash = hashlib.sha256(cls.cert_data).hexdigest()

        if not os.path.isdir(LICENSE_PATH):
            os.makedirs(LICENSE_PATH)

        with open(os.path.join(LICENSE_PATH, 'test.crt'), 'w+') as f:
            f.write(cls.cert_data)

        # re-initialize the cache for these tests.
        http._CACHE = Cache(ttl=300)

    def test_000_http(self):
        """ First, validate that trust is not enabled.
        """
        self.assertTrue(http._trust_enabled)

    def test_001_http(self):
        """ Test http get with mocked in responses giving back a
        "good" response. In this case, the identity cert exists so the
        hash can be generated.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse(**kwargs)

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 0)

        r = http.get('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

        self.assertEqual(r.headers, {VAPOR_IDENTITY_HASH: self.cert_hash})
        self.assertEqual(r.status_code, 200)

    def test_002_http(self):
        """ Test http get with mocked in responses giving back a
        "good" response. In this case, the identity cert exists so the
        hash can be generated. The identity should now be in the hash cache.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse(**kwargs)

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        r = http.get('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

        self.assertEqual(r.headers, {VAPOR_IDENTITY_HASH: self.cert_hash})
        self.assertEqual(r.status_code, 200)

    def test_003_http(self):
        """ Test http get with mocked in responses giving back a
        "good" response. In this case, the identity cert exists so the
        hash can be generated. The identity should now be in the hash cache.

        Now, we add in kwargs to the headers to make sure nothing gets overridden.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse(**kwargs)

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        r = http.get('http://test.url', headers={})

        self.assertEqual(len(http._CACHE), 1)

        self.assertEqual(r.headers, {VAPOR_IDENTITY_HASH: self.cert_hash})
        self.assertEqual(r.status_code, 200)

    def test_004_http(self):
        """ Test http get with mocked in responses giving back a
        "good" response. In this case, the identity cert exists so the
        hash can be generated. The identity should now be in the hash cache.

        Now, we add in kwargs to the headers to make sure nothing gets overridden.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse(**kwargs)

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        r = http.get('http://test.url', headers={'TEST_HEADER': '1'})

        self.assertEqual(len(http._CACHE), 1)

        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            r.headers,
            {
                VAPOR_IDENTITY_HASH: self.cert_hash,
                'TEST_HEADER': '1'
            }
        )

    def test_005_http(self):
        """ Test http get with mocked in responses giving back a
        "good" response. In this case, the identity cert exists so the
        hash can be generated. The identity should now be in the hash cache.

        Now, we add in kwargs to the headers to make sure nothing gets overridden.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse(**kwargs)

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        r = http.get('http://test.url', headers={'TEST_HEADER': '1', 'ANOTHER-HEADER': 'test'})

        self.assertEqual(len(http._CACHE), 1)

        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            r.headers,
            {
                VAPOR_IDENTITY_HASH: self.cert_hash,
                'TEST_HEADER': '1',
                'ANOTHER-HEADER': 'test'
            }
        )

    def test_006_http(self):
        """ Test http get with mocked in responses giving back a
        "good" response. In this case, the identity cert exists so the
        hash can be generated. The identity should now be in the hash cache.

        Specifying the identity hash in the header here should result in it
        getting overwritten.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse(**kwargs)

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        r = http.get('http://test.url', headers={VAPOR_IDENTITY_HASH: 'test'})

        self.assertEqual(len(http._CACHE), 1)

        self.assertEqual(r.headers, {VAPOR_IDENTITY_HASH: self.cert_hash})
        self.assertEqual(r.status_code, 200)

    def test_007_http(self):
        """ Test http get with mocked in responses giving back a
        "bad" response. Since trust is not enabled, there should be
        no additional changes to the response.
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

    def test_008_http(self):
        """ Test http get with mocked in responses giving back a
        "bad" response with headers. Since trust is not enabled, there
        should be no additional changes to the response.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            resp = MockResponse({'TEST_HEADER': 'value'}, **kwargs)
            resp.status_code = 500
            return resp

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        with self.assertRaises(VaporHTTPError):
            http.get('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

    def test_009_http(self):
        """ Test http get with mocked in responses giving back a
        "bad" response. Since trust is not enabled, there should be
        no additional changes to the response.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            resp = MockResponse(**kwargs)
            resp.status_code = 404
            return resp

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        with self.assertRaises(VaporHTTPError):
            http.get('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

    def test_010_http(self):
        """ Test http get with mocked in responses giving back a
        "bad" response with headers. Since trust is not enabled, there
        should be no additional changes to the response.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            resp = MockResponse({'TEST_HEADER': 'value'}, **kwargs)
            resp.status_code = 404
            return resp

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        with self.assertRaises(VaporHTTPError):
            http.get('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

    def test_011_http(self):
        """ Test http get with mocked in responses giving back a
        failed response.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            raise req.RequestException

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        with self.assertRaises(VaporRequestError):
            http.get('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

    def test_012_http(self):
        """ Test http get with mocked in responses giving back a
        failed response with headers.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            raise req.RequestException

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        with self.assertRaises(VaporRequestError):
            http.get('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

    def test_013_http(self):
        """ Test http get with mocked in responses giving back a
        failed response. In this case the failure is due to some
        unknown exception.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            raise Exception

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        with self.assertRaises(VaporError):
            http.get('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

    def test_014_http(self):
        """ Test http get with mocked in responses giving back a
        failed response with headers. In this case the failure is
        due to some unknown exception.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            raise Exception

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        with self.assertRaises(VaporError):
            http.get('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

    def test_015_http(self):
        """ Test http post with mocked in responses giving back a
        "good" response. In this case, the identity cert exists so the
        hash can be generated.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse(**kwargs)

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        r = http.post('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

        self.assertEqual(r.headers, {VAPOR_IDENTITY_HASH: self.cert_hash})
        self.assertEqual(r.status_code, 200)

    def test_016_http(self):
        """ Test http post with mocked in responses giving back a
        "good" response. In this case, the identity cert exists so the
        hash can be generated. The identity should now be in the hash cache.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse(**kwargs)

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        r = http.post('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

        self.assertEqual(r.headers, {VAPOR_IDENTITY_HASH: self.cert_hash})
        self.assertEqual(r.status_code, 200)

    def test_017_http(self):
        """ Test http post with mocked in responses giving back a
        "good" response. In this case, the identity cert exists so the
        hash can be generated. The identity should now be in the hash cache.

        Now, we add in kwargs to the headers to make sure nothing gets overridden.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse(**kwargs)

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        r = http.post('http://test.url', headers={})

        self.assertEqual(len(http._CACHE), 1)

        self.assertEqual(r.headers, {VAPOR_IDENTITY_HASH: self.cert_hash})
        self.assertEqual(r.status_code, 200)

    def test_018_http(self):
        """ Test http post with mocked in responses giving back a
        "good" response. In this case, the identity cert exists so the
        hash can be generated. The identity should now be in the hash cache.

        Now, we add in kwargs to the headers to make sure nothing gets overridden.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse(**kwargs)

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        r = http.post('http://test.url', headers={'TEST_HEADER': '1'})

        self.assertEqual(len(http._CACHE), 1)

        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            r.headers,
            {
                VAPOR_IDENTITY_HASH: self.cert_hash,
                'TEST_HEADER': '1'
            }
        )

    def test_019_http(self):
        """ Test http post with mocked in responses giving back a
        "good" response. In this case, the identity cert exists so the
        hash can be generated. The identity should now be in the hash cache.

        Now, we add in kwargs to the headers to make sure nothing gets overridden.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse(**kwargs)

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        r = http.post('http://test.url', headers={'TEST_HEADER': '1', 'ANOTHER-HEADER': 'test'})

        self.assertEqual(len(http._CACHE), 1)

        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            r.headers,
            {
                VAPOR_IDENTITY_HASH: self.cert_hash,
                'TEST_HEADER': '1',
                'ANOTHER-HEADER': 'test'
            }
        )

    def test_020_http(self):
        """ Test http post with mocked in responses giving back a
        "good" response. In this case, the identity cert exists so the
        hash can be generated. The identity should now be in the hash cache.

        Specifying the identity hash in the header here should result in it
        getting overwritten.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            return MockResponse(**kwargs)

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        r = http.post('http://test.url', headers={VAPOR_IDENTITY_HASH: 'test'})

        self.assertEqual(len(http._CACHE), 1)

        self.assertEqual(r.headers, {VAPOR_IDENTITY_HASH: self.cert_hash})
        self.assertEqual(r.status_code, 200)

    def test_021_http(self):
        """ Test http post with mocked in responses giving back a
        "bad" response. Since trust is not enabled, there should be
        no additional changes to the response.
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

    def test_022_http(self):
        """ Test http post with mocked in responses giving back a
        "bad" response with headers. Since trust is not enabled, there
        should be no additional changes to the response.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            resp = MockResponse({'TEST_HEADER': 'value'}, **kwargs)
            resp.status_code = 500
            return resp

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        with self.assertRaises(VaporHTTPError):
            http.post('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

    def test_023_http(self):
        """ Test http post with mocked in responses giving back a
        "bad" response. Since trust is not enabled, there should be
        no additional changes to the response.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            resp = MockResponse(**kwargs)
            resp.status_code = 404
            return resp

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        with self.assertRaises(VaporHTTPError):
            http.post('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

    def test_024_http(self):
        """ Test http post with mocked in responses giving back a
        "bad" response with headers. Since trust is not enabled, there
        should be no additional changes to the response.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            resp = MockResponse({'TEST_HEADER': 'value'}, **kwargs)
            resp.status_code = 404
            return resp

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        with self.assertRaises(VaporHTTPError):
            http.post('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

    def test_025_http(self):
        """ Test http post with mocked in responses giving back a
        failed response.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            raise req.RequestException

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        with self.assertRaises(VaporRequestError):
            http.post('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

    def test_026_http(self):
        """ Test http post with mocked in responses giving back a
        failed response with headers.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            raise req.RequestException

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        with self.assertRaises(VaporRequestError):
            http.post('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

    def test_027_http(self):
        """ Test http post with mocked in responses giving back a
        failed response. In this case the failure is due to some
        unknown exception.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            raise Exception

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        with self.assertRaises(VaporError):
            http.post('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

    def test_028_http(self):
        """ Test http post with mocked in responses giving back a
        failed response with headers. In this case the failure is
        due to some unknown exception.
        """
        # set up the mock test data
        def mock_request(**kwargs):
            raise Exception

        http.requests.request = mock_request

        # run the test
        self.assertEqual(len(http._CACHE), 1)

        with self.assertRaises(VaporError):
            http.post('http://test.url')

        self.assertEqual(len(http._CACHE), 1)

    def test_029_http(self):
        """ Test issuing an http call without providing the needed args.
        """
        with self.assertRaises(TypeError):
            http.get()

    def test_030_http(self):
        """ Test issuing an http call without providing the needed args.
        """
        with self.assertRaises(TypeError):
            http.post()

    def test_031_http(self):
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

        self.assertEqual(r.headers, {VAPOR_IDENTITY_HASH: self.cert_hash})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.key1, 'test')
        self.assertEqual(r.timeout, 10)
        self.assertEqual(r.method, http.GET)
        self.assertEqual(r.url, 'http://test.url')

    def test_032_http(self):
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

        self.assertEqual(r.headers, {VAPOR_IDENTITY_HASH: self.cert_hash})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.key1, 'test')
        self.assertEqual(r.timeout, 10)
        self.assertEqual(r.method, http.POST)
        self.assertEqual(r.url, 'http://test.url')
