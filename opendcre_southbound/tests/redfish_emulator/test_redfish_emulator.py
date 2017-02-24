#!/usr/bin/env python
""" Redfish Emulator TestCase

TestCase for the default config of the redfish emulator.

    Author:  Linh Hoang
    Date:    2/9/17

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
import os
import requests
from opendcre_southbound.emulator.redfish import redfish_resources


class RedfishTestCase(unittest.TestCase):
    base_path = 'http://redfish-emulator:5040/redfish/v1'

    def make_path(self, path):
        """ helper function to create urls to resources
        """
        return os.path.join(self.base_path, path)

    def do_get(self, path):
        """ helper function to send get requests with authentication
        """
        r = requests.get(path, auth=('root', 'redfish'))
        return r

    def do_patch(self, path, payload):
        """ helper function to send patch requests with authentication
        """
        r = requests.patch(path, json=payload, auth=('root', 'redfish'))
        return r

    def invalid_mockup(self):
        """ helper function to test invalid mock ups, should raise an OSError when non-existent mock up is passed in
        """
        redfish_resources.get_all_resources('InvalidMockUp')

    def test_000_invalid_mockup(self):
        """ test that OSError exception is raised
        """
        self.assertRaises(OSError, self.invalid_mockup())

    def test_001_database_populated(self):
        """ test default config for emulator generates a dictionary database
        """
        self.assertFalse(redfish_resources.database)
        database = redfish_resources.get_all_resources('RackmountServerMockUp')
        self.assertTrue(database)

    def test_002_auth(self):
        """ test requests sent without authentication to resources that require authentication is being denied
            requests sent with correct authentication returns 200
        """
        res_path = self.make_path('Systems')
        r_no_auth = requests.get(res_path)
        r_basic_auth = self.do_get(res_path)
        r_token_auth = requests.get(res_path, headers={'X-Auth-Token': '123456789authtoken'})
        r_invalid_basic_auth = requests.get(res_path, auth=('user', 'password'))
        r_invalid_token_auth = requests.get(res_path, headers={'X-Auth-Token': 'token'})

        self.assertEqual(r_no_auth.status_code, 401)
        self.assertEqual(r_basic_auth.status_code, 200)
        self.assertEqual(r_token_auth.status_code, 200)
        self.assertEqual(r_invalid_basic_auth.status_code, 401)
        self.assertEqual(r_invalid_token_auth.status_code, 401)

    def test_003_get_root(self):
        """ test that request sent to root path without authentication returns 200 status code
        """
        root_path = self.base_path
        resp = self.do_get(root_path).status_code
        self.assertEqual(resp, 200)

    def test_004_root_requests(self):
        """ root resource only supports get, all other request methods should return 405 error
        """
        root_path = self.base_path
        post = requests.post(root_path).status_code
        patch = requests.patch(root_path).status_code
        delete = requests.delete(root_path).status_code
        put = requests.put(root_path).status_code
        self.assertEqual(post, 405)
        self.assertEqual(patch, 405)
        self.assertEqual(delete, 405)
        self.assertEqual(put, 405)

    def test_005_resource_not_found(self):
        """ test that a request made to resource that does not exist returns 404
        """
        fake_path = self.make_path('Chassis/404')
        resp = self.do_get(fake_path)
        self.assertEqual(resp.status_code, 404)
        self.assertIn('Resource not found', resp.content)

    def test_006_patch(self):
        """ test patch request sent with valid payload returns 200 and resource was changed
        """
        res_path = self.make_path('Chassis/1U/Power')
        r_valid_key = self.do_patch(res_path, {'Name': 'Catfish Power'})
        self.assertEqual(r_valid_key.status_code, 200)

        new_name = self.do_get(res_path).json()['Name']
        self.assertEqual(new_name, 'Catfish Power')

    def test_007_bad_patch(self):
        """ test bad patch requests
        """
        res_path = self.make_path('Chassis/1U')

        r_payload_not_dict = self.do_patch(res_path, 'Test')
        self.assertEqual(r_payload_not_dict.status_code, 400)

        r_payload_is_none = self.do_patch(res_path, None)
        self.assertEqual(r_payload_is_none.status_code, 400)

        r_invalid_key = self.do_patch(res_path, {'Test': 'test'})
        self.assertEqual(r_invalid_key.status_code, 400)

    def test_008_system_reset(self):
        """ test request sent to turn system power off actually sets power to off
        """
        res_path = self.make_path('Systems/437XR1138R2/Actions/ComputerSystem.Reset')
        r = requests.post(res_path, json={'ResetType': 'ForceOff'}, auth=('root', 'redfish'))
        self.assertEqual(r.status_code, 200)

        system_path = self.make_path('Systems/437XR1138R2')
        power_state = self.do_get(system_path).json()['PowerState']
        self.assertEqual(power_state, 'Off')

    def test_009_system_reset_invalid(self):
        """ test request sent to reset system with bad content body, response should be 400 error
        """
        res_path = self.make_path('Systems/437XR1138R2/Actions/ComputerSystem.Reset')
        r_bad_value = requests.post(res_path, json={'ResetType': 'BadValue'}, auth=('root', 'redfish'))
        r_header_not_json = requests.post(res_path, data={'ResetType': 'ForceOff'}, auth=('root', 'redfish'))
        r_payload_not_dict = requests.post(res_path, json='Off', auth=('root', 'redfish'))
        self.assertEqual(r_bad_value.status_code, 400)
        self.assertEqual(r_header_not_json.status_code, 400)
        self.assertEqual(r_payload_not_dict.status_code, 400)

    def test_010_session_creation(self):
        """ test request sent to create new session is successful
        """
        res_path = self.make_path('SessionService/Sessions')
        r = requests.post(res_path, json={'UserName': 'root', 'Password': 'redfish'})
        self.assertEqual(r.status_code, 200)
        self.assertTrue('X-Auth-Token' in r.content)

        sessions = requests.get(res_path, auth=('root', 'redfish')).json()
        sessions_num = sessions['Members@odata.count']
        self.assertTrue(sessions_num > 1)

    def test_011_failed_session_creation(self):
        """ test requests sent to create new session with bad payloads
        """
        res_path = self.make_path('SessionService/Sessions')
        r_no_payload = requests.post(res_path)
        r_payload_not_json = requests.post(res_path, json='')
        r_no_json_header = requests.post(res_path, data={'UserName': 'root', 'Password': 'redfish'})

        self.assertEqual(r_no_payload.status_code, 400)
        self.assertEqual(r_no_json_header.status_code, 400)
        self.assertEqual(r_payload_not_json.status_code, 400)

    def test_012_session_logout(self):
        """ test deleting a session
        """
        session_path = self.make_path('SessionService/Sessions/2')
        r = requests.delete(session_path)
        self.assertEqual(r.status_code, 200)

        get_session = self.do_get(session_path)
        self.assertEqual(get_session.status_code, 404)

        bad_session_path = self.make_path('SessionService/Sessions/404')
        bad_r = requests.delete(bad_session_path)
        self.assertEqual(bad_r.status_code, 404)

    def test_013_get_boot(self):
        """ test getting boot target from System
        """
        res_path = self.make_path('Systems/437XR1138R2')
        resp = self.do_get(res_path).json()
        self.assertIn('Boot', resp)
        self.assertIn('BootSourceOverrideTarget', resp['Boot'])

    def test_014_set_boot(self):
        """ test changing the boot target
        """
        res_path = self.make_path('Systems/437XR1138R2')
        for target in ['Hdd', 'Pxe', 'None']:
            r = self.do_patch(res_path, {'Boot': {'BootSourceOverrideTarget': target}})
            new_boot_target = self.do_get(res_path).json()['Boot']['BootSourceOverrideTarget']
            self.assertEqual(r.status_code, 200)
            self.assertEqual(new_boot_target, target)

        r_invalid_boot_target = self.do_patch(res_path, {'Boot': {'BootSourceOverrideTarget': 'Test'}})
        self.assertEqual(r_invalid_boot_target.status_code, 400)

        r_invalid_key_1 = self.do_patch(res_path, {'Boot': {'BootSource': 'Hdd'}})
        self.assertEqual(r_invalid_key_1.status_code, 400)

        r_invalid_key_2 = self.do_patch(res_path, {'SetBoot': {'BootSourceOverrideTarget': 'Hdd'}})
        self.assertEqual(r_invalid_key_2.status_code, 400)

    def test_015_get_fan_reading(self):
        """ test getting fan reading
        """
        res_path = self.make_path('Chassis/1U/Thermal')
        r = self.do_get(res_path)
        resp = r.json()['Fans']

        self.assertEqual(r.status_code, 200)
        self.assertTrue(resp)

    def test_016_collection_invalid_requests(self):
        """ test sending unsupported requests returns 405
        """
        for collection in ['Chassis', 'Systems', 'Managers', 'AccountService']:
            res_path = self.make_path(collection)
            delete = requests.delete(res_path, auth=('root', 'redfish'))
            patch = requests.patch(res_path, auth=('root', 'redfish'))
            self.assertEqual(delete.status_code, 405)
            self.assertEqual(patch.status_code, 405)

    def test_017_get_LED(self):
        """ test getting led reading
        """
        res_path = self.make_path('Chassis/1U')
        r = self.do_get(res_path)
        self.assertTrue(r.content)
        self.assertEqual(r.status_code, 200)
        self.assertIn('IndicatorLED', r.content)

    def test_018_set_LED(self):
        """ test setting led state with valid values and invalid values
        """
        res_path = self.make_path('Chassis/1U')
        for valid_value in ['Off', 'Lit']:
            r = self.do_patch(res_path, {'IndicatorLED': valid_value})
            self.assertEqual(r.status_code, 200)

            led_state = self.do_get(res_path).json()['IndicatorLED']
            self.assertEqual(led_state, valid_value)

        r_no_json_header = requests.patch(res_path, data={'IndicatorLED': 'Off'}, auth=('root', 'redfish'))
        self.assertEqual(r_no_json_header.status_code, 400)

        r_payload_not_json = self.do_patch(res_path, 'Test')
        self.assertEqual(r_payload_not_json.status_code, 400)

        r_payload_is_none = self.do_patch(res_path, None)
        self.assertEqual(r_payload_is_none.status_code, 400)
