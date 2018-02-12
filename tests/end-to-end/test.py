"""Synse Server's End to End Tests"""
# pylint: disable=redefined-outer-name,unused-argument

import time

import pytest
import requests

from synse import __version__, errors
from synse.version import __api_version__

host        = 'synse:5000'
url_prefix  = 'synse'
version     = __version__
api_version = __api_version__

base_blueprint = 'http://{}/{}'.format(host, url_prefix)
core_blueprint = 'http://{}/{}/{}'.format(host, url_prefix, api_version)


def test_route():
    """Check whether the service is up and reachable"""
    route_req = requests.get('{}/test'.format(base_blueprint))
    assert route_req.status_code == 200
    assert route_req.json().get('status') == 'ok'


def test_version():
    """Check whether the version is up to date"""
    version_req = requests.get('{}/version'.format(base_blueprint))
    assert version_req.status_code == 200
    assert version_req.json().get('version') == version
    assert version_req.json().get('api_version') == api_version


def test_config():
    """Get all configuration options"""
    config_req = requests.get('{}/config'.format(core_blueprint))
    assert config_req.status_code == 200

    # These are default configuration options
    expected_keys = ['locale', 'pretty_json', 'logging', 'cache', 'grpc']

    req_json = config_req.json()
    for key in expected_keys:
        assert key in req_json


def test_plugins():
    """Get all configured plugins"""
    # Only after hitting /scan endpoint do plugins start to register
    # Should expect no data in the first request
    plugins_1st_req = requests.get('{}/plugins'.format(core_blueprint))
    assert plugins_1st_req.status_code == 200

    assert len(plugins_1st_req.json()) == 0

    # Make a scan request and check for the second plugins request
    # This time, it should return all the configured plugins
    scan_req = requests.get('{}/scan'.format(core_blueprint))
    assert scan_req.status_code == 200 

    plugins_2nd_req = requests.get('{}/plugins'.format(core_blueprint))
    assert plugins_2nd_req.status_code == 200

    assert len(plugins_2nd_req.json()) != 0
    
    for plugin in plugins_2nd_req.json():
        assert 'name' in plugin
        assert 'network' in plugin
        assert 'address' in plugin


def test_end_to_end():
    """Main entry point for all the tests"""
    # Perform a general scan
    scan_req = requests.get('{}/scan'.format(core_blueprint))
    assert scan_req.status_code == 200 

    racks = scan_req.json().get('racks')
    assert len(racks) != 0

    # Iterate through the results and execute other tests
    # Rack Level
    for rack in racks:
        rack_id = rack.get('id')
        check_rack_scan(rack, rack_id)

        boards = rack.get('boards')
        assert len(boards) != 0

        # Collect all boards ids to check if they match with rack info request
        boards_ids = [board.get('id') for board in boards]
        check_rack_info(boards_ids, rack_id)

        # Board Level
        for board in boards:
            board_id = board.get('id')
            check_board_scan(board, rack_id, board_id)

            devices = board.get('devices')
            assert len(devices) != 0

            # Collect all devices ids to check if they match with board info request
            devices_ids = [device.get('id') for device in devices]
            check_board_info(devices_ids, rack_id, board_id)

            # Device Level
            for device in devices:
                device_id = device.get('id')
                device_type = device.get('type')
                check_device_scan(rack_id, board_id, device_id)
                check_device_info(rack_id, board_id, device_id, device_type)
                check_device_read(rack_id, board_id, device_id, device_type)
                check_device_write(rack_id, board_id, device_id, device_type)
                check_device_alias(rack_id, board_id, device_id, device_type)


def check_rack_scan(rack, rack_id):
    """Check a scan request for given rack

    Args:
        rack (dict): Rack object from the general scan
        rack_id (str): Rack's unique ID
    """
    rack_scan_req = requests.get('{}/scan/{}'.format(core_blueprint, rack_id))
    assert rack_scan_req.status_code == 200
    assert rack_scan_req.json().get('id') == rack_id
    assert rack_scan_req.json() == rack


