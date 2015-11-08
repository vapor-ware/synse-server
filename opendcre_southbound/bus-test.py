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
import devicebus
import shutil

import vapor_ipmi

import requests

from version import __api_version__

PREFIX = "http://127.0.0.1:5000/opendcre/" + __api_version__
IPMIBOARD = '40000000'
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
        r = requests.get(PREFIX + "/scan/ff")
        # response = json.loads(r.text)
        # self.assertEqual(len(response["boards"]), 24)
        self.assertEqual(r.status_code, 500)  # currently not enabled in firmware

    def test_002_one_boards(self):
        """
            Test for one board.
        """
        r = requests.get(PREFIX + "/scan/00000001")
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"]), 1)

    def test_003_no_boards(self):
        """
            Test for no boards.
        """
        r = requests.get(PREFIX + "/scan/000000c8")
        self.assertEqual(r.status_code, 500)

    def test_004_no_devices(self):
        """
            Test for one board with no devices.
        """
        r = requests.get(PREFIX + "/scan/00000002")
        self.assertEqual(r.status_code, 500)  # should this really be so?

    def devices(self):
        """
            Test for one board with many devices.
        """
        r = requests.get(PREFIX + "/scan/00000003")
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"][0]["devices"]), 25)

    def test_006_many_requests(self):
        """
            Test for one board many times.  Too many cooks.
        """
        for x in range(5):
            r = requests.get(PREFIX + "/scan/00000001")
            response = json.loads(r.text)
            self.assertEqual(len(response["boards"]), 1)

    def test_007_extraneous_data(self):
        """
            Get a valid packet but with a boxload of data.
            We should be happy and drop the extra data on the floor.
        """
        r = requests.get(PREFIX + "/scan/00000063")
        self.assertEqual(r.status_code, 200)

    def test_008_invalid_data(self):
        """
            Get a valid packet but with bad data - checksum, trailer.
        """
        # BAD TRAILER
        r = requests.get(PREFIX + "/scan/00000064")
        self.assertEqual(r.status_code, 500)

        # BAD CHECKSUM
        r = requests.get(PREFIX + "/scan/00000065")
        self.assertEqual(r.status_code, 500)

    def test_009_no_data(self):
        """
            Get no packet in return.
        """
        # TIMEOUT
        r = requests.get(PREFIX + "/scan/00000066")
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
        r = requests.get(PREFIX + "/version/00000001")
        response = json.loads(r.text)
        self.assertEqual(response["firmware_version"], "Version Response 1")

    def test_002_very_long_version(self):
        """
            Test long version (valid board, valid version)
            Technically > 32 bytes will split stuff into multiple
            packets.
        """
        r = requests.get(PREFIX + "/version/00000002")
        self.assertEqual(r.status_code, 500)

    def test_003_empty_version(self):
        """
            Test empty version (valid board, empty version)
        """
        r = requests.get(PREFIX + "/version/00000003")
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
        r = requests.get(PREFIX + "/version/00000009")
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(response["firmware_version"], "0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789")

    def test_006_bad_data(self):
        """
            Bad checksum, bad trailer.
        """
        # bad trailer
        r = requests.get(PREFIX + "/version/0000000a")
        self.assertEqual(r.status_code, 500)

        # bad checksum
        r = requests.get(PREFIX + "/version/0000000b")
        self.assertEqual(r.status_code, 500)

    def test_007_no_data(self):
        """
            Timeout.
        """
        # timeout
        r = requests.get(PREFIX + "/version/000000c8")
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
        r = requests.get(PREFIX + "/read/thermistor/00000001/01ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 0)
        self.assertEqual(response["temperature_c"], 131.29)

        r = requests.get(PREFIX + "/read/none/00000001/03ff")
        self.assertEqual(r.status_code, 500)

    def test_002_read_mid(self):
        """
            Get a midpoint value for each supported conversion method
        """
        r = requests.get(PREFIX + "/read/thermistor/00000001/04ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 32768)
        self.assertEqual(response["temperature_c"], -4173.97)

        r = requests.get(PREFIX + "/read/none/00000001/06ff")
        self.assertEqual(r.status_code, 500)

    def test_003_read_8byte_max(self):
        """
            Get a max value for each supported conversion method
        """
        r = requests.get(PREFIX + "/read/thermistor/00000001/07ff")
        self.assertEqual(r.status_code, 500)  # 65535 was the value

        r = requests.get(PREFIX + "/read/thermistor/00000001/08ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 65534)
        self.assertAlmostEqual(response["temperature_c"], -8466.32, 1)

        r = requests.get(PREFIX + "/read/none/00000001/0aff")
        self.assertEqual(r.status_code, 500)

    def test_004_weird_data(self):
        """
            What happens when a lot of integer data are returned?
        """
        r = requests.get(PREFIX + "/read/thermistor/00000001/0bff")
        self.assertEqual(r.status_code, 500)  # we read something super weird for thermistor, so error

    def test_005_bad_data(self):
        """
            What happens when bad byte data are received.  What happens
            when there's a bad checksum or trailer?
        """
        # bad bytes
        r = requests.get(PREFIX + "/read/thermistor/00000001/0dff")
        self.assertEqual(r.status_code, 500)

        # bad trailer
        r = requests.get(PREFIX + "/read/thermistor/00000001/0eff")
        self.assertEqual(r.status_code, 500)

        # bad checksum
        r = requests.get(PREFIX + "/read/thermistor/00000001/0fff")
        self.assertEqual(r.status_code, 500)

    def test_006_no_data(self):
        """
            Timeout.
        """
        # timeout
        r = requests.get(PREFIX + "/read/none/00000001/10ff")
        self.assertEqual(r.status_code, 500)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
            PREFIX + "/scan/00000001",
            PREFIX + "/version/00000001",
            PREFIX + "/read/thermistor/00000001/01ff"
        ]
        for x in range(100):
            r = requests.get(request_urls[random.randint(0, len(request_urls) - 1)])
            self.assertEqual(r.status_code, 200)

    def test_002_device_reads(self):
        for x in range(100):
            r = requests.get(PREFIX + "/read/thermistor/00000001/01ff")
            self.assertEqual(r.status_code, 200)
            r = requests.get(PREFIX + "/read/thermistor/00000001/0cff")
            self.assertEqual(r.status_code, 200)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
        r = requests.get(PREFIX + "/power/status/00000001/01ff")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], True)
        self.assertEqual(response["over_current"], False)
        self.assertEqual(response["under_voltage"], False)

        # expected raw 64 (0x40) - when off, power_ok and under_voltage
        # and under_current don't have any meaning
        r = requests.get(PREFIX + "/power/status/00000001/01ff")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "64,0,0,0")
        self.assertEqual(response["power_status"], "off")
        self.assertEqual(response["power_ok"], True)
        self.assertEqual(response["over_current"], False)
        self.assertEqual(response["under_voltage"], False)

        # expected raw 2048 (0x800) - power problem but not
        # something related to under voltage or over current condition
        r = requests.get(PREFIX + "/power/status/00000001/01ff")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2048,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], False)
        self.assertEqual(response["over_current"], False)
        self.assertEqual(response["under_voltage"], False)

        # expected raw 2048+8=2056 (0x1010) - power problem due to under voltage
        r = requests.get(PREFIX + "/power/status/00000001/01ff")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2056,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], False)
        self.assertEqual(response["over_current"], False)
        self.assertEqual(response["under_voltage"], True)

        # expected raw 2048+16=2064 (0x1020) - power problem due to over current
        r = requests.get(PREFIX + "/power/status/00000001/01ff")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2064,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], False)
        self.assertEqual(response["over_current"], True)
        self.assertEqual(response["under_voltage"], False)

        # expected raw 2072 (0x1030)
        r = requests.get(PREFIX + "/power/status/00000001/01ff")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2072,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], False)
        self.assertEqual(response["over_current"], True)
        self.assertEqual(response["under_voltage"], True)

    def test_002_power_on(self):
        r = requests.get(PREFIX + "/power/on/00000001/01ff")
        self.assertEqual(r.status_code, 200)

    def test_003_power_cycle(self):
        r = requests.get(PREFIX + "/power/cycle/00000001/01ff")
        self.assertEqual(r.status_code, 200)

    def test_004_power_off(self):
        r = requests.get(PREFIX + "/power/off/00000001/01ff")
        self.assertEqual(r.status_code, 200)

    def test_005_valid_port_invalid_type(self):
        r = requests.get(PREFIX + "/power/status/00000001/02ff")
        self.assertEqual(r.status_code, 500)

    def test_006_invalid_port(self):
        r = requests.get(PREFIX + "/power/status/00000001/03ff")
        self.assertEqual(r.status_code, 500)

    def test_007_invalid_command(self):
        r = requests.get(PREFIX + "/power/invalid/00000001/01ff")
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX + "/power/cyle/00000001/01ff")
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX + "/power/xxx/00000001/01ff")
        self.assertEqual(r.status_code, 500)

    def test_008_no_power_data(self):
        r = requests.get(PREFIX + "/power/status/00000001/03ff")
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX + "/power/status/00000001/04ff")
        self.assertEqual(r.status_code, 500)

    def test_010_weird_data(self):
        r = requests.get(PREFIX + "/power/status/00000001/05ff")
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX + "/power/status/00000001/06ff")
        self.assertEqual(r.status_code, 500)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
        r = requests.get(PREFIX + "/read/thermistor/00000001/01ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 100)

        r = requests.get(PREFIX + "/read/thermistor/00000001/01ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 101)

        r = requests.get(PREFIX + "/read/thermistor/00000001/01ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 102)

    def test_002_read_same_board_diff_port(self):
        """
            Test reading thermistor devices on the same board but different ids,
            where both devices have the same length of responses and repeatable=true.
            One device being tested does not start at the first response since
            previous tests have incremented its counter.
        """
        r = requests.get(PREFIX + "/read/thermistor/00000001/01ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 103)

        r = requests.get(PREFIX + "/read/thermistor/00000001/03ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 200)

        r = requests.get(PREFIX + "/read/thermistor/00000001/01ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 104)

        r = requests.get(PREFIX + "/read/thermistor/00000001/03ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 201)

    def test_003_read_diff_board_diff_port(self):
        """
            Test reading thermistor devices on different boards, where both
            devices have the same length of responses and repeatable=true. One
            device being tested does not start at the first response since
            previous tests have incremented its counter.
        """
        r = requests.get(PREFIX + "/read/thermistor/00000001/03ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 202)

        r = requests.get(PREFIX + "/read/thermistor/00000003/02ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 800)

        r = requests.get(PREFIX + "/read/thermistor/00000001/03ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 203)

        r = requests.get(PREFIX + "/read/thermistor/00000003/02ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 801)

    def test_004_read_until_wraparound(self):
        """
            Test incrementing the counter on alternating devices (two
            thermistors), both where repeatable=true, but where the length
            of the responses list differ.
        """
        r = requests.get(PREFIX + "/read/thermistor/00000001/0cff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 600)

        r = requests.get(PREFIX + "/read/thermistor/00000001/0aff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 500)

        r = requests.get(PREFIX + "/read/thermistor/00000001/0cff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 601)

        r = requests.get(PREFIX + "/read/thermistor/00000001/0aff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 501)

        r = requests.get(PREFIX + "/read/thermistor/00000001/0cff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 602)

        r = requests.get(PREFIX + "/read/thermistor/00000001/0aff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 502)

        r = requests.get(PREFIX + "/read/thermistor/00000001/0cff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 603)

        r = requests.get(PREFIX + "/read/thermistor/00000001/0aff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 503)

        # counter should wrap back around here, since len(responses) has
        # been exceeded.
        r = requests.get(PREFIX + "/read/thermistor/00000001/0cff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 600)

        # counter should not wrap around for this device, since len(responses)
        # has not been exceeded
        r = requests.get(PREFIX + "/read/thermistor/00000001/0aff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 504)

        r = requests.get(PREFIX + "/read/thermistor/00000001/0cff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 601)

        r = requests.get(PREFIX + "/read/thermistor/00000001/0aff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 505)

    def test_005_power_same_board_diff_port(self):
        """
            Test incrementing the counter on alternating power devices,
            one where repeatable=true, and one where repeatable=false
        """
        r = requests.get(PREFIX + "/power/status/00000001/06ff")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

        r = requests.get(PREFIX + "/power/status/00000001/07ff")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

        r = requests.get(PREFIX + "/power/status/00000001/06ff")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "64,0,0,0")

        r = requests.get(PREFIX + "/power/status/00000001/07ff")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "64,0,0,0")

        r = requests.get(PREFIX + "/power/status/00000001/06ff")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2048,0,0,0")

        r = requests.get(PREFIX + "/power/status/00000001/07ff")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2048,0,0,0")

        # repeatable=true, so the counter should cycle back around
        r = requests.get(PREFIX + "/power/status/00000001/06ff")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

        # repeatable=false, so should not the counter back around
        r = requests.get(PREFIX + "/power/status/00000001/07ff")
        self.assertEqual(r.status_code, 500)

    def test_006_power_read_alternation(self):
        """
           Test incrementing the counter alternating between a power cmd and
           a read cmd, both where repeatable=true.
        """
        # perform three requests on the thermistor to get the count different from
        # the start count of the power
        r = requests.get(PREFIX + "/read/thermistor/00000001/08ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 300)

        r = requests.get(PREFIX + "/read/thermistor/00000001/08ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 301)

        r = requests.get(PREFIX + "/read/thermistor/00000001/08ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 302)

        # start alternating between power and thermistor
        r = requests.get(PREFIX + "/power/status/00000001/05ff")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

        r = requests.get(PREFIX + "/read/thermistor/00000001/08ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 303)

        r = requests.get(PREFIX + "/power/status/00000001/05ff")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "64,0,0,0")

        r = requests.get(PREFIX + "/read/thermistor/00000001/08ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 304)

        r = requests.get(PREFIX + "/power/status/00000001/05ff")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2048,0,0,0")

        r = requests.get(PREFIX + "/read/thermistor/00000001/08ff")
        response = json.loads(r.text)
        self.assertEqual(response["device_raw"], 305)

        r = requests.get(PREFIX + "/power/status/00000001/05ff")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2056,0,0,0")

        r = requests.get(PREFIX + "/read/thermistor/00000001/08ff")
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


class ByteProtocolTestCase(unittest.TestCase):
    def test_001_board_id_to_bytes(self):
        """ Test converting a board_id to bytes.
        """
        board_id = 0xf1e2d3c4
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xf1, 0xe2, 0xd3, 0xc4])

        board_id = 0x1
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x1])

        board_id = 0x00000000
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x00])

        board_id = 0xffffffff
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xff, 0xff, 0xff, 0xff])

        board_id = 0x123
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x01, 0x23])

    def test_002_board_id_to_bytes(self):
        """ Test converting a board_id long to bytes.
        """
        board_id = long(0x00)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x00])

        board_id = long(0x01)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x01])

        board_id = long(0x12345678)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x12, 0x34, 0x56, 0x78])

        board_id = long(0xffff)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0xff, 0xff])

        board_id = long(0xfabfab)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0xfa, 0xbf, 0xab])

        board_id = long(0x8d231a66)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x8d, 0x23, 0x1a, 0x66])

    def test_003_board_id_to_bytes(self):
        """ Test converting a board_id string to bytes.
        """
        board_id = '{0:08x}'.format(0xf1e2d3c4)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xf1, 0xe2, 0xd3, 0xc4])

        board_id = '{0:08x}'.format(0xffffffff)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xff, 0xff, 0xff, 0xff])

        board_id = '{0:08x}'.format(0x00000000)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x00])

        board_id = '{0:08x}'.format(0xbeef)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0xbe, 0xef])

        board_id = '{0:04x}'.format(0x123)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x01, 0x23])

        board_id = '{0:02x}'.format(0x42)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x42])

    def test_004_board_id_to_bytes(self):
        """ Test converting a board_id unicode to bytes.
        """
        board_id = unicode('{0:08x}'.format(0xf1e2d3c4))
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xf1, 0xe2, 0xd3, 0xc4])

        board_id = unicode('{0:08x}'.format(0xffffffff))
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xff, 0xff, 0xff, 0xff])

        board_id = unicode('{0:08x}'.format(0x00000000))
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x00])

        board_id = unicode('{0:08x}'.format(0xbeef))
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0xbe, 0xef])

        board_id = unicode('{0:04x}'.format(0x123))
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x01, 0x23])

        board_id = unicode('{0:02x}'.format(0x42))
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x42])

    def test_005_board_id_to_bytes(self):
        """ Test converting a board_id list to bytes.
        """
        board_id = [0x01, 0x02, 0x03, 0x04]
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id, board_id_bytes)

        board_id = [0xff, 0xff, 0xff, 0xff]
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id, board_id_bytes)

        board_id = [0x00, 0x00, 0x00, 0x00]
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id, board_id_bytes)

    def test_006_board_id_to_bytes(self):
        """ Test converting a board_id invalid type to bytes.
        """
        board_id = [0x01, 0x02, 0x03]
        with self.assertRaises(TypeError):
            board_id_bytes = devicebus.board_id_to_bytes(board_id)

        board_id = (0x01, 0x02, 0x03, 0x04)
        with self.assertRaises(TypeError):
            board_id_bytes = devicebus.board_id_to_bytes(board_id)

        board_id = float(0xf)
        with self.assertRaises(TypeError):
            board_id_bytes = devicebus.board_id_to_bytes(board_id)

        board_id = {0x01, 0x02, 0x03, 0x04}
        with self.assertRaises(TypeError):
            board_id_bytes = devicebus.board_id_to_bytes(board_id)

    def test_007_board_id_join_bytes(self):
        """ Test converting a list of board_id bytes into its original value.
        """
        board_id_bytes = [0x00, 0x00, 0x00, 0x00]
        board_id = devicebus.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0x00000000)

        board_id_bytes = [0xff, 0xff, 0xff, 0xff]
        board_id = devicebus.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0xffffffff)

        board_id_bytes = [0x00, 0x00, 0x43, 0x21]
        board_id = devicebus.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0x4321)

        board_id_bytes = [0x00, 0x00, 0x00, 0x01]
        board_id = devicebus.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0x1)

        board_id_bytes = [0xa7, 0x2b, 0x11, 0x0e]
        board_id = devicebus.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0xa72b110e)

        board_id_bytes = [0xbe, 0xef, 0x00, 0x00]
        board_id = devicebus.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0xbeef0000)

    def test_008_board_id_join_bytes(self):
        """ Test converting a list of board_id bytes into its original value.
        """
        board_id_bytes = []
        with self.assertRaises(ValueError):
            devicebus.board_id_join_bytes(board_id_bytes)

        board_id_bytes = [0x12, 0x34, 0x56]
        with self.assertRaises(ValueError):
            devicebus.board_id_join_bytes(board_id_bytes)

        board_id_bytes = [0x12, 0x34, 0x56, 0x78, 0x90]
        with self.assertRaises(ValueError):
            devicebus.board_id_join_bytes(board_id_bytes)

        board_id_bytes = 0x12345678
        with self.assertRaises(ValueError):
            devicebus.board_id_join_bytes(board_id_bytes)

    def test_009_device_id_to_bytes(self):
        """ Test converting a device_id to bytes.
        """
        device_id = 0xf1e2
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xf1, 0xe2])

        device_id = 0x1
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x1])

        device_id = 0x0000
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x00])

        device_id = 0xffff
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xff, 0xff])

        device_id = 0x123
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x01, 0x23])

    def test_010_device_id_to_bytes(self):
        """ Test converting a device_id to bytes.
        """
        device_id = long(0x00)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x00])

        device_id = long(0x0f)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x0f])

        device_id = long(0xffff)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xff, 0xff])

        device_id = long(0xa1b)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x0a, 0x1b])

        device_id = long(0xbeef)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xbe, 0xef])

    def test_011_device_id_to_bytes(self):
        """ Test converting a device_id to bytes.
        """
        device_id = '{0:04x}'.format(0xf1e2)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xf1, 0xe2])

        device_id = '{0:04x}'.format(0x0)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x00])

        device_id = '{0:04x}'.format(0xffff)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xff, 0xff])

        device_id = '{0:04x}'.format(0xabc)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x0a, 0xbc])

        device_id = '{0:02x}'.format(0x12)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x12])

    def test_012_device_id_to_bytes(self):
        """ Test converting a device_id to bytes.
        """
        device_id = unicode('{0:04x}'.format(0xf1e2))
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xf1, 0xe2])

        device_id = unicode('{0:04x}'.format(0x0))
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x00])

        device_id = unicode('{0:04x}'.format(0xffff))
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xff, 0xff])

        device_id = unicode('{0:04x}'.format(0xabc))
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x0a, 0xbc])

        device_id = unicode('{0:02x}'.format(0x12))
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x12])

    def test_013_device_id_to_bytes(self):
        """ Test converting a device_id to bytes.
        """
        device_id = [0x00, 0x00]
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id, device_id_bytes)

        device_id = [0xff, 0xff]
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id, device_id_bytes)

        device_id = [0x12, 0x34]
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id, device_id_bytes)

    def test_014_device_id_join_bytes(self):
        """ Test converting a list of device_id bytes into its original value.
        """
        device_id_bytes = [0x00, 0x00]
        device_id = devicebus.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0x0000)

        device_id_bytes = [0xff, 0xff]
        device_id = devicebus.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0xffff)

        device_id_bytes = [0x43, 0x21]
        device_id = devicebus.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0x4321)

        device_id_bytes = [0x00, 0x01]
        device_id = devicebus.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0x1)

        device_id_bytes = [0xa7, 0x2b]
        device_id = devicebus.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0xa72b)

        device_id_bytes = [0xef, 0x00]
        device_id = devicebus.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0xef00)

    def test_015_device_id_join_bytes(self):
        """ Test converting a list of device_id bytes into its original value.
        """
        device_id_bytes = []
        with self.assertRaises(ValueError):
            devicebus.device_id_join_bytes(device_id_bytes)

        device_id_bytes = [0x12]
        with self.assertRaises(ValueError):
            devicebus.device_id_join_bytes(device_id_bytes)

        device_id_bytes = [0x12, 0x34, 0x56]
        with self.assertRaises(ValueError):
            devicebus.device_id_join_bytes(device_id_bytes)

        device_id_bytes = 0x1234
        with self.assertRaises(ValueError):
            devicebus.device_id_join_bytes(device_id_bytes)

