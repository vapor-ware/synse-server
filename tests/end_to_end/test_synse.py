"""End to end tests for Synse Server.

These tests are designed to run against an instance of
Synse Server with an emulator plugin backing configured.

The goal of this test is to provide end-to-end validation
of all components. They do not care about the values that
are returned as much as that the responses/schemes return
as expected.
"""
# pylint: disable=line-too-long

import os
import time

import pytest
import requests
import ujson

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

    @classmethod
    def is_airflow(cls, device):
        """Check if the device ID corresponds to an airflow type device."""
        return device in cls.airflow

    @classmethod
    def is_temperature(cls, device):
        """Check if the device ID corresponds to a temperature type device."""
        return device in cls.temperature

    @classmethod
    def is_pressure(cls, device):
        """Check if the device ID corresponds to a pressure type device."""
        return device in cls.pressure

    @classmethod
    def is_humidity(cls, device):
        """Check if the device ID corresponds to a humidity type device."""
        return device in cls.humidity

    @classmethod
    def is_led(cls, device):
        """Check if the device ID corresponds to an LED type device."""
        return device in cls.led

    @classmethod
    def is_fan(cls, device):
        """Check if the device ID corresponds to a fan type device."""
        return device in cls.fan


def url_unversioned(uri):
    """Create the unversioned URL for Synse Server with the given URI."""
    return 'http://{}:5000/synse/{}'.format(host, uri)


def url(uri):
    """Create the versioned URL for Synse Server with the given URI."""
    return 'http://{}:5000/synse/{}/{}'.format(host, __api_version__, uri)


def validate_write_ok(data, size):
    """Helper to validate that write response schemes are correct."""
    assert isinstance(data, list)
    assert len(data) == size

    for item in data:
        assert 'context' in item
        assert 'transaction' in item

        context = item['context']
        transaction = item['transaction']

        assert isinstance(context, dict)
        assert isinstance(transaction, str)

        assert 'action' in context
        assert 'raw' in context


def wait_for_transaction(transaction_id):
    """Helper to check the transaction state. This will wait until
    the transaction is in a done state, or 5 seconds.
    """
    start = time.time()
    while True:
        now = time.time()
        if now - start > 5:
            pytest.fail('Failed to resolve transaction state (timeout)')

        response = requests.get(url('transaction/{}'.format(transaction_id)))
        assert response.status_code == 200

        data = response.json()
        validate_transaction(data)

        state = data['state']
        status = data['status']

        if (state == 'ok' and status == 'done') or (state == 'error'):
            return data

        time.sleep(0.1)


def validate_transaction(data):
    """Helper to validate that transaction check response schemes are correct."""
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

    assert state in ['ok', 'error']
    assert status in ['unknown', 'pending', 'writing', 'done']


def validate_read(data):
    """Helper to validate that read response schemes are correct."""
    assert isinstance(data, dict)

    assert 'type' in data
    assert 'data' in data

    t = data['type']
    d = data['data']

    # lookup maps the reading type to the fields that reading type should provide
    lookup = {
        'temperature': ['temperature'],
        'led': ['color', 'state'],
        'fan': ['fan_speed'],
        'airflow': ['airflow'],
        'pressure': ['pressure'],
        'humidity': ['temperature', 'humidity']
    }

    keys = lookup.get(t)
    if keys is None:
        pytest.fail('Reading type unknown: {}'.format(data))

    assert isinstance(d, dict)
    for k in keys:
        assert k in d


def validate_error_response(data, http_code, error_code):
    """Helper to validate that error response schemes are correct."""
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


def validate_scan(data):
    """Helper to validate that scan response schemes are correct."""
    assert isinstance(data, dict)
    assert 'racks' in data

    racks = data['racks']
    assert isinstance(racks, list)
    assert len(racks) == 1  # as per the emulator config for the tests

    for rack in racks:
        validate_scan_rack(rack)


def validate_scan_rack(rack):
    """Validate the data for a rack scan result."""
    assert isinstance(rack, dict)
    assert 'id' in rack
    assert 'boards' in rack
    assert rack['id'] == 'rack-1'  # as per the emulator config for the tests

    boards = rack['boards']
    assert isinstance(boards, list)
    assert len(boards) == 1  # as per the emulator config for the tests

    for board in boards:
        validate_scan_board(board)