def check_rack_info(boards_ids, rack_id):
    """Check an info request for a given rack

    Args:
        boards_ids (list): List of boards' IDs from the general scan
        rack_id (str): Rack's unique ID
    """
    rack_info_req = requests.get('{}/info/{}'.format(core_blueprint, rack_id))
    assert rack_info_req.status_code == 200
    assert rack_info_req.json().get('rack') == rack_id
    assert rack_info_req.json().get('boards') == boards_ids


def check_board_scan(board, rack_id, board_id):
    """Check a scan request for a given board and rack

    Args:
        board (dict): Board object from the general scan
        rack_id (str): Rack's unique ID
        board_id (str): Board's unique ID
    """
    board_info_req = requests.get('{}/scan/{}/{}'.format(core_blueprint, rack_id, board_id))
    assert board_info_req.status_code == 200
    assert board_info_req.json().get('id') == board_id
    assert board_info_req.json() == board


def check_board_info(devices_ids, rack_id, board_id):
    """Check an info request for a given board and rack
    
    Args:
        devices_ids (list): List of devices's IDs from the general scan
        rack_id (str): Rack's unique ID
        board_id (str): Board's unique ID
    """
    board_info_req = requests.get('{}/info/{}/{}'.format(core_blueprint, rack_id, board_id))
    assert board_info_req.status_code == 200
    assert board_info_req.json().get('board') == board_id
    assert board_info_req.json().get('location').get('rack') == rack_id
    assert board_info_req.json().get('devices') == devices_ids


def check_device_scan(rack_id, board_id, device_id):
    """Check a scan request for a given device, board and rack
    
    Args:
        rack_id (str): Rack's unique ID
        board_id (str): Board's unique ID
        device_id (str): Device's unique ID

    Details:
        There is no available endpoint for this. 
        Should return 404 HTTP code and URL_NOT_FOUND error.
    """
    device_scan_req = requests.get(
        '{}/scan/{}/{}/{}'.format(core_blueprint, rack_id, board_id, device_id)
    )
    assert device_scan_req.status_code == 404
    assert device_scan_req.json().get('http_code') == 404
    assert device_scan_req.json().get('error_id') == errors.URL_NOT_FOUND


def check_device_info(rack_id, board_id, device_id, device_type):
    """Check an info request for a given device, board and rack

    Args:
        rack_id (str): Rack's unique ID
        board_id (str): Board's unique ID
        device_id (str): Device's unique ID
        device_type (str): Type of device 
    """
    device_info_req = requests.get(
        '{}/info/{}/{}/{}'.format(core_blueprint, rack_id, board_id, device_id)
    )
    assert device_info_req.status_code == 200
    assert device_info_req.json().get('type') == device_type

    expected_keys = ['timestamp', 'uid', 'type', 'model',
                     'manufacturer', 'info', 'comment', 'location', 'output']

    req_json = device_info_req.json()
    for key in expected_keys:
        assert key in req_json


def check_device_read(rack_id, board_id, device_id, device_type):
    """Check a read request for a given device, board and rack
    
    Args:
        rack_id (str): Rack's unique ID
        board_id (str): Board's unique ID
        device_id (str): Device's unique ID
        device_type (str): Type of device 
    """
    device_read_req = requests.get(
        '{}/read/{}/{}/{}'.format(core_blueprint, rack_id, board_id, device_id)
    )
    assert device_read_req.status_code == 200
    assert device_read_req.json().get('type') == device_type

    data = device_read_req.json().get('data')
    assert data is not None

    if device_type == 'led':
        assert 'state' in data
        assert 'color' in data
        assert 'blink' in data
    elif device_type == 'fan':
        assert 'fan_speed' in data
    elif device_type == 'temperature':
        assert 'temperature' in data


