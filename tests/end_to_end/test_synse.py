"""End to end tests for Synse Server.

These tests are designed to run against an instance of
Synse Server with an emulator plugin backing configured.

The goal of this test is to provide end-to-end validation
of all components. They do not care about the values that
are returned as much as that the responses/schemes return
as expected.
"""
# pylint: disable=redefined-outer-name,unused-argument

import os
import time

import pytest
import requests

from synse import errors
from synse.version import __api_version__, __version__

# get the host information via ENV, or use the default of localhost
host = os.environ.get('SYNSE_TEST_HOST', 'localhost')


# -------------------------------
# Test Utilities
# -------------------------------

class EmulatorDevices(object):
    """EmulatorDevices is a container that defines the well-known device
    IDs for the emulator devices. Since the emulator is configured the
    same way for these tests, it should always produce the same device
    IDs.

    Note that if the emulator configuration changes, these IDs may need
    to be changed, updated, or added to.
    """
    airflow = [
        '29d1a03e8cddfbf1cf68e14e60e5f5cc'
    ]

    temperature = [
        '329a91c6781ce92370a3c38ba9bf35b2',
        '83cc1efe7e596e4ab6769e0c6e3edf88',
        'db1e5deb43d9d0af6d80885e74362913',
        'eb100067acb0c054cf877759db376b03',
        'f97f284037b04badb6bb7aacd9654a4e'
    ]

    pressure = [
        '5b2ce651ad91715c96ec71f4096c5d0e',
        'f3dd2a56b588f181c5c782f45467b214'
    ]

    humidity = [
        'bbadeee4d96ca38ffbcaabb3d8837526'
    ]

    led = [
        'd29e0bd113a484dc48fd55bd3abad6bb',
        'f52d29fecf05a195af13f14c7306cfed'
    ]

    fan = [
        'eb9a56f95b5bd6d9b51996ccd0f2329c'
    ]

    all = airflow + temperature + pressure + humidity + led + fan


def url_unversioned(uri):
    """Create the unversioned URL for Synse Server with the given URI."""
    return 'http://{}:5000/synse/{}'.format(host, uri)


def url(uri):
    """Create the versioned URL for Synse Server with the given URI."""
    return 'http://{}:5000/synse/{}/{}'.format(host, __api_version__, uri)


def validate_write_ok(data):
    """"""
    assert isinstance(data, list)

    for item in data:
        assert 'context' in item
        assert 'transaction' in item

        context = item['context']
        transaction = item['transaction']

        assert isinstance(context, dict)
        assert isinstance(transaction, str)

        assert 'action' in context
        assert 'raw' in context


def validate_transaction_ok(data):
    """"""
    # FIXME -- wait until status is DONE or we are in ERROR state..
    assert isinstance(data, dict)

    assert 'id' in data
    assert 'context' in data
    assert 'state' in data
    assert 'status' in data
    assert 'created' in data
    assert 'updated' in data
    assert 'message' in data

    _id = data['id']
    context = data['context']
    state = data['state']
    status = data['status']
    created = data['created']
    updated = data['updated']
    message = data['message']

    assert isinstance(_id, str)
    assert isinstance(context, dict)
    assert isinstance(state, str)
    assert isinstance(status, str)
    assert isinstance(created, str)
    assert isinstance(updated, str)
    assert isinstance(message, str)

    assert state == 'ok'
    assert status in ['unknown', 'pending', 'writing', 'done']


def validate_read(data):
    """"""
    assert isinstance(data, dict)

    assert 'type' in data
    assert 'data' in data


def validate_error_response(data, http_code, error_code):
    """"""
    assert isinstance(data, dict)

    assert 'http_code' in data
    assert 'error_id' in data
    assert 'description' in data
    assert 'timestamp' in data
    assert 'context' in data

    assert isinstance(data['http_code'], int)
    assert isinstance(data['error_id'], int)
    assert isinstance(data['description'], str)
    assert isinstance(data['timestamp'], str)
    assert isinstance(data['context'], str)

    assert data['http_code'] == http_code
    assert data['error_id'] == error_code


