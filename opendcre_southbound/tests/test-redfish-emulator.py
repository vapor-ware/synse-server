import unittest
import logging
from vapor_common.test_utils import run_suite, exit_suite

from redfish_emulator.test_redfish_emulator import RedfishTestCase

def get_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RedfishTestCase))
    return suite

if __name__ == '__main__':
    result = run_suite('test-redfish-emulator', get_suite(), loglevel=logging.INFO)
    exit_suite(result)