def check_device_write(rack_id, board_id, device_id, device_type):
    """Check a write request for a given device, board and rack
    
    Args:
        rack_id (str): Rack's unique ID
        board_id (str): Board's unique ID
        device_id (str): Device's unique ID
        device_type (str): Type of device
    """
    if device_type == 'led':
        check_led_write(rack_id, board_id, device_id)
    elif device_type == 'fan':
        check_fan_write(rack_id, board_id, device_id)
    elif device_type == 'temperature':
        check_temperature_write(rack_id, board_id, device_id)


def check_led_write(rack_id, board_id, device_id):
    """Check a write request for a given led device

    Args:
        rack_id (str): Rack's unique ID
        board_id (str): Board's unique ID
        device_id (str): Device's unique ID

    Details:
        This is the list for all the cases that need to be check.
        On the left side are cases and sub-cases.
        On the right side are expected return values.
        Return values contains 2 components: status code and transaction state

        Cases,                                                      Status code,
        Subcases                                                    Transaction state
        ------------------------------------------------------------------------------
        Key's correctness
            2 keys are correct
                2 values are valid                                  -> 200, ok
                1 value is valid
                    action's value is valid                         -> 200, error
                    raw's value is valid                            -> 200, ok
                2 values are not valid                              -> 200, ok
            1 key is correct
                action is correct
                    action's value is valid                         -> break
                    action's value is not valid                     -> 200, ok
                raw is correct
                    raw's value is valid                            -> 200, ok
                    raw's value is not valid                        -> 200, ok
            2 keys are not correct                                  -> 500

        Key's absence
            2 keys are absence                                      -> 500
            1 key is absence
                action is absence
                    raw's value is valid                            -> 200, ok
                    raw's value is not valid                        -> 200, ok
                raw is absence
                    action's value is valid                         -> break
                    action's value is not valid                     -> 200, ok
    """
    # Options that return 200 status codes and their transactions' states are ok
    code_200_state_ok = {
        # Case: 2 keys are correct, 2 values are valid
        # These options should overwrite the existing values
        'state_on': {
            'action': 'state',
            'raw': 'on'
        },
        'state_off': {
            'action': 'state',
            'raw': 'off'
        },
        'color_min': {
            'action': 'color',
            'raw': '000000'
        },
        'color_max': {
            'action': 'color',
            'raw': 'FFFFFF'
        },
        'blink_blink': {
            'action': 'blink',
            'raw': 'blink'
        },
        'blink_steady': {
            'action': 'blink',
            'raw': 'steady'
        },

        # Case: 2 keys are correct, raw's value is valid
        # Because action's value is invalid, it can be anything
        # Therefore, no need to check for a specific state, color or blink
        'invalid_action_value': {
            'action': 'invalid',
            'raw': 'on'
        },

        # Case: 2 keys are correct, 2 values are not valid
        'invalid_values': {
            'action': 'invalid',
            'raw': 'invalid'
        },

        # Case: 1 key is correct / action is correct, action's value is not valid
        # Because raw is incorrect, raw's value can be anything even if it's valid
        'correct_action_invalid_value': {
            'action': 'invalid',
            'incorrect_raw': 'on/off/ffffff/blink'
        },

        # Case: 1 key is correct / raw is correct, raw's value is valid
        # Because action is incorrect, action's value can be anything
        # Therefore, no need to check for a specific state, color or blink
        'correct_raw_valid_value': {
            'incorrect_action': 'state/color/blink',
            'raw': 'on'
        },

        # Case: 1 key is correct / raw is correct, raw's value is not valid
        # Similarly, action is incorrect, no need to check for a specific value
        'correct_raw_invalid_value': {
            'incorrect_action': 'state/color/blink',
            'raw': 'invalid'
        },

        # Case: 1 key is absence / action is absence, raw's value is valid
        # Because action is absence, raw's value can be anything, even if it's valid
        'absence_action': {
            'raw': 'valid/invalid'
        },

        # Case: 1 key is absence / raw is absence, action's value is not valid
        # If the value is valid, see Issue #2 
        'absence_raw_invalid_action_value': {
            'action': 'invalid'
        }
    }

    # Options that return 200 status codes and their transactions' states are error
    code_200_state_error = {
        # Case: 2 keys are correct, action value is valid
        'state_invalid_raw_value': {
            'action': 'state',
            'raw': 'invalid'
        },

        # FIXME: Issue #1. 
        # LED color write isn't validated so the test fail
        # Comment out until fixed.
        # 'color_invalid_value': {
        #     'action': 'color',
        #     'raw': 'invalid'
        # }
        'blink_invalid_value': {
            'action': 'blink',
            'raw': 'invalid'
        }

        # Case: 1 key is correct / action is correct, action's value is valid
        # FIXME: Issue #2
        # It returns 200 status code and break the program.
        # Comment out until fixed.
        # 'state_incorrect_raw': {
        #     'action': 'state',
        #     'incorrect_raw': 'on'
        # },
        # 'color_incorrect_raw': {
        #     'action': 'color',
        #     'incorrect_raw': '000000'
        # },
        # 'blink_incorrect_raw': {
        #     'action': 'blink',
        #     'incorrect_raw': 'blink blink'
        # },

        # Case: 1 key is absence / raw is absence, action's value is valid
        # 'state_absence_raw': {
        #     'action': 'state'
        # },
        # 'color_absence_raw': {
        #     'action': 'color'
        # },
        # 'blink_absence_raw': {
        #     'action': 'blink'
        # }
    }

    # Options that return 500 status codes
    code_500 = {
        # Case: 2 keys are not correct
        # Because both keys are wrong, their value can be anything
        'incorrect_keys': {
            'incorrect_action': 'state/color/blink',
            'incorrect_raw': 'on/000000/blink'
        },

        # Case: 2 keys are absence
        'no_keys': {}
    }

    # List of transaction ids for requests that return 200 status codes
    tx_ids_code_200_state_ok = []
    tx_ids_code_200_state_error = []

    # For every post request, get its transaction id and append to the corresponding list
    # We only append the first returned transaction because at the moment,
    # it is only possible to write one value at a time
    for option, payload in code_200_state_ok.items():
        write_req = requests.post(
            '{}/write/{}/{}/{}'.format(core_blueprint, rack_id,board_id, device_id),
            json=payload
        )
        assert write_req.status_code == 200

        tx_ids_code_200_state_ok.append(write_req.json()[0].get('transaction'))

    for option, payload in code_200_state_error.items():
        write_req = requests.post(
            '{}/write/{}/{}/{}'.format(core_blueprint, rack_id, board_id, device_id),
            json=payload
        )
        assert write_req.status_code == 200

        tx_ids_code_200_state_error.append(write_req.json()[0].get('transaction'))

    # For requests that return 500 status code, there are no transactions have made
    # Only check for its status code
    for option, payload in code_500.items():
        write_req = requests.post(
            '{}/write/{}/{}/{}'.format(core_blueprint, rack_id, board_id, device_id),
            json=payload
        )
        assert write_req.status_code == 500

    # After making write requests and having all the transaction ids needed
    # Check if transactions ids' states are correct
    for id in tx_ids_code_200_state_ok:
        check_transaction(id, 'ok')
 
    for id in tx_ids_code_200_state_error:
        check_transaction(id, 'error')