# -------------------------------
# Test Cases
# -------------------------------

def test_status_ok():
    """Test Synse Server's 'test' route."""
    response = requests.get(url_unversioned('test'))
    assert response.status_code == 200

    data = response.json()
    assert 'status' in data
    assert 'timestamp' in data
    assert data['status'] == 'ok'


def test_version_ok():
    """Test Synse Server's 'version' route."""
    response = requests.get(url_unversioned('version'))
    assert response.status_code == 200

    data = response.json()
    assert 'version' in data
    assert 'api_version' in data
    assert data['version'] == __version__
    assert data['api_version'] == __api_version__


def test_config_ok():
    """Test Synse Server's 'config' route."""
    response = requests.get(url('config'))
    assert response.status_code == 200

    data = response.json()

    # the expected configuration keys (default config)
    expected = {
        'cache': {
            'meta': {'ttl': 20},
            'transaction': {'ttl': 300}
        },
        'grpc': {'timeout': 3},
        'locale': 'en_US',
        'logging': 'debug',
        'plugin': {'tcp': {}, 'unix': {}},
        'pretty_json': True
    }

    assert expected == data


def test_plugins_ok():
    """Test Synse Server's 'plugins' route.

    Since this test runs against a Synse Server instance with an emulator
    instance configured, we expect that emulator to be the only plugin
    present here.
    """
    response = requests.get(url('plugins'))
    assert response.status_code == 200

    data = response.json()

    # we expect to have only the emulator plugin configured
    assert isinstance(data, list)
    assert len(data) == 1
    plugin = data[0]

    assert 'name' in plugin
    assert 'network' in plugin
    assert 'address' in plugin

    assert plugin['name'] == 'emulator'
    assert plugin['network'] == 'unix'
    assert plugin['address'] == '/tmp/synse/procs/emulator.sock'


@pytest.mark.parametrize(
    'params', [
        {},
        {'force': 'true'},
        {'force': 'TRUE'},
        {'force': 'True'},
        {'force': 'tRuE'},
        {'force': 'false'},
        {'force': 'FALSE'},
        {'force': 'False'},
        {'force': 'fAlSe'},
    ]
)
def test_scan_ok(params):
    """Test Synse Server's 'scan' route."""
    response = requests.get(url('scan'), params=params)
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert 'racks' in data

    racks = data['racks']
    assert isinstance(racks, list)
    assert len(racks) == 1

    rack = racks[0]
    assert isinstance(rack, dict)
    assert 'id' in rack
    assert 'boards' in rack
    assert rack['id'] == 'rack-1'  # as per the emulator config for the tests

    boards = rack['boards']
    assert isinstance(boards, list)
    assert len(boards) == 1

    board = boards[0]
    assert isinstance(board, dict)
    assert 'id' in board
    assert 'devices' in board
    assert board['id'] == 'vec'  # as per the emulator config for the tests

    devices = board['devices']
    assert isinstance(devices, list)
    assert len(devices) == len(EmulatorDevices.all)

    for device in devices:
        assert isinstance(device, dict)
        assert 'id' in device
        assert 'info' in device
        assert 'type' in device

        _id = device['id']
        assert _id in EmulatorDevices.all
        if _id in EmulatorDevices.led:
            assert device['type'] == 'led'
        elif _id in EmulatorDevices.humidity:
            assert device['type'] == 'humidity'
        elif _id in EmulatorDevices.pressure:
            assert device['type'] == 'pressure'
        elif _id in EmulatorDevices.temperature:
            assert device['type'] == 'temperature'
        elif _id in EmulatorDevices.airflow:
            assert device['type'] == 'airflow'
        elif _id in EmulatorDevices.fan:
            assert device['type'] == 'fan'
        else:
            raise ValueError('Unexpected device type: {}'.format(device))