def validate_scan_board(board):
    """Validate the data for a board scan result."""
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
        if EmulatorDevices.is_led(_id):
            assert device['type'] == 'led'
        elif EmulatorDevices.is_humidity(_id):
            assert device['type'] == 'humidity'
        elif EmulatorDevices.is_pressure(_id):
            assert device['type'] == 'pressure'
        elif EmulatorDevices.is_temperature(_id):
            assert device['type'] == 'temperature'
        elif EmulatorDevices.is_airflow(_id):
            assert device['type'] == 'airflow'
        elif EmulatorDevices.is_fan(_id):
            assert device['type'] == 'fan'
        else:
            pytest.fail('Unexpected device type: {}'.format(device))


# -------------------------------
# Test Cases
# -------------------------------

#
# Status
#

class TestStatus(object):
    """Tests for the 'test' route."""

    def test_status_ok(self):
        """Test Synse Server's 'test' route."""
        response = requests.get(url_unversioned('test'))
        assert response.status_code == 200

        data = response.json()
        assert 'status' in data
        assert 'timestamp' in data
        assert data['status'] == 'ok'


#
# Version
#

class TestVersion(object):
    """Tests for the 'version' route."""

    def test_version_ok(self):
        """Test Synse Server's 'version' route."""
        response = requests.get(url_unversioned('version'))
        assert response.status_code == 200

        data = response.json()
        assert 'version' in data
        assert 'api_version' in data
        assert data['version'] == __version__
        assert data['api_version'] == __api_version__


#
# Config
#

class TestConfig(object):
    """Tests for the 'config' route."""

    def test_config_ok(self):
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


#
# Plugins
#

class TestPlugins(object):
    """Tests for the 'plugins' route."""

    def test_plugins_ok(self):
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


#
# Scan
#

class TestScan(object):
    """Tests for the 'scan' route."""

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
    def test_scan_ok(self, params):
        """Test Synse Server's 'scan' route."""
        response = requests.get(url('scan'), params=params)
        assert response.status_code == 200

        data = response.json()
        validate_scan(data)

    def test_scan_rack_ok(self):
        """Test Synse Server's 'scan' route, at rack resolution."""
        response = requests.get(url('scan/rack-1'))
        assert response.status_code == 200

        data = response.json()
        validate_scan_rack(data)

    def test_scan_rack_error(self):
        """Test Synse Server's 'scan' route, at rack resolution, when the rack does not exist."""
        response = requests.get(url('scan/unknown-rack'))
        assert response.status_code == 404

        data = response.json()
        validate_error_response(data, 404, errors.RACK_NOT_FOUND)

    def test_scan_board_ok(self):
        """Test Synse Server's 'scan' route, at board resolution."""
        response = requests.get(url('scan/rack-1/vec'))
        assert response.status_code == 200

        data = response.json()
        validate_scan_board(data)

    def test_scan_board_error(self):
        """Test Synse Server's 'scan' route, at board resolution, when the board does not exist."""
        response = requests.get(url('scan/rack-1/unknown-board'))
        assert response.status_code == 404

        data = response.json()
        validate_error_response(data, 404, errors.BOARD_NOT_FOUND)

    def test_scan_device_error(self):
        """Test Synse Server's 'scan' route, at device resolution. This is not supported
        so we expect it to fail.
        """
        response = requests.get(url('scan/rack-1/vec/eb9a56f95b5bd6d9b51996ccd0f2329c'))
        assert response.status_code == 404

        data = response.json()
        validate_error_response(data, 404, errors.URL_NOT_FOUND)

    @pytest.mark.parametrize(
        'params', [
            {'force': 'true', 'invalid': 'param'},
            {'foo': 'bar'},
        ]
    )
    def test_scan_bad_params(self, params):
        """Test Synse Server's 'scan' route while passing in invalid query parameters."""
        response = requests.get(url('scan'), params=params)
        assert response.status_code == 400

        error = response.json()
        validate_error_response(error, 400, errors.INVALID_ARGUMENTS)


#
# Read
#