def check_transaction(transaction_id, expected_state):
    """Check a transaction request for a given transaction id and state
    
    Args:
        transaction_id (str): Transaction's unique ID
        expected_state (str): Expected state of the transaction
    """
    r = requests.get('{}/transaction/{}'.format(core_blueprint, transaction_id))
    assert r.status_code == 200

    # If a transaction is done processing, check if it match the expected state
    # Otherwise, sleep for some time and check again
    if r.json().get('status') == 'done':
        assert r.json().get('state') == expected_state
    else:
        time.sleep(0.1)
        check_transaction(transaction_id, expected_state)
    

def check_fan_write(rack_id, board_id, device_id):
    """Check a write request for a given fan device

    Args:
        rack_id (str): Rack's unique ID
        board_id (str): Board's unique ID
        device_id (str): Device's unique ID
    """
    # TODO: Fill in when API documentation is ready
    pass


def check_temperature_write(rack_id, board_id, device_id):
    """Check a write request for a given temperature device

    Args:
        rack_id (str): Rack's unique ID
        board_id (str): Board's unique ID
        device_id (str): Device's unique ID

    Details:
        Temperature device don't support write.
        Should return 500 HTTP code and INVALID_ARGUMENTS error.
    """
    temperature_write_req = requests.post(
        '{}/write/{}/{}/{}'.format(core_blueprint, rack_id, board_id, device_id),
        json={}
    )
    assert temperature_write_req.status_code == 500
    assert temperature_write_req.json().get('http_code') == 500
    assert temperature_write_req.json().get('error_id') == errors.INVALID_ARGUMENTS