@pytest.mark.parametrize(
    'params', [
        {'force': 'true', 'invalid': 'param'},
        {'foo': 'bar'},
    ]
)
def test_scan_bad_params(params):
    """Test Synse Server's 'scan' route while passing in invalid query parameters."""
    response = requests.get(url('scan'), params=params)
    assert response.status_code == 400

    error = response.json()
    validate_error_response(error, 400, errors.INVALID_ARGUMENTS)


@pytest.mark.parametrize(
    'device', EmulatorDevices.all
)
def test_read_ok(device):
    """"""
    response = requests.get(url('read/rack-1/vec/{}'.format(device)))
    assert response.status_code == 200

    data = response.json()
    validate_read(data)


@pytest.mark.parametrize(
    'rack,board,device,error_id', [
        ('rack-1', 'vec', 'abcdefg', errors.DEVICE_NOT_FOUND),
        ('rack-1', 'no-such-board', '29d1a03e8cddfbf1cf68e14e60e5f5cc', errors.BOARD_NOT_FOUND),
        ('rack-none', 'vec', '29d1a03e8cddfbf1cf68e14e60e5f5cc', errors.RACK_NOT_FOUND),
    ]
)
def test_read_bad_info(rack, board, device, error_id):
    """"""
    response = requests.get(url('read/{}/{}/{}'.format(rack, board, device)))
    assert response.status_code == 404

    data = response.json()
    validate_error_response(data, 404, error_id)


def test_read_bad_query_params():
    """"""
    response = requests.get(url('read/rack-1/vec/29d1a03e8cddfbf1cf68e14e60e5f5cc'), params={'foo': 'bar'})
    assert response.status_code == 400

    data = response.json()
    validate_error_response(data, 400, errors.INVALID_ARGUMENTS)


@pytest.mark.parametrize(
    'device', EmulatorDevices.led
)
def test_led_read_ok(device):
    """"""
    response = requests.get(url('led/rack-1/vec/{}'.format(device)))
    assert response.status_code == 200

    data = response.json()
    validate_read(data)


@pytest.mark.parametrize(
    'device', EmulatorDevices.led
)
def test_led_write_ok(device):
    """"""
    response = requests.get(url('led/rack-1/vec/{}'.format(device)), args={'color': 'ff00ff'})
    assert response.status_code == 200

    data = response.json()
    validate_write_ok(data)

    transaction_id = data['transaction']
    # TODO - validate transaction


@pytest.mark.parametrize(
    'device', EmulatorDevices.led
)
def test_led_write_multi_ok(device):
    """"""
    response = requests.get(url('led/rack-1/vec/{}'.format(device)), args={'color': '00ffff', 'state': 'on'})
    assert response.status_code == 200

    data = response.json()
    validate_write_ok(data)

    transaction_id = data['transaction']
    # TODO - validate transaction


@pytest.mark.parametrize(
    'device', filter(lambda x: x not in EmulatorDevices.led, EmulatorDevices.all)
)
def test_led_read_bad_device(device):
    """"""
    response = requests.get(url('led/rack-1/vec/{}'.format(device)))
    assert response.status_code == 400

    data = response.json()
    validate_error_response(data, 400, errors.INVALID_DEVICE_TYPE)


@pytest.mark.parametrize(
    'device', filter(lambda x: x not in EmulatorDevices.led, EmulatorDevices.all)
)
def test_led_write_bad_device(device):
    """"""
    response = requests.get(url('led/rack-1/vec/{}'.format(device)), params={'color': 'ff0000'})
    assert response.status_code == 400

    data = response.json()
    validate_error_response(data, 400, errors.INVALID_DEVICE_TYPE)


@pytest.mark.parametrize(
    'device', EmulatorDevices.led
)
def test_led_write_bad_params(device):
    """"""
    # TODO -- add qparams to the parametrize
    response = requests.get(url('led/rack-1/vec/{}'.format(device)))
    assert response.status_code == 400

    data = response.json()
    validate_error_response(data, 400, errors.INVALID_ARGUMENTS)


@pytest.mark.parametrize(
    'device', EmulatorDevices.fan
)
def test_fan_read_ok(device):
    """"""
    response = requests.get(url('fan/rack-1/vec/{}'.format(device)))
    assert response.status_code == 200

    data = response.json()
    validate_read(data)