class TestRead(object):
    """Tests for the 'read' route."""

    @pytest.mark.parametrize(
        'device', EmulatorDevices.all
    )
    def test_read_ok(self, device):
        """Test Synse Server's 'read' route while passing in valid devices to be
        read from.
        """
        response = requests.get(url('read/rack-1/vec/{}'.format(device)))
        assert response.status_code == 200

        data = response.json()
        validate_read(data)

    @pytest.mark.parametrize(
        'rack,board,device', [
            ('rack-1', 'vec', 'abcdefg'),
            ('rack-1', 'no-such-board', '29d1a03e8cddfbf1cf68e14e60e5f5cc'),
            ('rack-none', 'vec', '29d1a03e8cddfbf1cf68e14e60e5f5cc'),
        ]
    )
    def test_read_bad_info(self, rack, board, device):
        """Test Synse Server's 'read' route will passing in invalid rack, board,
        and device info to read from.
        """
        response = requests.get(url('read/{}/{}/{}'.format(rack, board, device)))
        assert response.status_code == 404

        data = response.json()
        # all of these errors should be device not found - this may seem strange
        # since we have invalid rack and invalid board here, but we expect device
        # not found because it comes from the check for device resolution.
        validate_error_response(data, 404, errors.DEVICE_NOT_FOUND)

    def test_read_bad_query_params(self):
        """Test Synse Server's 'read' route, passing in query parameters.

        The read route does not support query parameters, so it should return
        a 400 error.
        """
        response = requests.get(
            url('read/rack-1/vec/29d1a03e8cddfbf1cf68e14e60e5f5cc'),
            params={'foo': 'bar'}
        )
        assert response.status_code == 400

        data = response.json()
        validate_error_response(data, 400, errors.INVALID_ARGUMENTS)


#
# Write
#

class TestWrite(object):
    """Tests for the 'write' route."""

    @pytest.mark.parametrize(
        'device', EmulatorDevices.led
    )
    def test_write_ok(self, device):
        """Test Synse Server's 'write' route, specifying writeable devices."""
        response = requests.post(
            url('write/rack-1/vec/{}'.format(device)),
            data=ujson.dumps({'action': 'color', 'raw': 'ff00ff'})
        )
        assert response.status_code == 200

        data = response.json()
        validate_write_ok(data, 1)

        for t in data:
            transaction_id = t['transaction']
            transaction = wait_for_transaction(transaction_id)

            assert transaction['state'] == 'ok'
            assert transaction['status'] == 'done'

    @pytest.mark.parametrize(
        'device', filter(lambda x: x not in EmulatorDevices.fan + EmulatorDevices.led, EmulatorDevices.all)
    )
    def test_write_error(self, device):
        """Test Synse Server's 'write' route, specifying non-writable devices."""
        response = requests.post(
            url('write/rack-1/vec/{}'.format(device)),
            data=ujson.dumps({'action': 'foo', 'raw': 'bar'})
        )
        assert response.status_code == 500

        data = response.json()
        validate_error_response(data, 500, errors.FAILED_WRITE_COMMAND)

    @pytest.mark.parametrize(
        'data', [
            {},
            {'raw': 'bar'},
            {'foo': 'bar'}
        ]
    )
    def test_write_bad_args(self, data):
        """Test Synse Server's 'write' route, passing in bad write data."""
        device = EmulatorDevices.led[0]

        response = requests.post(url('write/rack-1/vec/{}'.format(device)), data=ujson.dumps(data))
        assert response.status_code == 400

        data = response.json()
        validate_error_response(data, 400, errors.INVALID_ARGUMENTS)

    @pytest.mark.parametrize(
        'data', [
            {'action': 'foo'},
            {'action': 'state', 'raw': 'value'},
            {'action': 'color'},
            {'action': 'color', 'raw': 'not-a-color'}
        ]
    )
    def test_write_invalid_json(self, data):
        """Test Synse Server's 'write' route, passing in bad data to the plugin."""
        device = EmulatorDevices.led[0]

        response = requests.post(url('write/rack-1/vec/{}'.format(device)), data=ujson.dumps(data))
        assert response.status_code == 200

        data = response.json()
        validate_write_ok(data, 1)

        for t in data:
            transaction_id = t['transaction']
            transaction = wait_for_transaction(transaction_id)

            assert transaction['state'] == 'error'
            assert transaction['status'] == 'done'


#
# Info
#