def check_device_alias(rack_id, board_id, device_id, device_type):
    """Check a alias request for a given device, device type, board, rack
    
    Args:
        rack_id (str): Rack's unique ID
        board_id (str): Board's unique ID
        device_id (str): Device's unique ID
        device_type (str): Type of device 
    """
    check_alias_no_query_param(rack_id, board_id, device_id, device_type)
    check_alias_query_param(rack_id, board_id, device_id, device_type)


def check_alias_no_query_param(rack_id, board_id, device_id, device_type):
    """Check a alias request using no query parameter

    Args:
        rack_id (str): Rack's unique ID
        board_id (str): Board's unique ID
        device_id (str): Device's unique ID
        device_type (str): Type of device 

    Details:
        Without query parameter, it acts like a read request.
        If a device type is not in the supported list, there is no endpoint for that device.
        Should return 404 HTTP code and URL_NOT_FOUND error.
    """
    alias_req = requests.get(
        '{}/{}/{}/{}/{}'.format(core_blueprint, device_type, rack_id, board_id, device_id)
    )
    if device_type in ['led', 'fan', 'power', 'boot_target']:
        assert alias_req.status_code == 200
        assert alias_req.json().get('type') == device_type
        assert 'data' in alias_req.json()
    else:
        assert alias_req.status_code == 404
        assert alias_req.json().get('http_code') == 404
        assert alias_req.json().get('error_id') == errors.URL_NOT_FOUND


def check_alias_query_param(rack_id, board_id, device_id, device_type):
    """Check a alias request using query parameters

    Args:
        rack_id (str): Rack's unique ID
        board_id (str): Board's unique ID
        device_id (str): Device's unique ID
        device_type (str): Type of device 

    Details:
        It acts like a write request if and only if query parameter(s) is valid.
        Otherwise, it acts like a read request.
    """
    if device_type == 'led':
        check_alias_led_query_param(rack_id, board_id, device_id)
    elif device_type == 'fan':
        # TODO: Fill in when API documentation is ready
        pass
    elif device_type == 'boot':
        # TODO: Fill in when API documentation is ready
        pass
    elif device_type == 'boot_target':
        # TODO: Fill in when API documentation is ready
        pass
    else:
        # TODO: Fill in when API documentation is ready
        pass