@pytest.mark.parametrize(
    'device', EmulatorDevices.fan
)
def test_fan_write_ok(device):
    """"""
    response = requests.get(url('fan/rack-1/vec/{}'.format(device)), params={'speed': '50'})
    assert response.status_code == 200

    data = response.json()
    validate_write_ok(data)

    transaction_id = data['transaction']
    # TODO - validate transaction


@pytest.mark.parametrize(
    'device', filter(lambda x: x not in EmulatorDevices.fan, EmulatorDevices.all)
)
def test_fan_read_bad_device(device):
    """"""
    response = requests.get(url('fan/rack-1/vec/{}'.format(device)))
    assert response.status_code == 400

    data = response.json()
    validate_error_response(data, 400, errors.INVALID_DEVICE_TYPE)


@pytest.mark.parametrize(
    'device', filter(lambda x: x not in EmulatorDevices.fan, EmulatorDevices.all)
)
def test_fan_write_bad_device(device):
    """"""
    response = requests.get(url('fan/rack-1/vec/{}'.format(device)), params={'speed': '30'})
    assert response.status_code == 400

    data = response.json()
    validate_error_response(data, 400, errors.INVALID_DEVICE_TYPE)


@pytest.mark.parametrize(
    'device', EmulatorDevices.fan
)
def test_fan_write_bad_params(device):
    """"""
    # TODO - params in parametrize
    response = requests.get(url('fan/rack-1/vec/{}'.format(device)))
    assert response.status_code == 400

    data = response.json()


'''
def test_end_to_end():
    """Main entry point for all the tests"""
    # Perform a general scan
    scan_req = requests.get('{}/scan'.format(url))
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
'''

def check_rack_scan(rack, rack_id):
    """Check a scan request for given rack

    Args:
        rack (dict): Rack object from the general scan
        rack_id (str): Rack's unique ID
    """
    rack_scan_req = requests.get('{}/scan/{}'.format(url, rack_id))
    assert rack_scan_req.status_code == 200
    assert rack_scan_req.json().get('id') == rack_id
    assert rack_scan_req.json() == rack