class TestInfo(object):
    """Tests for the 'info' route."""

    def test_rack_info_no_ctx(self):
        """Test Synse Server's 'info' route providing no context. This
        should result in a test failure.
        """
        response = requests.get(url('info'))
        assert response.status_code == 404

        data = response.json()
        validate_error_response(data, 404, errors.URL_NOT_FOUND)

    def test_rack_info_ok(self):
        """Test Synse Server's 'info' route at the rack level."""
        response = requests.get(url('info/rack-1'))
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert 'rack' in data
        assert 'boards' in data

        assert data['rack'] == 'rack-1'
        assert isinstance(data['boards'], list)
        assert len(data['boards']) == 1
        assert data['boards'][0] == 'vec'

    def test_rack_info_error(self):
        """Test Synse Server's 'info' route at the rack level, when the
        rack does not exist.
        """
        response = requests.get(url('info/invalid-rack'))
        assert response.status_code == 404

        data = response.json()
        validate_error_response(data, 404, errors.RACK_NOT_FOUND)

    def test_board_info_ok(self):
        """Test Synse Server's 'info' route at the board level."""
        response = requests.get(url('info/rack-1/vec'))
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert 'board' in data
        assert data['board'] == 'vec'

        assert 'location' in data
        assert isinstance(data['location'], dict)
        assert 'rack' in data['location']
        assert data['location']['rack'] == 'rack-1'

        assert 'devices' in data
        assert isinstance(data['devices'], list)
        assert len(data['devices']) == len(EmulatorDevices.all)
        for device in data['devices']:
            assert device in EmulatorDevices.all

    def test_board_info_error(self):
        """Test Synse Server's 'info' route at the board level, when the
        board does not exist.
        """
        response = requests.get(url('info/rack-1/invalid-board'))
        assert response.status_code == 404

        data = response.json()
        validate_error_response(data, 404, errors.BOARD_NOT_FOUND)

    @pytest.mark.parametrize(
        'device', EmulatorDevices.all
    )
    def test_device_info_ok(self, device):
        """Test Synse Server's 'info' route at the device level."""
        response = requests.get(url('info/rack-1/vec/{}'.format(device)))
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert 'timestamp' in data
        assert 'uid' in data
        assert 'type' in data
        assert 'model' in data
        assert 'manufacturer' in data
        assert 'protocol' in data
        assert 'info' in data
        assert 'comment' in data
        assert 'location' in data
        assert 'output' in data

        assert isinstance(data['location'], dict)
        assert 'rack' in data['location']
        assert 'board' in data['location']
        assert data['location']['rack'] == 'rack-1'
        assert data['location']['board'] == 'vec'

    def test_device_info_error(self):
        """Test Synse Server's 'info' route at the device level, when the
        device does not exist.
        """
        response = requests.get(url('info/rack-1/vec/invalid-device'))
        assert response.status_code == 404

        data = response.json()
        validate_error_response(data, 404, errors.DEVICE_NOT_FOUND)


#
# LED
#

