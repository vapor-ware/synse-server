#!/usr/bin/env python
""" Tests for Vapor Common's Trust Utils

    Author: Erick Daniszewski
    Date:   12/06/2016
    
    \\//
     \/apor IO
"""
import unittest
import os
import errno
import hashlib
import shutil

from werkzeug.contrib.cache import SimpleCache
from bson import ObjectId

from vapor_common.utils import trust
from vapor_common.constants import LICENSE_PATH


class MockRequest(object):
    """ Mock object for the Flask Request object to be used in unittests.
    """
    def __init__(self, remote_addr='127.0.0.1'):
        self.remote_addr = remote_addr


class MockVec(object):
    """ Mock object for a Vec.
    """
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)


# we will want to mock out the crate_api.utils.identity utils here so that
# we have no dependencies on crate_api for these tests. below are three methods
# which will be used to override which simulate the possible outcomes from that
# method: (i) return None, (ii) return a Vec, (iii) raise an exception
def get_vec_with_identity_override_1(manifest_host, identity_hash):
    return None


def get_vec_with_identity_override_2(manifest_host, identity_hash):
    vec_data = {
        'ip': '127.0.0.1',
        'hostname': 'vec001',
        'cluster_id': 'cluster_1',
        'mgmt_unit_id': 1,
        'region_id': 1,
        'service_profile': str(ObjectId()),
        'is_vec_leader': False,
        'is_crate_primary': False,
        'rack_id': "rack_1",
        'identity_hash': identity_hash
    }
    return MockVec(**vec_data)


def get_vec_with_identity_override_3(manifest_host, identity_hash):
    raise ValueError('test exception')


class TrustUtilsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.manifest_ip = 'manifest-endpoint-x64'

    def test_001_get_local_hash(self):
        """ Test getting the local hash when the license directory does not exist.
        """
        res = trust.get_local_hash()
        self.assertIsNone(res)

    def test_002_get_local_hash(self):
        """ Test getting the local hash when the license directory does exist but
        does not contain any certs.
        """
        try:
            os.makedirs(LICENSE_PATH)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(LICENSE_PATH):
                pass
            else:
                raise

        res = trust.get_local_hash()
        self.assertIsNone(res)

    def test_003_get_local_hash(self):
        """ Test getting the local hash when the license directory contains multiple
        certs.
        """
        file1 = os.path.join(LICENSE_PATH, 'file1.crt')
        file2 = os.path.join(LICENSE_PATH, 'file2.crt')

        with open(file1, 'w') as f:
            f.write('123')

        with open(file2, 'w') as f:
            f.write('456')

        with self.assertRaises(ValueError):
            trust.get_local_hash()

        # now, remove the files for the next test.
        os.remove(file1)
        os.remove(file2)

    def test_004_get_local_hash(self):
        """ Test getting the local hash when the license directory contains files
        without the crt ending.
        """
        file1 = os.path.join(LICENSE_PATH, 'file1.csv')
        file2 = os.path.join(LICENSE_PATH, 'file2.txt')

        with open(file1, 'w') as f:
            f.write('123')

        with open(file2, 'w') as f:
            f.write('456')

        res = trust.get_local_hash()
        self.assertIsNone(res)

        # now, remove the files for the next test.
        os.remove(file1)
        os.remove(file2)

    def test_005_get_local_hash(self):
        """ Test getting the local hash when a valid cert exists.
        """
        file1 = os.path.join(LICENSE_PATH, 'file1.crt')
        contents = 'abc123'

        with open(file1, 'w') as f:
            f.write(contents)

        res = trust.get_local_hash()
        self.assertIsInstance(res, basestring)

        calculated_hash = hashlib.sha256(contents).hexdigest()

        self.assertEqual(res, calculated_hash)

        # now, remove the files for the next test.
        os.remove(file1)

    def test_006_get_local_hash(self):
        """ Test getting the local hash when the license directory contains files
        without the crt ending and a file with the crt ending.
        """
        file1 = os.path.join(LICENSE_PATH, 'file1.csv')
        file2 = os.path.join(LICENSE_PATH, 'file2.txt')
        file3 = os.path.join(LICENSE_PATH, 'file3.crt')
        contents = 'def456'

        with open(file1, 'w') as f:
            f.write('123')

        with open(file2, 'w') as f:
            f.write('456')

        with open(file3, 'w') as f:
            f.write(contents)

        res = trust.get_local_hash()
        self.assertIsInstance(res, basestring)

        calculated_hash = hashlib.sha256(contents).hexdigest()

        self.assertEqual(res, calculated_hash)

        # now, remove the files for the next test.
        os.remove(file1)
        os.remove(file2)
        os.remove(file3)

    def test_007_check_local_trust(self):
        """ Check if the incoming identity hash is trusted by virtue of it being a
        local request.

        In this case, there is no cert directory defined locally, so we expect a
        return of False
        """
        if os.path.isdir(LICENSE_PATH):
            shutil.rmtree(LICENSE_PATH)

        cache = SimpleCache()

        data = 'abc'
        ret = trust.check_local_trust(cache, hashlib.sha256(data).hexdigest())

        self.assertEqual(ret, False)
        self.assertIsNone(cache.get('local_hash'))

    def test_008_check_local_trust(self):
        """ Check if the incoming identity hash is trusted by virtue of it being a
        local request.

        In this case, there is no cert defined locally, so we expect a return of
        False
        """
        try:
            os.makedirs(LICENSE_PATH)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(LICENSE_PATH):
                pass
            else:
                raise

        cache = SimpleCache()

        data = 'abc'
        ret = trust.check_local_trust(cache, hashlib.sha256(data).hexdigest())

        self.assertEqual(ret, False)
        self.assertIsNone(cache.get('local_hash'))

    def test_009_check_local_trust(self):
        """ Check if the incoming identity hash is trusted by virtue of it being a
        local request.

        In this case, the cert is defined locally, but it does not match the incoming
        hash.
        """
        cert_data = 'abcdef'

        with open(os.path.join(LICENSE_PATH, 'test.crt'), 'w') as f:
            f.write(cert_data)

        cache = SimpleCache()

        hash_data = '123345'
        ret = trust.check_local_trust(cache, hashlib.sha256(hash_data).hexdigest())

        self.assertEqual(ret, False)
        self.assertEqual(cache.get('local_hash'), hashlib.sha256(cert_data).hexdigest())

    def test_010_check_local_trust(self):
        """ Check if the incoming identity hash is trusted by virtue of it being a
        local request.

        In this case, the cert is defined locally, and it does match the incoming hash.
        """
        cert_data = 'abcdef'

        with open(os.path.join(LICENSE_PATH, 'test.crt'), 'w') as f:
            f.write(cert_data)

        cache = SimpleCache()
        ret = trust.check_local_trust(cache, hashlib.sha256(cert_data).hexdigest())

        self.assertEqual(ret, True)
        self.assertEqual(cache.get('local_hash'), hashlib.sha256(cert_data).hexdigest())

    def test_011_check_local_trust(self):
        """ Check if the incoming identity hash is trusted by virtue of it being a
        local request.

        In this case, the certs should match and the second time around, we expect the
        same result (testing that the cache does work).
        """
        cert_data = 'abcdef'

        with open(os.path.join(LICENSE_PATH, 'test.crt'), 'w') as f:
            f.write(cert_data)

        cache = SimpleCache()
        ret = trust.check_local_trust(cache, hashlib.sha256(cert_data).hexdigest())

        self.assertEqual(ret, True)
        self.assertEqual(cache.get('local_hash'), hashlib.sha256(cert_data).hexdigest())

        ret = trust.check_local_trust(cache, hashlib.sha256(cert_data).hexdigest())

        self.assertEqual(ret, True)
        self.assertEqual(cache.get('local_hash'), hashlib.sha256(cert_data).hexdigest())

    def test_012_check_local_trust(self):
        """ Check if the incoming identity hash is trusted by virtue of it being a
        local request.

        In this case, the cache already has the correct hash value in it.
        """
        cert_data = 'abcdef'

        cache = SimpleCache()
        cache.set('local_hash', hashlib.sha256(cert_data).hexdigest())

        ret = trust.check_local_trust(cache, hashlib.sha256(cert_data).hexdigest())

        self.assertEqual(ret, True)
        self.assertEqual(cache.get('local_hash'), hashlib.sha256(cert_data).hexdigest())

    def test_013_check_local_trust(self):
        """ Check if the incoming identity hash is trusted by virtue of it being a
        local request.

        In this case, the cache has an incorrect hash value in it.
        """
        cert_data = 'abcdef'
        hash_data = '123456'

        cache = SimpleCache()
        cache.set('local_hash', hashlib.sha256(cert_data).hexdigest())

        ret = trust.check_local_trust(cache, hashlib.sha256(hash_data).hexdigest())

        self.assertEqual(ret, False)
        self.assertEqual(cache.get('local_hash'), hashlib.sha256(cert_data).hexdigest())

    def test_014_validate_ipmi_mode(self):
        """ Test the validation for vec identity when the Vec is running in IPMI mode.

        First, test when crate is not enabled. We expect this to return False.
        """
        trust.crate_enabled = False

        data = 'abcdef'
        cache = SimpleCache()
        request = MockRequest()
        identity_hash = hashlib.sha256(data).hexdigest()

        ret = trust.validate_ipmi_mode(cache, request, identity_hash, self.manifest_ip)
        self.assertEqual(ret, False)

        # revert crate_enabled to True for subsequent tests
        trust.crate_enabled = True

    def test_015_validate_ipmi_mode(self):
        """ Test the validation for vec identity when the Vec is running in IPMI mode.

        Test validating the identity hash when it is already stored in the cache and
        it matches the requesting address.
        """
        data = 'abcdef'
        identity_hash = hashlib.sha256(data).hexdigest()

        vec_data = {
            'ip': '127.0.0.1',
            'hostname': 'vec001',
            'cluster_id': 'cluster_1',
            'mgmt_unit_id': 1,
            'region_id': 1,
            'service_profile': str(ObjectId()),
            'is_vec_leader': False,
            'is_crate_primary': False,
            'rack_id': "rack_1",
            'identity_hash': identity_hash
        }

        vec = MockVec(**vec_data)
        cache = SimpleCache()
        request = MockRequest(remote_addr='127.0.0.1')

        # put the record in the cache
        cache.set(identity_hash, vec)

        ret = trust.validate_ipmi_mode(cache, request, identity_hash, self.manifest_ip)
        self.assertEqual(ret, True)

    def test_016_validate_ipmi_mode(self):
        """ Test the validation for vec identity when the Vec is running in IPMI mode.

        Test validating the identity hash when it is already stored in the cache and
        it does not match the requesting address.
        """
        data = 'abcdef'
        identity_hash = hashlib.sha256(data).hexdigest()

        vec_data = {
            'ip': '127.0.0.1',
            'hostname': 'vec001',
            'cluster_id': 'cluster_1',
            'mgmt_unit_id': 1,
            'region_id': 1,
            'service_profile': str(ObjectId()),
            'is_vec_leader': False,
            'is_crate_primary': False,
            'rack_id': "rack_1",
            'identity_hash': identity_hash
        }

        vec = MockVec(**vec_data)
        cache = SimpleCache()
        request = MockRequest(remote_addr='127.0.0.2')

        # put the record in the cache
        cache.set(identity_hash, vec)

        ret = trust.validate_ipmi_mode(cache, request, identity_hash, self.manifest_ip)
        self.assertEqual(ret, False)

    def test_017_validate_ipmi_mode(self):
        """ Test the validation for vec identity when the Vec is running in IPMI mode.

        Test validating the identity hash when it is not already stored in the cache and
        the manifest instance is unreachable.

        In this case, Manifest unreachable is simulated by patching in an override method
        which raises an exception, which we would expect if the Manifest were actually
        unavailable/unresponsive/etc
        """
        trust.get_vec_with_identity = get_vec_with_identity_override_3

        data = 'abcdef'
        identity_hash = hashlib.sha256(data).hexdigest()
        cache = SimpleCache()
        request = MockRequest(remote_addr='127.0.0.1')

        ret = trust.validate_ipmi_mode(cache, request, identity_hash, 'not-a-real-manifest')
        self.assertEqual(ret, False)

    def test_018_validate_ipmi_mode(self):
        """ Test the validation for vec identity when the Vec is running in IPMI mode.

        Test validating the identity hash when it is not already stored in the cache and
        must be looked up from Manifest. When looked up, it does match.

        Here, we will override the Crate functionality for test isolation.
        """
        trust.get_vec_with_identity = get_vec_with_identity_override_2

        data = 'abcdef'
        identity_hash = hashlib.sha256(data).hexdigest()

        cache = SimpleCache()
        request = MockRequest(remote_addr='127.0.0.1')

        # verify there is nothing in the cache pre-validation
        data = cache.get(identity_hash)
        self.assertIsNone(data)

        ret = trust.validate_ipmi_mode(cache, request, identity_hash, self.manifest_ip)
        self.assertEqual(ret, True)

        # now check that the new value was added to the cache.
        data = cache.get(identity_hash)
        self.assertIsNotNone(data)

    def test_019_validate_ipmi_mode(self):
        """ Test the validation for vec identity when the Vec is running in IPMI mode.

        Test validating the identity hash when it is not already stored in the cache and
        must be looked up from Manifest. When looked up, there is no matching VEC with
        that hash (untrusted)

        Here, we will override the Crate functionality for test isolation.
        """
        trust.get_vec_with_identity = get_vec_with_identity_override_1

        data = 'abcdef'
        identity_hash = hashlib.sha256(data).hexdigest()

        cache = SimpleCache()
        request = MockRequest(remote_addr='127.0.0.1')

        # verify there is nothing in the cache pre-validation
        data = cache.get(identity_hash)
        self.assertIsNone(data)

        ret = trust.validate_ipmi_mode(cache, request, identity_hash, self.manifest_ip)
        self.assertEqual(ret, False)

        # now check that the new value was added to the cache.
        data = cache.get(identity_hash)
        self.assertIsNone(data)

    def test_020_validate_ipmi_mode(self):
        """ Test the validation for vec identity when the Vec is running in IPMI mode.

        Test validating the identity hash when it is not already stored in the cache and
        must be looked up from Manifest. When looked up, it does not match.
        """
        trust.get_vec_with_identity = get_vec_with_identity_override_2

        data = 'abcdef'
        identity_hash = hashlib.sha256(data).hexdigest()

        cache = SimpleCache()
        request = MockRequest(remote_addr='127.0.0.2')

        # verify there is nothing in the cache pre-validation
        data = cache.get(identity_hash)
        self.assertIsNone(data)

        ret = trust.validate_ipmi_mode(cache, request, identity_hash, self.manifest_ip)
        self.assertEqual(ret, False)

        # now check that the new value was added to the cache.
        data = cache.get(identity_hash)
        self.assertIsNotNone(data)