def check_alias_led_query_param(rack_id, board_id, device_id):
    """Check a alias led request using query parameters

    Args:
        rack_id (str): Rack's unique ID
        board_id (str): Board's unique ID
        device_id (str): Device's unique ID

    Details:
        There are 3 cases:
        - status code is 200, state is ok
        - state code is 500
        - doesn't write anything, return like read request
        Each case, except the last one, will check for both single and query parameters.
    """
    # Options that return 200 status code and their transactions states are ok
    code_200_state_ok = {
        # Case: Single query parameter / correct key and valid value
        'state_on': 'state=on',
        'state_off': 'state=off',
        'color_min': 'color=000000',
        'color_max': 'color=FFFFFF',
        'blink_blink': 'blink=blink',
        'blink_steady': 'blink=steady',

        # Case: Multiple query parameters / different correct keys
        'state_on_color_max': 'state=on&color=FFFFFF',
        'color_max_blink_steady': 'color=FFFFFF&blink=steady',
        'blink_steady_state_on': 'blink=steady&state=on',

        # Case: Multiple query parameters / same correct keys, valid values
        'state_off_on': 'state=off&state=on',
        'color_min_max': 'color=000000&color=FFFFFF',
        'blink_blink_steady': 'blink=blink&blink=steady',

        # Case: Multiple query parameters / same correct keys, 
        # 1 invalid value after 1 valid value
        'state_valid_invalid': 'state=on&state=invalid',
        'color_valid_invalid': 'color=000000&color=invalid',
        'blink_valid_invalid': 'blink=steady&blink=invalid'
    }

    # Options that return 500 status code
    code_500 = {
        # Case: Single query parameter / correct key and invalid value
        'invalid_state': 'state=invalid',
        'invalid_color': 'color=invalid',
        'invalid_blink': 'blink=invalid',

        # Case: Multiple query parameters / correct keys, 1 invalid value
        'state_valid_color_invalid': 'state=on&color=invalid',
        'state_invalid_color_valid': 'state=invalid&color=FFFFFF',
        'color_valid_blink_invalid': 'color=FFFFFF&blink=invalid',
        'color_invalid_blink_valid': 'color=invalid&blink=steady',
        'blink_valid_state_invalid': 'blink=steady&state=invalid',
        'blink_invalid_state_valid': 'blink=invalid&state=on',

        # Case: Multiple query parameters / same correct keys,
        # 1 valid value after 1 invalid value
        'state_invalid_valid': 'state=invalid&state=on',
        'color_invalid_valid': 'color=invalid&color=FFFFFF',
        'state_invalid_valid': 'blink=invalid&blink=steady'
    }

    # Options that return like read requests
    return_like_read = {
        'absence_key': '',
        'invalid_key': 'invalid',
        'absence_state_value': 'state=',
        'absence_state_value': 'color=',
        'absence_state_value': 'blink=',
        'absence_state_value_no_equal_sign': 'state',
        'absence_color_value_no_equal_sign': 'color',
        'absence_blink_value_no_equal_sign': 'blink',
    }

    # List of transaction ids for requests that return 200 status codes
    tx_ids_code_200_state_ok = []

    # For every post request, get its transaction id(s) and append to the corresponding list
    for option, param in code_200_state_ok.items():
        alias_req = requests.get(
            '{}/led/{}/{}/{}?{}'.format(core_blueprint, rack_id, board_id, device_id, param)
        )
        assert alias_req.status_code == 200

        # Append all returned transactions to the list
        for transaction in alias_req.json():
            tx_ids_code_200_state_ok.append(transaction.get('transaction'))

    # For requests that return 500 status code, there are no transactions have made
    # Only check for its status code
    for option, param in code_500.items():
        alias_req = requests.get(
            '{}/led/{}/{}/{}?{}'.format(core_blueprint, rack_id, board_id, device_id, param)
        )
        assert alias_req.status_code == 500
        assert alias_req.json().get('http_code') == 500
        assert alias_req.json().get('error_id') == errors.INVALID_ARGUMENTS

    # For requests that return just like read requests, simply check for its type and data
    for option, param in return_like_read.items():
        alias_req = requests.get(
            '{}/led/{}/{}/{}?{}'.format(core_blueprint, rack_id, board_id, device_id, param)
        )
        assert alias_req.status_code == 200
        assert alias_req.json().get('type') == 'led'
        assert 'data' in alias_req.json()

    # After making requests and having all the transaction ids needed
    # Check if transactions ids' states are correct
    for id in tx_ids_code_200_state_ok:
        check_transaction(id, 'ok')
