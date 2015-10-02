#!/usr/bin/python
"""
   OpenDCRE Southbound API Test Harness
   Author:  andrew
   Date:    4/13/2015
        \\//
         \/apor IO

    Copyright (C) 2015  Vapor IO

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
import os
import subprocess
import signal
import time
import json
import random

import requests

from version import __api_version__

PREFIX = "http://127.0.0.1:5000/opendcre/" + __api_version__
EMULATORTTY = "/dev/ttyVapor001"
ENDPOINTTTY = "/dev/ttyVapor002"
EMULATOR_ENABLE = True


class ScanTestCase(unittest.TestCase):
    """
        Test board scan issues that may arise.
    """
    @classmethod
    def setUpClass(self):
        """
            Set up the emulator and endpoint, which run as separate processes.
            These processes communicate via a virtual serial port.  We sleep
            for a second to give time for flask to initialize before running
            the test.
        """
        if EMULATOR_ENABLE:
            # use the test001.json emulator configuration for this test
            self.emulatorConfiguration = "./opendcre_southbound/tests/test001.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_many_boards(self):
        """
            Test for many boards (24 to be exact)
        """
        r = requests.get(PREFIX + "/scan/255")
        # response = json.loads(r.text)
        # self.assertEqual(len(response["boards"]), 24)
        self.assertEqual(r.status_code, 500)  # currently not enabled in firmware

    def test_002_one_boards(self):
        """
            Test for one board.
        """
        r = requests.get(PREFIX + "/scan/1")
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"]), 1)

    def test_003_no_boards(self):
        """
            Test for no boards.
        """
        r = requests.get(PREFIX + "/scan/200")
        self.assertEqual(r.status_code, 500)

    def test_004_no_ports(self):
        """
            Test for one board no ports.
        """
        r = requests.get(PREFIX + "/scan/2")
        self.assertEqual(r.status_code, 500)  # should this really be so?

    def test_005_many_ports(self):
        """
            Test for one board many ports.
        """
        r = requests.get(PREFIX + "/scan/3")
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"][0]["ports"]), 25)

    def test_006_many_requests(self):
        """
            Test for one board many times.  Too many cooks.
        """
        for x in range(5):
            r = requests.get(PREFIX + "/scan/1")
            response = json.loads(r.text)
            self.assertEqual(len(response["boards"]), 1)

    def test_007_extraneous_data(self):
        """
            Get a valid packet but with a boxload of data.
            We should be happy and drop the extra data on the floor.
        """
        r = requests.get(PREFIX + "/scan/99")
        self.assertEqual(r.status_code, 200)

    def test_008_invalid_data(self):
        """
            Get a valid packet but with bad data - checksum, trailer.
        """
        # BAD TRAILER
        r = requests.get(PREFIX + "/scan/100")
        self.assertEqual(r.status_code, 500)

        # BAD CHECKSUM
        r = requests.get(PREFIX + "/scan/101")
        self.assertEqual(r.status_code, 500)

    def test_009_no_data(self):
        """
            Get no packet in return.
        """
        # TIMEOUT
        r = requests.get(PREFIX + "/scan/102")
        self.assertEqual(r.status_code, 500)

    def test_010_bad_url(self):
        """
            Get no packet in return.
        """
        # bad url
        r = requests.get(PREFIX + "/scan/")
        self.assertEqual(r.status_code, 404)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:
            print " * SB-TEST: Cleaning up!"
            try:
                os.killpg(self.p.pid, signal.SIGTERM)
            except:
                pass
            try:
                os.killpg(self.p2.pid, signal.SIGTERM)
            except:
                pass
            try:
                os.killpg(self.p3.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass


################################################################################
class VersionTestCase(unittest.TestCase):
    """
        Test board version issues that may arise.
    """
    @classmethod
    def setUpClass(self):
        """
            Set up the emulator and endpoint, which run as separate processes.
            These processes communicate via a virtual serial port.  We sleep
            for a second to give time for flask to initialize before running
            the test.
        """
        if EMULATOR_ENABLE:
            # use the test002.json emulator configuration for this test
            self.emulatorConfiguration = "./opendcre_southbound/tests/test002.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_simple_version(self):
        """
            Test simple version (valid board, valid version)
        """
        r = requests.get(PREFIX + "/version/1")
        response = json.loads(r.text)
        self.assertEqual(response["firmware_version"], "Version Response 1")

    def test_002_very_long_version(self):
        """
            Test long version (valid board, valid version)
            Technically > 32 bytes will split stuff into multiple
            packets.
        """
        r = requests.get(PREFIX + "/version/2")
        self.assertEqual(r.status_code, 500)

    def test_003_empty_version(self):
        """
            Test empty version (valid board, empty version)
        """
        r = requests.get(PREFIX + "/version/3")
        response = json.loads(r.text)
        self.assertEqual(response["firmware_version"], "")

    def test_004_many_board_versions(self):
        """
            Test many board versions (valid boards, various versions)
        """
        for x in range(5):
            r = requests.get(PREFIX + "/version/" + str(x + 4))
            response = json.loads(r.text)
            self.assertEqual(response["firmware_version"], "Version 0x0" + str(x + 1))

    def test_005_long_data(self):
        """
            Data > 32 bytes (should be multiple packets but we cheat currently)
        """
        r = requests.get(PREFIX + "/version/9")
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(response["firmware_version"], "0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789")

    def test_006_bad_data(self):
        """
            Bad checksum, bad trailer.
        """
        # bad trailer
        r = requests.get(PREFIX + "/version/10")
        self.assertEqual(r.status_code, 500)

        # bad checksum
        r = requests.get(PREFIX + "/version/11")
        self.assertEqual(r.status_code, 500)

    def test_007_no_data(self):
        """
            Timeout.
        """
        # timeout
        r = requests.get(PREFIX + "/version/200")
        self.assertEqual(r.status_code, 500)

    def test_008_bad_url(self):
        """
            Timeout.
        """
        # bad url
        r = requests.get(PREFIX + "/version/")
        self.assertEqual(r.status_code, 404)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:
            print " * SB-TEST: Cleaning up!"
            try:
                os.killpg(self.p.pid, signal.SIGTERM)
            except:
                pass
            try:
                os.killpg(self.p2.pid, signal.SIGTERM)
            except:
                pass
            try:
                os.killpg(self.p3.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass


################################################################################
class DeviceReadTestCase(unittest.TestCase):
    """
        Test device read issues that may arise.
    """
    @classmethod
    def setUpClass(self):
        """
            Set up the emulator and endpoint, which run as separate processes.
            These processes communicate via a virtual serial port.  We sleep
            for a second to give time for flask to initialize before running
            the test.
        """
        if EMULATOR_ENABLE:
            # use the test001.json emulator configuration for this test
            self.emulatorConfiguration = "./opendcre_southbound/tests/test003.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_read_zero(self):
        """
            Get a zero value for each supported conversion method
        """
        r = requests.get(PREFIX + "/read/thermistor/1/1")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 0)
        self.assertEqual(response["temperature_c"], 131.29)

        r = requests.get(PREFIX + "/read/none/1/3")
        self.assertEqual(r.status_code, 500)

    def test_002_read_mid(self):
        """
            Get a midpoint value for each supported conversion method
        """
        r = requests.get(PREFIX + "/read/thermistor/1/4")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 32768)
        self.assertEqual(response["temperature_c"], -4173.97)

        r = requests.get(PREFIX + "/read/none/1/6")
        self.assertEqual(r.status_code, 500)

    def test_003_read_8byte_max(self):
        """
            Get a max value for each supported conversion method
        """
        r = requests.get(PREFIX + "/read/thermistor/1/7")
        self.assertEqual(r.status_code, 500)  # 65535 was the value

        r = requests.get(PREFIX + "/read/thermistor/1/8")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 65534)
        self.assertAlmostEqual(response["temperature_c"], -8466.32, 1)

        r = requests.get(PREFIX + "/read/none/1/10")
        self.assertEqual(r.status_code, 500)

    def test_004_weird_data(self):
        """
            What happens when a lot of integer data are returned?
        """
        r = requests.get(PREFIX + "/read/thermistor/1/11")
        self.assertEqual(r.status_code, 500)  # we read something super weird for thermistor, so error

    def test_005_bad_data(self):
        """
            What happens when bad byte data are received.  What happens
            when there's a bad checksum or trailer?
        """
        # bad bytes
        r = requests.get(PREFIX + "/read/thermistor/1/13")
        self.assertEqual(r.status_code, 500)

        # bad trailer
        r = requests.get(PREFIX + "/read/thermistor/1/14")
        self.assertEqual(r.status_code, 500)

        # bad checksum
        r = requests.get(PREFIX + "/read/thermistor/1/15")
        self.assertEqual(r.status_code, 500)

    def test_006_no_data(self):
        """
            Timeout.
        """
        # timeout
        r = requests.get(PREFIX + "/read/none/1/16")
        self.assertEqual(r.status_code, 500)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:
            print " * SB-TEST: Cleaning up!"
            try:
                os.killpg(self.p.pid, signal.SIGTERM)
            except:
                pass
            try:
                os.killpg(self.p2.pid, signal.SIGTERM)
            except:
                pass
            try:
                os.killpg(self.p3.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass


################################################################################
class EnduranceTestCase(unittest.TestCase):
    """
        Basic endurance tests.  Make sure there are not any lingering issues or
        clogged pipes between the bus and flask.
    """
    @classmethod
    def setUpClass(self):
        """
            Set up the emulator and endpoint, which run as separate processes.
            These processes communicate via a virtual serial port.  We sleep
            for a second to give time for flask to initialize before running
            the test.
        """
        if EMULATOR_ENABLE:
            # use the test001.json emulator configuration for this test
            self.emulatorConfiguration = "./opendcre_southbound/tests/test004.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_random_good_requests(self):
        request_urls = [
            PREFIX + "/scan/1",
            PREFIX + "/version/1",
            PREFIX + "/read/thermistor/1/1"
        ]
        for x in range(100):
            r = requests.get(request_urls[random.randint(0, len(request_urls) - 1)])
            self.assertEqual(r.status_code, 200)

    def test_002_device_reads(self):
        for x in range(100):
            r = requests.get(PREFIX + "/read/thermistor/1/1")
            self.assertEqual(r.status_code, 200)
            r = requests.get(PREFIX + "/read/thermistor/1/12")
            self.assertEqual(r.status_code, 200)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:
            print " * SB-TEST: Cleaning up!"
            try:
                os.killpg(self.p.pid, signal.SIGTERM)
            except:
                pass
            try:
                os.killpg(self.p2.pid, signal.SIGTERM)
            except:
                pass
            try:
                os.killpg(self.p3.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass


################################################################################
class PowerTestCase(unittest.TestCase):
    """
        Power control/status tests.
    """
    @classmethod
    def setUpClass(self):
        """
            Set up the emulator and endpoint, which run as separate processes.
            These processes communicate via a virtual serial port.  We sleep
            for a second to give time for flask to initialize before running
            the test.
        """
        if EMULATOR_ENABLE:
            # use the test001.json emulator configuration for this test
            self.emulatorConfiguration = "./opendcre_southbound/tests/test005.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_get_power_status(self):
        # expected raw 0
        r = requests.get(PREFIX + "/power/status/1/1")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], True)
        self.assertEqual(response["over_current"], False)
        self.assertEqual(response["under_voltage"], False)

        # expected raw 64 (0x40) - when off, power_ok and under_voltage
        # and under_current don't have any meaning
        r = requests.get(PREFIX + "/power/status/1/1")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "64,0,0,0")
        self.assertEqual(response["power_status"], "off")
        self.assertEqual(response["power_ok"], True)
        self.assertEqual(response["over_current"], False)
        self.assertEqual(response["under_voltage"], False)

        # expected raw 2048 (0x800) - power problem but not
        # something related to under voltage or over current condition
        r = requests.get(PREFIX + "/power/status/1/1")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2048,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], False)
        self.assertEqual(response["over_current"], False)
        self.assertEqual(response["under_voltage"], False)

        # expected raw 2048+8=2056 (0x1010) - power problem due to under voltage
        r = requests.get(PREFIX + "/power/status/1/1")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2056,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], False)
        self.assertEqual(response["over_current"], False)
        self.assertEqual(response["under_voltage"], True)

        # expected raw 2048+16=2064 (0x1020) - power problem due to over current
        r = requests.get(PREFIX + "/power/status/1/1")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2064,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], False)
        self.assertEqual(response["over_current"], True)
        self.assertEqual(response["under_voltage"], False)

        # expected raw 2072 (0x1030)
        r = requests.get(PREFIX + "/power/status/1/1")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2072,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], False)
        self.assertEqual(response["over_current"], True)
        self.assertEqual(response["under_voltage"], True)

    def test_002_power_on(self):
        r = requests.get(PREFIX + "/power/on/1/1")
        self.assertEqual(r.status_code, 200)

    def test_003_power_cycle(self):
        r = requests.get(PREFIX + "/power/cycle/1/1")
        self.assertEqual(r.status_code, 200)

    def test_004_power_off(self):
        r = requests.get(PREFIX + "/power/off/1/1")
        self.assertEqual(r.status_code, 200)

    def test_005_valid_port_invalid_type(self):
        r = requests.get(PREFIX + "/power/status/1/2")
        self.assertEqual(r.status_code, 500)

    def test_006_invalid_port(self):
        r = requests.get(PREFIX + "/power/status/1/3")
        self.assertEqual(r.status_code, 500)

    def test_007_invalid_command(self):
        r = requests.get(PREFIX + "/power/invalid/1/1")
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX + "/power/cyle/1/1")
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX + "/power/xxx/1/1")
        self.assertEqual(r.status_code, 500)

    def test_008_no_power_data(self):
        r = requests.get(PREFIX + "/power/status/1/3")
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX + "/power/status/1/4")
        self.assertEqual(r.status_code, 500)

    def test_010_weird_data(self):
        r = requests.get(PREFIX + "/power/status/1/5")
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX + "/power/status/1/6")
        self.assertEqual(r.status_code, 500)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:
            print " * SB-TEST: Cleaning up!"
            try:
                os.killpg(self.p.pid, signal.SIGTERM)
            except:
                pass
            try:
                os.killpg(self.p2.pid, signal.SIGTERM)
            except:
                pass
            try:
                os.killpg(self.p3.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass


################################################################################
class EmulatorCounterTestCase(unittest.TestCase):
    """
        Tests to ensure the emulator counter behaves as is expected and does
        not get changed erroneously.
    """
    @classmethod
    def setUpClass(self):
        """
            Set up the emulator and endpoint, which run as separate processes.
            These processes communicate via a virtual serial port.  We sleep
            for a second to give time for flask to initialize before running
            the test.
        """
        if EMULATOR_ENABLE:
            # use the test006.json emulator configuration for this test
            self.emulatorConfiguration = "./opendcre_southbound/tests/test006.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_read_same_board_same_port(self):
        """
            Test reading a single thermistor device repeatedly to make sure it
            increments sequentially.
        """
        r = requests.get(PREFIX + "/read/thermistor/1/1")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 100)

        r = requests.get(PREFIX + "/read/thermistor/1/1")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 101)

        r = requests.get(PREFIX + "/read/thermistor/1/1")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 102)

    def test_002_read_same_board_diff_port(self):
        """
            Test reading thermistor devices on the same board but different ports,
            where both devices have the same length of responses and repeatable=true.
            One device being tested does not start at the first response since
            previous tests have incremented its counter.
        """
        r = requests.get(PREFIX + "/read/thermistor/1/1")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 103)

        r = requests.get(PREFIX + "/read/thermistor/1/3")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 200)

        r = requests.get(PREFIX + "/read/thermistor/1/1")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 104)

        r = requests.get(PREFIX + "/read/thermistor/1/3")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 201)

    def test_003_read_diff_board_diff_port(self):
        """
            Test reading thermistor devices on different boards, where both
            devices have the same length of responses and repeatable=true. One
            device being tested does not start at the first response since
            previous tests have incremented its counter.
        """
        r = requests.get(PREFIX + "/read/thermistor/1/3")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 202)

        r = requests.get(PREFIX + "/read/thermistor/3/2")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 800)

        r = requests.get(PREFIX + "/read/thermistor/1/3")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 203)

        r = requests.get(PREFIX + "/read/thermistor/3/2")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 801)

    def test_004_read_until_wraparound(self):
        """
            Test incrementing the counter on alternating devices (humidity
            and thermistor), both where repeatable=true, but where the length
            of the responses list differ.
        """
        r = requests.get(PREFIX + "/read/humidity/1/12")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 600)

        r = requests.get(PREFIX + "/read/thermistor/1/10")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 500)

        r = requests.get(PREFIX + "/read/humidity/1/12")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 601)

        r = requests.get(PREFIX + "/read/thermistor/1/10")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 501)

        r = requests.get(PREFIX + "/read/humidity/1/12")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 602)

        r = requests.get(PREFIX + "/read/thermistor/1/10")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 502)

        r = requests.get(PREFIX + "/read/humidity/1/12")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 603)

        r = requests.get(PREFIX + "/read/thermistor/1/10")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 503)

        # counter should wrap back around here, since len(responses) has
        # been exceeded.
        r = requests.get(PREFIX + "/read/humidity/1/12")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 600)

        # counter should not wrap around for this device, since len(responses)
        # has not been exceeded
        r = requests.get(PREFIX + "/read/thermistor/1/10")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 504)

        r = requests.get(PREFIX + "/read/humidity/1/12")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 601)

        r = requests.get(PREFIX + "/read/thermistor/1/10")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 505)

    def test_005_power_same_board_diff_port(self):
        """
            Test incrementing the counter on alternating power devices,
            one where repeatable=true, and one where repeatable=false
        """
        r = requests.get(PREFIX + "/power/status/1/6")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

        r = requests.get(PREFIX + "/power/status/1/7")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

        r = requests.get(PREFIX + "/power/status/1/6")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "64,0,0,0")

        r = requests.get(PREFIX + "/power/status/1/7")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "64,0,0,0")

        r = requests.get(PREFIX + "/power/status/1/6")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2048,0,0,0")

        r = requests.get(PREFIX + "/power/status/1/7")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2048,0,0,0")

        # repeatable=true, so the counter should cycle back around
        r = requests.get(PREFIX + "/power/status/1/6")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

        # repeatable=false, so should not the counter back around
        r = requests.get(PREFIX + "/power/status/1/7")
        self.assertEqual(r.status_code, 500)

    def test_006_power_read_alternation(self):
        """
           Test incrementing the counter alternating between a power cmd and
           a read cmd, both where repeatable=true.
        """
        # perform three requests on the thermistor to get the count different from
        # the start count of the power
        r = requests.get(PREFIX + "/read/thermistor/1/8")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 300)

        r = requests.get(PREFIX + "/read/thermistor/1/8")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 301)

        r = requests.get(PREFIX + "/read/thermistor/1/8")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 302)

        # start alternating between power and thermistor
        r = requests.get(PREFIX + "/power/status/1/5")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

        r = requests.get(PREFIX + "/read/thermistor/1/8")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 303)

        r = requests.get(PREFIX + "/power/status/1/5")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "64,0,0,0")

        r = requests.get(PREFIX + "/read/thermistor/1/8")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 304)

        r = requests.get(PREFIX + "/power/status/1/5")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2048,0,0,0")

        r = requests.get(PREFIX + "/read/thermistor/1/8")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 305)

        r = requests.get(PREFIX + "/power/status/1/5")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2056,0,0,0")

        r = requests.get(PREFIX + "/read/thermistor/1/8")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 306)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:
            print " * SB-TEST: Cleaning up!"
            try:
                os.killpg(self.p.pid, signal.SIGTERM)
            except:
                pass
            try:
                os.killpg(self.p2.pid, signal.SIGTERM)
            except:
                pass
            try:
                os.killpg(self.p3.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass


unittest.main()