def check_rack_info(boards_ids, rack_id):
    """Check an info request for a given rack

    Args:
        boards_ids (list): List of boards' IDs from the general scan
        rack_id (str): Rack's unique ID
    """
    rack_info_req = requests.get('{}/info/{}'.format(url, rack_id))
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
    board_info_req = requests.get('{}/scan/{}/{}'.format(url, rack_id, board_id))
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
    board_info_req = requests.get('{}/info/{}/{}'.format(url, rack_id, board_id))
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
        '{}/scan/{}/{}/{}'.format(url, rack_id, board_id, device_id)
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
        '{}/info/{}/{}/{}'.format(url, rack_id, board_id, device_id)
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
        '{}/read/{}/{}/{}'.format(url, rack_id, board_id, device_id)
    )
    assert device_read_req.status_code == 200
    assert device_read_req.json().get('type') == device_type

    data = device_read_req.json().get('data')
    assert data is not None

    if device_type == 'led':
        assert 'state' in data
        assert 'color' in data
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
                    action's value is not valid                     -> 200, error
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
                    action's value is not valid                     -> 200, error
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
        'state_blink': {
            'action': 'state',
            'raw': 'blink'
        },
        'color_min': {
            'action': 'color',
            'raw': '000000'
        },
        'color_max': {
            'action': 'color',
            'raw': 'FFFFFF'
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
    }

    # Options that return 200 status codes and their transactions' states are error
    code_200_state_error = {
        # Case: 2 keys are correct, action value is valid
        'state_invalid_raw_value': {
            'action': 'state',
            'raw': 'invalid'
        },

        # LED color write isn't validated so the test fail
        'color_invalid_value': {
            'action': 'color',
            'raw': 'invalid'
        },

        # Case: 1 key is correct / action is correct, action's value is not valid
        # Because raw is incorrect, raw's value can be anything even if it's valid
        'correct_action_invalid_value': {
            'action': 'invalid',
            'incorrect_raw': 'on/off/blink/ffffff'
        },

        # Case: 1 key is absence / raw is absence, action's value is not valid
        # If the value is valid, see synse-emulator-plugin's issue #2
        'absence_raw_invalid_action_value': {
            'action': 'invalid'
        },

        # Case: 1 key is correct / action is correct, action's value is valid
        # It returns 200 status code and break the program.
        'state_incorrect_raw': {
            'action': 'state',
            'incorrect_raw': 'on'
        },
        'color_incorrect_raw': {
            'action': 'color',
            'incorrect_raw': '000000'
        },

        # Case: 1 key is absence / raw is absence, action's value is valid
        'state_absence_raw': {
            'action': 'state'
        },
        'color_absence_raw': {
            'action': 'color'
        }
    }

    # Options that return 500 status codes
    code_400 = {
        # Case: 2 keys are not correct
        # Because both keys are wrong, their value can be anything
        'incorrect_keys': {
            'incorrect_action': 'state/color',
            'incorrect_raw': 'on/000000'
        },

        # Case: 1 key is correct / raw is correct, raw's value is valid
        # Because action is incorrect, action's value can be anything
        # Therefore, no need to check for a specific state or color
        'correct_raw_valid_value': {
            'incorrect_action': 'state/color',
            'raw': 'on'
        },

        # Case: 1 key is correct / raw is correct, raw's value is not valid
        # Similarly, action is incorrect, no need to check for a specific value
        'correct_raw_invalid_value': {
            'incorrect_action': 'state/color',
            'raw': 'invalid'
        },

        # Case: 1 key is absence / action is absence, raw's value is valid
        # Because action is absence, raw's value can be anything, even if it's valid
        'absence_action': {
            'raw': 'valid/invalid'
        },

        # Case: 2 keys are absence
        'no_keys': {}
    }

    # List of transactions objects for requests that return 200 status codes
    # Each transaction object have its checking case, inherited from these cases above, and its id
    tx_code_200_state_ok = []
    tx_code_200_state_error = []

    # For every post request, get its transaction id and append to the corresponding list
    # along with its checking case
    # We only append the first returned transaction because at the moment,
    # it is only possible to write one value at a time
    for case, payload in code_200_state_ok.items():
        write_req = requests.post(
            '{}/write/{}/{}/{}'.format(url, rack_id, board_id, device_id),
            json=payload
        )
        assert write_req.status_code == 200

        tx_code_200_state_ok.append({
            'case': case,
            'id': write_req.json()[0].get('transaction')
        })

    for case, payload in code_200_state_error.items():
        write_req = requests.post(
            '{}/write/{}/{}/{}'.format(url, rack_id, board_id, device_id),
            json=payload
        )
        assert write_req.status_code == 200

        tx_code_200_state_error.append({
            'case': case,
            'id': write_req.json()[0].get('transaction')
        })

    # For requests that return 500 status code, there are no transactions have made
    # Only check for its status code
    for case, payload in code_400.items():
        write_req = requests.post(
            '{}/write/{}/{}/{}'.format(url, rack_id, board_id, device_id),
            json=payload
        )
        assert write_req.status_code == 400

    # After making write requests and having all the transaction ids needed
    # Check if transactions ids' states are correct
    for case in tx_code_200_state_ok:
        check_transaction(case['case'], case['id'], 'ok')

    for case in tx_code_200_state_error:
        check_transaction(case['case'], case['id'], 'error')