class TestLED(object):
    """Tests for the 'led' route."""

    @pytest.mark.parametrize(
        'device', EmulatorDevices.led
    )
    def test_led_read_ok(self, device):
        """Test Synse Server's 'led' route, specifying valid LED devices to read from."""
        response = requests.get(url('led/rack-1/vec/{}'.format(device)))
        assert response.status_code == 200

        data = response.json()
        validate_read(data)

    @pytest.mark.parametrize(
        'device', EmulatorDevices.led
    )
    def test_led_write_ok(self, device):
        """Test Synse Server's 'led' route, specifying valid LED devices to write to
        for a single writing value.
        """
        response = requests.get(url('led/rack-1/vec/{}'.format(device)), params={'color': 'ff00ff'})
        assert response.status_code == 200

        data = response.json()
        validate_write_ok(data, 1)

        for t in data:
            transaction_id = t['transaction']
            transaction = wait_for_transaction(transaction_id)

            assert transaction['state'] == 'ok'
            assert transaction['status'] == 'done'

    @pytest.mark.parametrize(
        'device', EmulatorDevices.led
    )
    def test_led_write_multi_ok(self, device):
        """Test Synse Server's 'led' route, specifying valid LED devices to write to
        for multiple writing values.
        """
        response = requests.get(
            url('led/rack-1/vec/{}'.format(device)),
            params={'color': '00ffff', 'state': 'on'}
        )
        assert response.status_code == 200

        data = response.json()
        validate_write_ok(data, 2)

        for t in data:
            transaction_id = t['transaction']
            transaction = wait_for_transaction(transaction_id)

            assert transaction['state'] == 'ok'
            assert transaction['status'] == 'done'

    @pytest.mark.parametrize(
        'device', filter(lambda x: x not in EmulatorDevices.led, EmulatorDevices.all)
    )
    def test_led_read_bad_device(self, device):
        """Test Synse Server's 'led' route, specifying a non-LED device to read from."""
        response = requests.get(url('led/rack-1/vec/{}'.format(device)))
        assert response.status_code == 400

        data = response.json()
        validate_error_response(data, 400, errors.INVALID_DEVICE_TYPE)

    @pytest.mark.parametrize(
        'device', filter(lambda x: x not in EmulatorDevices.led, EmulatorDevices.all)
    )
    def test_led_write_bad_device(self, device):
        """Test Synse Server's 'led' route, specifying a non-LED device to write to."""
        response = requests.get(url('led/rack-1/vec/{}'.format(device)), params={'color': 'ff0000'})
        assert response.status_code == 400

        data = response.json()
        validate_error_response(data, 400, errors.INVALID_DEVICE_TYPE)

    @pytest.mark.parametrize(
        'device,params', [(device, params) for params in [
            {'foo': 'bar'},
            {'color': '00ff00', 'foo': 'bar'},
            {'color': 'this is not a color'},
            {'state': 'on', 'foo': 'bar'},
            {'state': 'invalid-state'}
        ] for device in EmulatorDevices.led]
    )
    def test_led_write_bad_params(self, device, params):
        """Test Synse Server's 'led' route, specifying invalid query parameters for write."""
        response = requests.get(url('led/rack-1/vec/{}'.format(device)), params=params)
        assert response.status_code == 400

        data = response.json()
        validate_error_response(data, 400, errors.INVALID_ARGUMENTS)


#
# Fan
#

class TestFan(object):
    """Tests for the 'fan' route."""

    @pytest.mark.parametrize(
        'device', EmulatorDevices.fan
    )
    def test_fan_read_ok(self, device):
        """Test Synse Server's 'fan' route, specifying valid fan devices to read from."""
        response = requests.get(url('fan/rack-1/vec/{}'.format(device)))
        assert response.status_code == 200

        data = response.json()
        validate_read(data)

    @pytest.mark.parametrize(
        'device', EmulatorDevices.fan
    )
    def test_fan_write_ok(self, device):
        """Test Synse Server's 'fan' route, specifying valid fan devices to write to."""
        response = requests.get(url('fan/rack-1/vec/{}'.format(device)), params={'speed': '50'})
        assert response.status_code == 200

        data = response.json()
        validate_write_ok(data, 1)

        for t in data:
            transaction_id = t['transaction']
            transaction = wait_for_transaction(transaction_id)

            assert transaction['state'] == 'ok'
            assert transaction['status'] == 'done'

    @pytest.mark.parametrize(
        'device', filter(lambda x: x not in EmulatorDevices.fan, EmulatorDevices.all)
    )
    def test_fan_read_bad_device(self, device):
        """Test Synse Server's 'fan' route, specifying non-fan devices to read from."""
        response = requests.get(url('fan/rack-1/vec/{}'.format(device)))
        assert response.status_code == 400

        data = response.json()
        validate_error_response(data, 400, errors.INVALID_DEVICE_TYPE)

    @pytest.mark.parametrize(
        'device', filter(lambda x: x not in EmulatorDevices.fan, EmulatorDevices.all)
    )
    def test_fan_write_bad_device(self, device):
        """Test Synse Server's 'fan' route, specifying non-fan devices to write to."""
        response = requests.get(url('fan/rack-1/vec/{}'.format(device)), params={'speed': '30'})
        assert response.status_code == 400

        data = response.json()
        validate_error_response(data, 400, errors.INVALID_DEVICE_TYPE)

    @pytest.mark.parametrize(
        'device,params', [(device, params) for params in [
            {'foo': 'bar'},
            {'speed': '50', 'foo': 'bar'},
            {'speed_percent': '50', 'speed': '10'}
        ] for device in EmulatorDevices.fan]
    )
    def test_fan_write_bad_params(self, device, params):
        """Test Synse Server's 'fan' route, specifying invalid query parameters for write."""
        response = requests.get(url('fan/rack-1/vec/{}'.format(device)), params=params)
        assert response.status_code == 400

        data = response.json()
        validate_error_response(data, 400, errors.INVALID_ARGUMENTS)