################################################################################
#                                                                              #
#                           I P M I  T E S T S                                 #
#                                                                              #
################################################################################

################################################################################
class BMCValidConfigTestCase01(unittest.TestCase):
    """
        Given valid BMC and vBMC configurations, ensure correct responses
        received.  In this case, power control should complete and return
        a status value.  Assumes valid power control as well.  Scan also
        tested.
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
            self.emulatorConfiguration = "./opendcre_southbound/tests/test001.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            self.vBMCConfig = './opendcre_southbound/tests/vbmc007.json'
            self.bmcConfig = './opendcre_southbound/tests/bmc007.json'
            shutil.copy(self.bmcConfig, '/opendcre/bmc_config.json')
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p4 = subprocess.Popen(['./opendcre_southbound/virtualbmc.py', self.vBMCConfig], preexec_fn=os.setsid)
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_scan(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that all of the entries are there - by doing a scan.

        """
        r = requests.get(PREFIX + '/scan/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(len(response['boards']), 1)
        self.assertEqual(len(response['boards'][0]['devices']), 4)

    def test_002_scan_all(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that all of the entries are there - by doing a scan all.

        """
        r = requests.get(PREFIX + '/scan')
        response = json.loads(r.text)
        # there are 6 'boards' in emulator config, but only 3 are valid (the
        # invalid ones do not have any devices, so are ignored by scan)
        self.assertEqual(len(response['boards']), 4)
        hasIpmiBoard = False
        for board in response['boards']:
            if board['board_id'] == IPMIBOARD:
                self.assertEqual(len(board['devices']), 4)
                hasIpmiBoard = True
        self.assertTrue(hasIpmiBoard)

    def test_003_version(self):
        """
            Ensure that the IPMI module is returning for version.

        """
        r = requests.get(PREFIX + '/version/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)

    def test_004_power_control(self):
        """
            Ensure that power control returns a status.
        """
        r = requests.get(PREFIX + '/power/on/' + IPMIBOARD + "/1")
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(response['power_ok'], True)

    def test_005_power_control_loop(self):
        """
            Ensure that power control returns a status.
        """
        for i in range(0, 5):
            r = requests.get(PREFIX + '/power/on/' + IPMIBOARD + "/1")
            response = json.loads(r.text)
            self.assertEqual(r.status_code, 200)
            self.assertEqual(response['power_ok'], True)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
                os.killpg(self.p4.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass

################################################################################
class BMCValidConfigTestCase02(unittest.TestCase):
    """
        Given valid configuration, repeat status checking quite a bit.
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
            self.emulatorConfiguration = "./opendcre_southbound/tests/test001.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            self.vBMCConfig = './opendcre_southbound/tests/vbmc016.json'
            self.bmcConfig = './opendcre_southbound/tests/bmc007.json'
            shutil.copy(self.bmcConfig, '/opendcre/bmc_config.json')
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p4 = subprocess.Popen(['./opendcre_southbound/virtualbmc.py', self.vBMCConfig], preexec_fn=os.setsid)
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_status_loop(self):
        """
            Ensure that power control returns a status.
        """
        for i in range(0, 500):
            r = requests.get(PREFIX + '/power/status/' + IPMIBOARD + "/1")
            response = json.loads(r.text)
            self.assertEqual(r.status_code, 200)
            self.assertEqual(response['power_ok'], True)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
                os.killpg(self.p4.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass

################################################################################
class BMCInValidConfigTestCase01(unittest.TestCase):
    """
        Given invalid BMC configuration, ensure that the IPMI board shows up,
        but does not have any devices.
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
            self.emulatorConfiguration = "./opendcre_southbound/tests/test001.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            self.vBMCConfig = './opendcre_southbound/tests/vbmc007.json'
            self.bmcConfig = './opendcre_southbound/tests/bmc008.json'
            shutil.copy(self.bmcConfig, '/opendcre/bmc_config.json')
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p4 = subprocess.Popen(['./opendcre_southbound/virtualbmc.py', self.vBMCConfig], preexec_fn=os.setsid)
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_scan(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that no IPMI devices are present, as the config was invalid.

        """
        r = requests.get(PREFIX + '/scan/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(len(response['boards']), 1)
        self.assertEqual(len(response['boards'][0]['devices']), 0)

    def test_002_scan_all(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that no IPMI devices are present, as config was invalid -
            via scan all.

        """
        r = requests.get(PREFIX + '/scan')
        response = json.loads(r.text)
        # there are 6 'boards' in emulator config, but only 3 are valid (the
        # invalid ones do not have any devices, so are ignored by scan)
        self.assertEqual(len(response['boards']), 4)
        hasIpmiBoard = False
        for board in response['boards']:
            if board['board_id'] == IPMIBOARD:
                self.assertEqual(len(board['devices']), 0)
                hasIpmiBoard = True
        self.assertTrue(hasIpmiBoard)

    def test_003_version(self):
        """
            Ensure that the IPMI module is returning for version.

        """
        r = requests.get(PREFIX + '/version/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
                os.killpg(self.p4.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass

################################################################################
class BMCInValidConfigTestCase02(unittest.TestCase):
    """
        Given invalid BMC configuration, ensure that the IPMI board shows up,
        but does not have any devices.
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
            self.emulatorConfiguration = "./opendcre_southbound/tests/test001.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            self.vBMCConfig = './opendcre_southbound/tests/vbmc007.json'
            self.bmcConfig = './opendcre_southbound/tests/bmc009.json'
            shutil.copy(self.bmcConfig, '/opendcre/bmc_config.json')
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p4 = subprocess.Popen(['./opendcre_southbound/virtualbmc.py', self.vBMCConfig], preexec_fn=os.setsid)
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_scan(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that no IPMI devices are present, as the config was invalid.

        """
        r = requests.get(PREFIX + '/scan/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(len(response['boards']), 1)
        self.assertEqual(len(response['boards'][0]['devices']), 0)

    def test_002_scan_all(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that no IPMI devices are present, as config was invalid -
            via scan all.

        """
        r = requests.get(PREFIX + '/scan')
        response = json.loads(r.text)
        # there are 6 'boards' in emulator config, but only 3 are valid (the
        # invalid ones do not have any devices, so are ignored by scan)
        self.assertEqual(len(response['boards']), 4)
        hasIpmiBoard = False
        for board in response['boards']:
            if board['board_id'] == IPMIBOARD:
                self.assertEqual(len(board['devices']), 0)
                hasIpmiBoard = True
        self.assertTrue(hasIpmiBoard)

    def test_003_version(self):
        """
            Ensure that the IPMI module is returning for version.

        """
        r = requests.get(PREFIX + '/version/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
                os.killpg(self.p4.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass

################################################################################
class BMCInValidConfigTestCase03(unittest.TestCase):
    """
        Given invalid BMC configuration, ensure that the IPMI board shows up,
        but does not have any devices.
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
            self.emulatorConfiguration = "./opendcre_southbound/tests/test001.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            self.vBMCConfig = './opendcre_southbound/tests/vbmc007.json'
            self.bmcConfig = './opendcre_southbound/tests/bmc010.json'
            shutil.copy(self.bmcConfig, '/opendcre/bmc_config.json')
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p4 = subprocess.Popen(['./opendcre_southbound/virtualbmc.py', self.vBMCConfig], preexec_fn=os.setsid)
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_scan(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that no IPMI devices are present, as the config was invalid.

        """
        r = requests.get(PREFIX + '/scan/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(len(response['boards']), 1)
        self.assertEqual(len(response['boards'][0]['devices']), 0)

    def test_002_scan_all(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that no IPMI devices are present, as config was invalid -
            via scan all.

        """
        r = requests.get(PREFIX + '/scan')
        response = json.loads(r.text)
        # there are 6 'boards' in emulator config, but only 3 are valid (the
        # invalid ones do not have any devices, so are ignored by scan)
        self.assertEqual(len(response['boards']), 4)
        hasIpmiBoard = False
        for board in response['boards']:
            if board['board_id'] == IPMIBOARD:
                self.assertEqual(len(board['devices']), 0)
                hasIpmiBoard = True
        self.assertTrue(hasIpmiBoard)

    def test_003_version(self):
        """
            Ensure that the IPMI module is returning for version.

        """
        r = requests.get(PREFIX + '/version/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
                os.killpg(self.p4.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass

################################################################################
class BMCInValidConfigTestCase04(unittest.TestCase):
    """
        Given invalid BMC configuration, which has extra field, we are able to
        move on without failure, so we should see 1 device returned.
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
            self.emulatorConfiguration = "./opendcre_southbound/tests/test001.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            self.vBMCConfig = './opendcre_southbound/tests/vbmc007.json'
            self.bmcConfig = './opendcre_southbound/tests/bmc011.json'
            shutil.copy(self.bmcConfig, '/opendcre/bmc_config.json')
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p4 = subprocess.Popen(['./opendcre_southbound/virtualbmc.py', self.vBMCConfig], preexec_fn=os.setsid)
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_scan(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that one IPMI device is present, as the config was invalid, but
            not so much so to prevent initialization (extra field ignored).

        """
        r = requests.get(PREFIX + '/scan/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(len(response['boards']), 1)
        self.assertEqual(len(response['boards'][0]['devices']), 1)

    def test_002_scan_all(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that one IPMI device is present, as the config was invalid, but
            not so much so to prevent initialization (extra field ignored) -
            via scan all.

        """
        r = requests.get(PREFIX + '/scan')
        response = json.loads(r.text)
        # there are 6 'boards' in emulator config, but only 3 are valid (the
        # invalid ones do not have any devices, so are ignored by scan)
        self.assertEqual(len(response['boards']), 4)
        hasIpmiBoard = False
        for board in response['boards']:
            if board['board_id'] == IPMIBOARD:
                self.assertEqual(len(board['devices']), 1)
                hasIpmiBoard = True
        self.assertTrue(hasIpmiBoard)

    def test_003_version(self):
        """
            Ensure that the IPMI module is returning for version.

        """
        r = requests.get(PREFIX + '/version/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
                os.killpg(self.p4.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass

################################################################################
class BMCInValidConfigTestCase05(unittest.TestCase):
    """
        Given invalid BMC configuration, ensure that the IPMI board shows up,
        but does not have any devices.
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
            self.emulatorConfiguration = "./opendcre_southbound/tests/test001.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            self.vBMCConfig = './opendcre_southbound/tests/vbmc007.json'
            self.bmcConfig = './opendcre_southbound/tests/bmc012.json'
            shutil.copy(self.bmcConfig, '/opendcre/bmc_config.json')
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p4 = subprocess.Popen(['./opendcre_southbound/virtualbmc.py', self.vBMCConfig], preexec_fn=os.setsid)
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_scan(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that no IPMI devices are present, as the config was invalid.

        """
        r = requests.get(PREFIX + '/scan/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(len(response['boards']), 1)
        self.assertEqual(len(response['boards'][0]['devices']), 0)

    def test_002_scan_all(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that no IPMI devices are present, as config was invalid -
            via scan all.

        """
        r = requests.get(PREFIX + '/scan')
        response = json.loads(r.text)
        # there are 6 'boards' in emulator config, but only 3 are valid (the
        # invalid ones do not have any devices, so are ignored by scan)
        self.assertEqual(len(response['boards']), 4)
        hasIpmiBoard = False
        for board in response['boards']:
            if board['board_id'] == IPMIBOARD:
                self.assertEqual(len(board['devices']), 0)
                hasIpmiBoard = True
        self.assertTrue(hasIpmiBoard)

    def test_003_version(self):
        """
            Ensure that the IPMI module is returning for version.

        """
        r = requests.get(PREFIX + '/version/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
                os.killpg(self.p4.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass

################################################################################
class BMCInValidConfigTestCase06(unittest.TestCase):
    """
        In this case, there is no BMC config file provided; ensure that the
        endpoint comes up, with no BMC devices present.
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
            self.emulatorConfiguration = "./opendcre_southbound/tests/test001.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            self.vBMCConfig = './opendcre_southbound/tests/vbmc007.json'
            self.bmcConfig = './opendcre_southbound/tests/bmc012.json'
            shutil.move('/opendcre/bmc_config.json', '/opendcre/bmc_config.removed')
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p4 = subprocess.Popen(['./opendcre_southbound/virtualbmc.py', self.vBMCConfig], preexec_fn=os.setsid)
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_scan(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that no IPMI devices are present, as the config was invalid.

        """
        r = requests.get(PREFIX + '/scan/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(len(response['boards']), 1)
        self.assertEqual(len(response['boards'][0]['devices']), 0)

    def test_002_scan_all(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that no IPMI devices are present, as config was invalid -
            via scan all.

        """
        r = requests.get(PREFIX + '/scan')
        response = json.loads(r.text)
        # there are 6 'boards' in emulator config, but only 3 are valid (the
        # invalid ones do not have any devices, so are ignored by scan)
        self.assertEqual(len(response['boards']), 4)
        hasIpmiBoard = False
        for board in response['boards']:
            if board['board_id'] == IPMIBOARD:
                self.assertEqual(len(board['devices']), 0)
                hasIpmiBoard = True
        self.assertTrue(hasIpmiBoard)

    def test_003_version(self):
        """
            Ensure that the IPMI module is returning for version.

        """
        r = requests.get(PREFIX + '/version/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
                os.killpg(self.p4.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass

################################################################################
class VBMCNoCloseTestCase(unittest.TestCase):
    """
        A power control command sequence is sent to the vBMC, which does
        everything ok, except does not send a response to the close command.
        In which case, we expect a 500 error back, as IPMI is not behaving
        reliably.

        No auth used in this test case.
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
            self.emulatorConfiguration = "./opendcre_southbound/tests/test001.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            self.vBMCConfig = './opendcre_southbound/tests/vbmc008.json'
            self.bmcConfig = './opendcre_southbound/tests/bmc007.json'
            shutil.copy(self.bmcConfig, '/opendcre/bmc_config.json')
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p4 = subprocess.Popen(['./opendcre_southbound/virtualbmc.py', self.vBMCConfig], preexec_fn=os.setsid)
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_scan(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that the correct number of BMC devices are present.

        """
        r = requests.get(PREFIX + '/scan/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(len(response['boards']), 1)
        self.assertEqual(len(response['boards'][0]['devices']), 4)

    def test_002_scan_all(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that the correct number of devices show up.

        """
        r = requests.get(PREFIX + '/scan')
        response = json.loads(r.text)
        # there are 6 'boards' in emulator config, but only 3 are valid (the
        # invalid ones do not have any devices, so are ignored by scan)
        self.assertEqual(len(response['boards']), 4)
        hasIpmiBoard = False
        for board in response['boards']:
            if board['board_id'] == IPMIBOARD:
                self.assertEqual(len(board['devices']), 4)
                hasIpmiBoard = True
        self.assertTrue(hasIpmiBoard)

    def test_003_version(self):
        """
            Ensure that the IPMI module is returning for version.

        """
        r = requests.get(PREFIX + '/version/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)

    def test_004_power_control(self):
        """
            Ensure that power control returns 500 as the session will not be closed.
        """
        r = requests.get(PREFIX + '/power/on/' + IPMIBOARD + "/1")
        self.assertEqual(r.status_code, 500)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
                os.killpg(self.p4.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass

################################################################################
class VBMCChassisErrorReturnTestCase(unittest.TestCase):
    """
        A power control command sequence is sent to the vBMC, which returns an
        error.
        In which case, we expect a 500 error back, as IPMI is not behaving
        reliably.

        No auth used in this test case.
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
            self.emulatorConfiguration = "./opendcre_southbound/tests/test001.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            self.vBMCConfig = './opendcre_southbound/tests/vbmc009.json'
            self.bmcConfig = './opendcre_southbound/tests/bmc007.json'
            shutil.copy(self.bmcConfig, '/opendcre/bmc_config.json')
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p4 = subprocess.Popen(['./opendcre_southbound/virtualbmc.py', self.vBMCConfig], preexec_fn=os.setsid)
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_scan(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that the correct number of BMC devices are present.

        """
        r = requests.get(PREFIX + '/scan/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(len(response['boards']), 1)
        self.assertEqual(len(response['boards'][0]['devices']), 4)

    def test_002_scan_all(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that the correct number of devices show up.

        """
        r = requests.get(PREFIX + '/scan')
        response = json.loads(r.text)
        # there are 6 'boards' in emulator config, but only 3 are valid (the
        # invalid ones do not have any devices, so are ignored by scan)
        self.assertEqual(len(response['boards']), 4)
        hasIpmiBoard = False
        for board in response['boards']:
            if board['board_id'] == IPMIBOARD:
                self.assertEqual(len(board['devices']), 4)
                hasIpmiBoard = True
        self.assertTrue(hasIpmiBoard)

    def test_003_version(self):
        """
            Ensure that the IPMI module is returning for version.

        """
        r = requests.get(PREFIX + '/version/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)

    def test_004_power_control(self):
        """
            Ensure that power control returns 500 as the session will not be closed.
        """
        r = requests.get(PREFIX + '/power/on/' + IPMIBOARD + "/1")
        self.assertEqual(r.status_code, 500)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
                os.killpg(self.p4.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass


################################################################################
class VBMCChannelAuthCapErrorTestCase(unittest.TestCase):
    """
        A connection command sequence is sent to the vBMC, which returns an
        error to the Get Channel Authentication Capabilities command.
        In which case, we expect a 500 error back, as IPMI is not behaving
        reliably.

        No auth used in this test case.
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
            self.emulatorConfiguration = "./opendcre_southbound/tests/test001.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            self.vBMCConfig = './opendcre_southbound/tests/vbmc010.json'
            self.bmcConfig = './opendcre_southbound/tests/bmc007.json'
            shutil.copy(self.bmcConfig, '/opendcre/bmc_config.json')
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p4 = subprocess.Popen(['./opendcre_southbound/virtualbmc.py', self.vBMCConfig], preexec_fn=os.setsid)
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_scan(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that the correct number of BMC devices are present.

        """
        r = requests.get(PREFIX + '/scan/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(len(response['boards']), 1)
        self.assertEqual(len(response['boards'][0]['devices']), 4)

    def test_002_scan_all(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that the correct number of devices show up.

        """
        r = requests.get(PREFIX + '/scan')
        response = json.loads(r.text)
        # there are 6 'boards' in emulator config, but only 3 are valid (the
        # invalid ones do not have any devices, so are ignored by scan)
        self.assertEqual(len(response['boards']), 4)
        hasIpmiBoard = False
        for board in response['boards']:
            if board['board_id'] == IPMIBOARD:
                self.assertEqual(len(board['devices']), 4)
                hasIpmiBoard = True
        self.assertTrue(hasIpmiBoard)

    def test_003_version(self):
        """
            Ensure that the IPMI module is returning for version.

        """
        r = requests.get(PREFIX + '/version/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)

    def test_004_power_control(self):
        """
            Ensure that power control returns 500 as we are unable to continue.
        """
        r = requests.get(PREFIX + '/power/on/' + IPMIBOARD + "/1")
        self.assertEqual(r.status_code, 500)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
                os.killpg(self.p4.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass

################################################################################
class VBMCCloseErrorTestCase(unittest.TestCase):
    """
        A power control command sequence is sent to the vBMC, which does
        everything ok, except does gets error as response to the close command.
        In which case, we expect a 500 error back, as IPMI is not behaving
        reliably.

        No auth used in this test case.
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
            self.emulatorConfiguration = "./opendcre_southbound/tests/test001.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            self.vBMCConfig = './opendcre_southbound/tests/vbmc008.json'
            self.bmcConfig = './opendcre_southbound/tests/bmc007.json'
            shutil.copy(self.bmcConfig, '/opendcre/bmc_config.json')
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p4 = subprocess.Popen(['./opendcre_southbound/virtualbmc.py', self.vBMCConfig], preexec_fn=os.setsid)
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_scan(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that the correct number of BMC devices are present.

        """
        r = requests.get(PREFIX + '/scan/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(len(response['boards']), 1)
        self.assertEqual(len(response['boards'][0]['devices']), 4)

    def test_002_scan_all(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that the correct number of devices show up.

        """
        r = requests.get(PREFIX + '/scan')
        response = json.loads(r.text)
        # there are 6 'boards' in emulator config, but only 3 are valid (the
        # invalid ones do not have any devices, so are ignored by scan)
        self.assertEqual(len(response['boards']), 4)
        hasIpmiBoard = False
        for board in response['boards']:
            if board['board_id'] == IPMIBOARD:
                self.assertEqual(len(board['devices']), 4)
                hasIpmiBoard = True
        self.assertTrue(hasIpmiBoard)

    def test_003_version(self):
        """
            Ensure that the IPMI module is returning for version.

        """
        r = requests.get(PREFIX + '/version/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)

    def test_004_power_control(self):
        """
            Ensure that power control returns 500 as close session returns error
        """
        r = requests.get(PREFIX + '/power/on/' + IPMIBOARD + "/1")
        self.assertEqual(r.status_code, 500)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
                os.killpg(self.p4.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass

################################################################################
class VBMCJunkDataTestCase(unittest.TestCase):
    """
        A power control command sequence is sent to the vBMC, which does
        everything ok, except does gets junk as response to the close command.
        We are able to survive this event, though it is concerning if it
        occurs in reality.

        No auth used in this test case.
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
            self.emulatorConfiguration = "./opendcre_southbound/tests/test001.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            self.vBMCConfig = './opendcre_southbound/tests/vbmc012.json'
            self.bmcConfig = './opendcre_southbound/tests/bmc007.json'
            shutil.copy(self.bmcConfig, '/opendcre/bmc_config.json')
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p4 = subprocess.Popen(['./opendcre_southbound/virtualbmc.py', self.vBMCConfig], preexec_fn=os.setsid)
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_scan(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that the correct number of BMC devices are present.

        """
        r = requests.get(PREFIX + '/scan/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(len(response['boards']), 1)
        self.assertEqual(len(response['boards'][0]['devices']), 4)

    def test_002_scan_all(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that the correct number of devices show up.

        """
        r = requests.get(PREFIX + '/scan')
        response = json.loads(r.text)
        # there are 6 'boards' in emulator config, but only 3 are valid (the
        # invalid ones do not have any devices, so are ignored by scan)
        self.assertEqual(len(response['boards']), 4)
        hasIpmiBoard = False
        for board in response['boards']:
            if board['board_id'] == IPMIBOARD:
                self.assertEqual(len(board['devices']), 4)
                hasIpmiBoard = True
        self.assertTrue(hasIpmiBoard)

    def test_003_version(self):
        """
            Ensure that the IPMI module is returning for version.

        """
        r = requests.get(PREFIX + '/version/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)

    def test_004_power_control(self):
        """
            Ensure that power control returns 200 despite close session
            returning junk data.
        """
        r = requests.get(PREFIX + '/power/on/' + IPMIBOARD + "/1")
        self.assertEqual(r.status_code, 200)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
                os.killpg(self.p4.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass

################################################################################
class VBMCInvalidSessionTestCase(unittest.TestCase):
    """
        A connection command sequence is sent to the vBMC, which does
        everything ok, except gets junk as session id from activate session
        command.
        In this case, we are able to survive despite IPMI not behaving
        reliably; with a real BMC, using wrong session ID will result in an
        error code, tested elsewhere.

        No auth used in this test case.
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
            self.emulatorConfiguration = "./opendcre_southbound/tests/test001.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            self.vBMCConfig = './opendcre_southbound/tests/vbmc013.json'
            self.bmcConfig = './opendcre_southbound/tests/bmc007.json'
            shutil.copy(self.bmcConfig, '/opendcre/bmc_config.json')
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p4 = subprocess.Popen(['./opendcre_southbound/virtualbmc.py', self.vBMCConfig], preexec_fn=os.setsid)
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_scan(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that the correct number of BMC devices are present.

        """
        r = requests.get(PREFIX + '/scan/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(len(response['boards']), 1)
        self.assertEqual(len(response['boards'][0]['devices']), 4)

    def test_002_scan_all(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that the correct number of devices show up.

        """
        r = requests.get(PREFIX + '/scan')
        response = json.loads(r.text)
        # there are 6 'boards' in emulator config, but only 3 are valid (the
        # invalid ones do not have any devices, so are ignored by scan)
        self.assertEqual(len(response['boards']), 4)
        hasIpmiBoard = False
        for board in response['boards']:
            if board['board_id'] == IPMIBOARD:
                self.assertEqual(len(board['devices']), 4)
                hasIpmiBoard = True
        self.assertTrue(hasIpmiBoard)

    def test_003_version(self):
        """
            Ensure that the IPMI module is returning for version.

        """
        r = requests.get(PREFIX + '/version/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)

    def test_004_power_control(self):
        """
            Ensure that power control returns 200 - we receive a weird session id
            but are able to continue - at least with the emulator.
        """
        r = requests.get(PREFIX + '/power/on/' + IPMIBOARD + "/1")
        self.assertEqual(r.status_code, 200)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
                os.killpg(self.p4.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass

################################################################################
class VBMCNotEnoughDataTestCase(unittest.TestCase):
    """
        A power control command sequence is sent to the vBMC, which does
        everything ok, except does gets not enough data as response to chassis
        command.
        In which case, we expect a 500 error back, as IPMI is not behaving
        reliably.

        No auth used in this test case.
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
            self.emulatorConfiguration = "./opendcre_southbound/tests/test001.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            self.vBMCConfig = './opendcre_southbound/tests/vbmc015.json'
            self.bmcConfig = './opendcre_southbound/tests/bmc007.json'
            shutil.copy(self.bmcConfig, '/opendcre/bmc_config.json')
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p4 = subprocess.Popen(['./opendcre_southbound/virtualbmc.py', self.vBMCConfig], preexec_fn=os.setsid)
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_scan(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that the correct number of BMC devices are present.

        """
        r = requests.get(PREFIX + '/scan/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(len(response['boards']), 1)
        self.assertEqual(len(response['boards'][0]['devices']), 4)

    def test_002_scan_all(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that the correct number of devices show up.

        """
        r = requests.get(PREFIX + '/scan')
        response = json.loads(r.text)
        # there are 6 'boards' in emulator config, but only 3 are valid (the
        # invalid ones do not have any devices, so are ignored by scan)
        self.assertEqual(len(response['boards']), 4)
        hasIpmiBoard = False
        for board in response['boards']:
            if board['board_id'] == IPMIBOARD:
                self.assertEqual(len(board['devices']), 4)
                hasIpmiBoard = True
        self.assertTrue(hasIpmiBoard)

    def test_003_version(self):
        """
            Ensure that the IPMI module is returning for version.

        """
        r = requests.get(PREFIX + '/version/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)

    def test_004_power_control(self):
        """
            Ensure that power control returns 500 as close session returns error
        """
        r = requests.get(PREFIX + '/power/on/' + IPMIBOARD + "/1")
        self.assertEqual(r.status_code, 500)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
                os.killpg(self.p4.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass

################################################################################
class VBMCTooMuchDataTestCase(unittest.TestCase):
    """
        A power control command sequence is sent to the vBMC, which does
        everything ok, except returns too much data to chassis command.
        In which case, we expect a 500 error back, as IPMI is not behaving
        reliably.

        No auth used in this test case.
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
            self.emulatorConfiguration = "./opendcre_southbound/tests/test001.json"
            self.emulatortty = EMULATORTTY
            self.endpointtty = ENDPOINTTTY
            self.vBMCConfig = './opendcre_southbound/tests/vbmc014.json'
            self.bmcConfig = './opendcre_southbound/tests/bmc007.json'
            shutil.copy(self.bmcConfig, '/opendcre/bmc_config.json')
            socatarg1 = "PTY,link=" + self.emulatortty + ",mode=666"
            socatarg2 = "PTY,link=" + self.endpointtty + ",mode=666"
            self.p4 = subprocess.Popen(['./opendcre_southbound/virtualbmc.py', self.vBMCConfig], preexec_fn=os.setsid)
            self.p3 = subprocess.Popen(["socat", socatarg1, socatarg2], preexec_fn=os.setsid)
            self.p2 = subprocess.Popen(["./opendcre_southbound/devicebus_emulator.py", self.emulatortty, self.emulatorConfiguration], preexec_fn=os.setsid)
            self.p = subprocess.Popen(["./start_opendcre.sh", self.endpointtty], preexec_fn=os.setsid)
            time.sleep(6)  # wait for flask to be ready

    def test_001_scan(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that the correct number of BMC devices are present.

        """
        r = requests.get(PREFIX + '/scan/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(len(response['boards']), 1)
        self.assertEqual(len(response['boards'][0]['devices']), 4)

    def test_002_scan_all(self):
        """
            Ensure that the configuration file was picked up by the endpoint,
            and that the correct number of devices show up.

        """
        r = requests.get(PREFIX + '/scan')
        response = json.loads(r.text)
        # there are 6 'boards' in emulator config, but only 3 are valid (the
        # invalid ones do not have any devices, so are ignored by scan)
        self.assertEqual(len(response['boards']), 4)
        hasIpmiBoard = False
        for board in response['boards']:
            if board['board_id'] == IPMIBOARD:
                self.assertEqual(len(board['devices']), 4)
                hasIpmiBoard = True
        self.assertTrue(hasIpmiBoard)

    def test_003_version(self):
        """
            Ensure that the IPMI module is returning for version.

        """
        r = requests.get(PREFIX + '/version/' + IPMIBOARD)
        response = json.loads(r.text)
        self.assertEqual(r.status_code, 200)

    def test_004_power_control(self):
        """
            Ensure that power control returns 500 as close session returns error
        """
        r = requests.get(PREFIX + '/power/on/' + IPMIBOARD + "/1")
        self.assertEqual(r.status_code, 500)

    @classmethod
    def tearDownClass(self):
        """
            Kill the flask and api endpoint processes upon completion.  If the
            test fails or crashes, this currently does not do an elegant enough
            job of cleaning up.
        """
        if EMULATOR_ENABLE:

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
                os.killpg(self.p4.pid, signal.SIGTERM)
            except:
                pass
            try:
                subprocess.call(["/bin/kill", "-s TERM `cat /var/run/nginx.pid`"])
            except:
                pass

unittest.main()
