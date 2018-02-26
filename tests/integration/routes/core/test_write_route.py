"""Test the 'synse.routes.core' module's write route."""
# pylint: disable=redefined-outer-name,unused-argument

import ujson

from synse import errors
from synse.version import __api_version__
from tests import utils

invalid_write_url = '/synse/{}/write/invalid-rack/invalid-board/invalid-device'.format(__api_version__)


def test_write_invalid_endpoint_valid_data(app):
    """Test posting a invalid write request with valid POST data.

    Details:
        In this case, rack, board, device are invalid.
        With the valid POST data, keys are corrects and values are valid,
        the returned error should be DEVICE_NOT_FOUND.

        The reason we assume that values are valid is because,
        not like end-to-end test when we have emulator plugin enabled,
        no test data is available for integration test.
        Therefore, there is no real device's value that we can count on.
    """
    valid_post_data = {
        'correct_keys': {
            'action': 'valid',
            'raw': 'valid'
        },
        'incorrect_action': {
            'incorrect_action': 'valid',
            'raw': 'valid'
        },
        'incorrect_raw': {
            'action': 'valid',
            'incorrect_raw': 'valid'
        },
        'absence_action': {
            'raw': 'valid'
        },
        'absence_raw': {
            'action': 'valid'
        }
    }

    for option, payload in valid_post_data.items():
        _, response = app.test_client.post(invalid_write_url, data=ujson.dumps(payload))
        utils.test_error_json(response, errors.DEVICE_NOT_FOUND)


def test_write_invalid_endpoint_invalid_data(app):
    """Test posting a invalid write response with invalid POST data.

    Details:
        In this case, rack, board, device are invalid.
        With the invalid POST data, no key is existed,
        the returned error should be INVALID_ARGUMENTS
    """
    invalid_post_data = {
        'empty': {},
        'incorrect_key': {
            'incorrect_key': 'valid'
        }
    }
    
    for option, payload in invalid_post_data.items():
        _, response = app.test_client.post(invalid_write_url, data=ujson.dumps(payload))
        utils.test_error_json(response, errors.INVALID_ARGUMENTS)


def test_write_endpoint_post_not_allowed(app):
    """Invalid request: GET"""
    _, response = app.test_client.get(invalid_write_url)
    assert response.status == 405


def test_write_endpoint_put_not_allowed(app):
    """Invalid request: PUT"""
    _, response = app.test_client.put(invalid_write_url)
    assert response.status == 405


def test_write_endpoint_delete_not_allowed(app):
    """Invalid request: DELETE"""
    _, response = app.test_client.delete(invalid_write_url)
    assert response.status == 405


def test_write_endpoint_patch_not_allowed(app):
    """Invalid request: PATCH"""
    _, response = app.test_client.patch(invalid_write_url)
    assert response.status == 405


def test_write_endpoint_head_not_allowed(app):
    """Invalid request: HEAD"""
    _, response = app.test_client.head(invalid_write_url)
    assert response.status == 405


def test_write_endpoint_options_not_allowed(app):
    """Invalid request: OPTIONS"""
    _, response = app.test_client.options(invalid_write_url)
    assert response.status == 405