def check_transaction(case, transaction_id, expected_state):
    """Check a transaction request for a given transaction id and state

    Args:
        case(str): Transaction's checking case
        transaction_id (str): Transaction's unique ID
        expected_state (str): Expected state of the transaction
    """
    r = requests.get('{}/transaction/{}'.format(url, transaction_id))
    if r.status_code != 200:
        print(r.json())
    assert r.status_code == 200

    # If a transaction is done processing, check if it match the expected state
    # Otherwise, sleep for some time and check again
    if r.json().get('status') == 'done':
        assert r.json().get('state') == expected_state
    else:
        time.sleep(0.1)
        check_transaction(case, transaction_id, expected_state)


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
        '{}/write/{}/{}/{}'.format(url, rack_id, board_id, device_id),
        json={}
    )
    assert temperature_write_req.status_code == 400
    assert temperature_write_req.json().get('http_code') == 400
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
        '{}/{}/{}/{}/{}'.format(url, device_type, rack_id, board_id, device_id)
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
        'state_blink': 'state=blink',
        'color_min': 'color=000000',
        'color_max': 'color=FFFFFF',

        # Case: Multiple query parameters / different correct keys
        'state_on_color_max': 'state=on&color=FFFFFF',
        'color_max_state_blink': 'color=FFFFFF&state=blink',

        # Case: Multiple query parameters / same correct keys, valid values
        'state_off_on_blink': 'state=off&state=on&state=blink',
        'color_min_max': 'color=000000&color=FFFFFF',

        # Case: Multiple query parameters / same correct keys,
        # 1 invalid value after 1 valid value
        'state_valid_invalid': 'state=on&state=invalid',
        'color_valid_invalid': 'color=000000&color=invalid',
    }

    # Options that return 400 status code
    code_400 = {
        # Case: Single query parameter / correct key and invalid value
        'invalid_state': 'state=invalid',
        'invalid_color': 'color=invalid',

        # Case: Multiple query parameters / correct keys, 1 invalid value
        'state_valid_color_invalid': 'state=on&color=invalid',
        'state_invalid_color_valid': 'state=invalid&color=FFFFFF',
        'color_valid_state_invalid': 'color=FFFFFF&state=invalid',
        'color_invalid_state_valid': 'color=invalid&state=on',

        # Case: Multiple query parameters / same correct keys,
        # 1 valid value after 1 invalid value
        'state_invalid_valid': 'state=invalid&state=on',
        'color_invalid_valid': 'color=invalid&color=FFFFFF',
    }

    # Options that return like read requests
    return_like_read = {
        'absence_key': '',
        'invalid_key': 'invalid',
        'absence_state_value': 'state=',
        'absence_color_value': 'color=',
        'absence_state_value_no_equal_sign': 'state',
        'absence_color_value_no_equal_sign': 'color',
    }

    # List of transactions objects for requests that return 200 status codes
    # Similar to checking write request, each transaction object has its checking case and id
    tx_code_200_state_ok = []

    # For every post request, get its transaction id(s) and append to the corresponding list
    for case, param in code_200_state_ok.items():
        alias_req = requests.get(
            '{}/led/{}/{}/{}?{}'.format(url, rack_id, board_id, device_id, param)
        )
        assert alias_req.status_code == 200

        # Using alias route, we can write multiple values for a device
        # Each successful write has its own transaction id
        # Therefore, unlike the write request, we need to append all the returned
        # transactions to the list, instead of just the first one
        for transaction in alias_req.json():
            tx_code_200_state_ok.append({
                'case': case,
                'id': transaction.get('transaction')
            })

    # For requests that return 500 status code, there are no transactions have made
    # Only check for its status code
    for case, param in code_400.items():
        alias_req = requests.get(
            '{}/led/{}/{}/{}?{}'.format(url, rack_id, board_id, device_id, param)
        )
        assert alias_req.status_code == 400
        assert alias_req.json().get('http_code') == 400
        assert alias_req.json().get('error_id') == errors.INVALID_ARGUMENTS

    # For requests that return just like read requests, simply check for its type and data
    for case, param in return_like_read.items():
        alias_req = requests.get(
            '{}/led/{}/{}/{}?{}'.format(url, rack_id, board_id, device_id, param)
        )
        assert alias_req.status_code == 200
        assert alias_req.json().get('type') == 'led'
        assert 'data' in alias_req.json()

    # After making requests and having all the transaction ids needed
    # Check if transactions ids' states are correct
    for case in tx_code_200_state_ok:
        check_transaction(case['case'], case['id'], 'ok')
