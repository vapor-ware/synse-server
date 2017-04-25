#!/usr/bin/env python
""" Vapor Unittest Timing Base

    Author: Erick Daniszewski
    Date:   01/26/2016

    \\//
     \/apor IO
"""
import unittest
import time
import sys
import logging


class VaporBaseTestCase(unittest.TestCase):
    """ Base class for Vapor test cases.

    The VaporBaseTestCase subclasses unittest.TestCase in order to add timing
    output to the tests that run. If the test case completes successfully, the
    TextRunner output should include the times it took for each test to complete.

    This timing information can be useful for finding bottlenecks in the code.
    """
    view_test_times = False

    @classmethod
    def setUpClass(cls):
        cls.test_times = []

    @classmethod
    def tearDownClass(cls):
        if cls.view_test_times:
            print "{:<8} {:<25}".format('-' * 7, '-' * 25)
            print "{:<8} {:<25}".format('Time', 'Test')
            print "{:<8} {:<25}".format('-' * 7, '-' * 25)
            for _test, _time in cls.test_times:
                print "{:<8.3f} {:<25}".format(_time, _test)

    def setUp(self):
        self.start_time = time.time()

    def tearDown(self):
        t = time.time() - self.start_time
        self.test_times.append((self.id().split('.')[-1], t))


class Tee(object):
    """ The Tee object gets its name from the unix tee command since the two do
    fundamentally similar things - it splits output so that it can be both displayed
    and written to file.

    Tee writes out to a file, as specified by the constructor args, and writes to
    sys.stderr, as that is the default stream used by the unittest text runner.

    This is intended to be used as the stream for a unittest text runner instance.
    """
    def __init__(self, name, mode):
        self.file = open(name, mode)
        self.stderr = sys.stderr

    def __del__(self):
        self.file.close()

    def write(self, data):
        self.file.write(data)
        self.stderr.write(data)

    def flush(self):
        self.file.flush()
        self.stderr.flush()


def run_suite(log_name, suite, loglevel=logging.DEBUG):
    """Setup the root logger to log everything to console and file.
    Test log file in /logs/test_results<log_name>.txt.
    There will be two things writing to the same file without locks, but all
    the info is there and it's not terribly disruptive.

    :param log_name: The name of the logger to use.
    :param suite: The test suite to run.
    :param loglevel: The log level to use in logging events.
    """
    stream = Tee('/logs/test_results-{}.txt'.format(log_name), 'w')

    logger = logging.getLogger()  # root
    logger.level = loglevel
    stream_handler = logging.StreamHandler(stream)
    logger.addHandler(stream_handler)

    runner = unittest.TextTestRunner(stream)
    return runner.run(suite)
