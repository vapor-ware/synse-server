#!/usr/bin/env python
""" Tests for Vapor Common's Package Setup.
This collection of tests should run first in any collection of tests for
this package. Ideally all tests in this suite should only read package
information. Let's make sure that this suite is reentrant.

    \\//
     \/apor IO
"""

import logging
import os
import unittest

from vapor_common.constants import LICENSE_PATH
from vapor_common.constants import PACKAGE_INSTALL_DIR
from vapor_common.errors import TestException

logger = logging.getLogger(__name__)

# FUTURE: Make class more generic. Should be able to test any package setup.

# The name of the package.
PACKAGE_NAME = 'vapor_common'
# The full path of where the package should be installed.
PACKAGE_DIR = os.path.join(PACKAGE_INSTALL_DIR, PACKAGE_NAME)


def find_all_files_named(file_name, path):
    """Find all files with an explict name.
    :param file_name: The explicit file name to look for.
    :param path: The path to look under."""
    result = []
    for root, dirs, files in os.walk(path):
        if file_name in files:
            result.append(os.path.join(root, file_name))
    logger.debug('find_all_files_named returns: {}'.format(result))
    return result


def find_file_where_expected_once(expected_path, file_name):
    """FInd a file exactly once in the container in the expected path.
    :param expected_path: The expected full path of the file.
    :param file_name: The file name to search for. No wildcards.
    :raises: TestException if the file was not found once in the expected
    path."""
    # Find all files with the fileName in the root.
    result = find_all_files_named(file_name, '/')

    if len(result) == 0:
        logger.error('find_file_where_expected_once result: {}'.format(result))
        raise TestException(
            'Expected file named {}, but not found.'.format(file_name))
    elif len(result) > 1:
        logger.error('find_file_where_expected_once result: {}'.format(result))
        raise TestException(
            'Expected file named {} found more than once: result'.format(
                file_name, result))
    elif result[0] != expected_path:
        logger.error('find_file_where_expected_once result: {}'.format(result))
        raise TestException(
            'Expected path {} is not the actual path {}.'.format(
                expected_path, result[0]))


def test_files_where_expected_once(base_path, relative_path, *file_names):
    """Test that a set of files exist where expected once.
    :param base_path: Base path of where the file would be installed.
    :param relative_path: Relative path of where the file should be installed.
    :param file_names: Array of file names to check.
    :raises: TestException on failure."""
    for file_name in file_names:
        expected_path = os.path.join(base_path, relative_path, file_name)
        find_file_where_expected_once(expected_path, file_name)


# CONSIDER: Should be run as setUpClass. If it fails then the setup failed.
# CONSIDER: Should be run as tearDownClass.
# CONSIDER: If tear down fails then the test set is nonreentant. (Left files around.)
# CONSIDER: PackageTestClass(package_name) inheriting from uniittest.
class TestVaporCommonPackageSetup(unittest.TestCase):
    """TODO: Class needs to be more generic."""

    def test_package_files(self):
        """Make sure that we setup the  expected files where expected and
         nowhere else."""

        # Make sure that PACKAGE_DIR is set correctly.
        self.assertEqual('/usr/local/lib/python2.7/dist-packages/vapor_common', PACKAGE_DIR)

        # Make sure the vapor_common directory exists in the test container.
        self.assertTrue(os.path.isdir(PACKAGE_DIR))

        # Test that the certs are not installed by default.
        cert = os.path.join(LICENSE_PATH, 'test.crt')
        self.assertFalse(os.path.isfile(cert))
        key = os.path.join(LICENSE_PATH, 'test.key')
        self.assertFalse(os.path.isfile(key))

        # Test each line / file in the data files of setup.py.
        test_files_where_expected_once(
            PACKAGE_DIR,
            'tests/data',
            'config.json')

        test_files_where_expected_once(
            PACKAGE_DIR,
            'tests/data',
            'invalid_contents.json')

        test_files_where_expected_once(
            PACKAGE_DIR,
            'tests/data/default',
            'default.json')

        test_files_where_expected_once(
            PACKAGE_DIR,
            'tests/data/override2',
            'test_file.json')

        test_files_where_expected_once(
            PACKAGE_DIR,
            'tests/data/override3',
            'test_config.json')

        # Ensure the test function works. Directory does not exist.
        with self.assertRaises(TestException):
            test_files_where_expected_once(
                PACKAGE_DIR,
                'directory_does_not_exist',
                'not_a_real_file.zvz')

        # Ensure the test function works. Directory exists but not file.
        with self.assertRaises(TestException):
            test_files_where_expected_once(
                PACKAGE_DIR,
                '.',
                'not_a_real_file.zvz')
