"""Test the 'synse_server.scheme.read' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-variable

import pytest
from synse_grpc import api

from synse_server.scheme.read import ReadResponse


def make_device_response():
    """Convenience method to create Device test data."""
    return api.Device(
        timestamp='october',
        uid='12345',
        kind='thermistor',
        metadata=dict(
            model='test',
            manufacturer='vapor io'
        ),
        plugin='foo',
        info='bar',
        location=api.Location(
            rack='rack-1',
            board='vec'
        ),
        output=[
            api.Output(
                name='foo.temperature',
                type='temperature',
                precision=3,
                unit=api.Unit(
                    name='celsius',
                    symbol='C'
                )
            )
        ]
    )


def test_read_scheme():
    """Test that the read scheme matches the expected."""
    dev = make_device_response()

    reading = api.Reading(
        timestamp='november',
        type='temperature',
        int64_value=10
    )

    response_scheme = ReadResponse(dev, [reading])

    assert response_scheme.data == {
        'kind': 'thermistor',
        'data': [
            {
                'info': '',
                'type': 'temperature',
                'value': 10.0,
                'timestamp': 'november',
                'unit': {
                    'name': 'celsius',
                    'symbol': 'C'
                }
            }
        ]
    }


def test_read_scheme_empty_string_value():
    """Test that the read scheme matches the expected when the read value
    is an empty string.
    """
    dev = make_device_response()

    reading = api.Reading(
        timestamp='november',
        type='temperature',
        string_value=''
    )

    response_scheme = ReadResponse(dev, [reading])

    assert response_scheme.data == {
        'kind': 'thermistor',
        'data': [
            {
                'info': '',
                'type': 'temperature',
                'value': '',  # an empty string is a valid value
                'timestamp': 'november',
                'unit': {
                    'name': 'celsius',
                    'symbol': 'C'
                }
            }
        ]
    }


def test_read_scheme_null_value():
    """Test that the read scheme matches the expected when there is no read value.
    """
    dev = make_device_response()

    reading = api.Reading(
        timestamp='november',
        type='temperature',
    )

    response_scheme = ReadResponse(dev, [reading])

    assert response_scheme.data == {
        'kind': 'thermistor',
        'data': [
            {
                'info': '',
                'type': 'temperature',
                'value': None,
                'timestamp': 'november',
                'unit': {
                    'name': 'celsius',
                    'symbol': 'C'
                }
            }
        ]
    }


def test_read_scheme_wrong_type_value():
    """Test that the read scheme matches the expected when the read value
    has the wrong type.
    """
    with pytest.raises(TypeError):
        _ = api.Reading(
            timestamp='november',
            type='temperature',
            string_value=101
        )


def test_read_scheme_non_convertible_value():
    """Test that the read scheme matches the expected when the read value
    is non-convertible.

    In this case, it doesn't raise the error but log a warning.
    The error value is still processed and left for the plugin level to handle.
    """
    dev = make_device_response()

    reading = api.Reading(
        timestamp='november',
        type='temperature',
        string_value='101a'
    )

    response_scheme = ReadResponse(dev, [reading])

    assert response_scheme.data == {
        'kind': 'thermistor',
        'data': [
            {
                'info': '',
                'type': 'temperature',
                'value': '101a',
                'timestamp': 'november',
                'unit': {
                    'name': 'celsius',
                    'symbol': 'C'
                }
            }
        ]
    }


def test_read_scheme_with_precision_rounding():
    """Test that the read scheme matches the expected when the read value
    must be rounded to the specified precision.
    """
    dev = make_device_response()

    reading = api.Reading(
        timestamp='november',
        type='temperature',
        float64_value=10.1234567
    )

    response_scheme = ReadResponse(dev, [reading])

    assert response_scheme.data == {
        'kind': 'thermistor',
        'data': [
            {
                'info': '',
                'value': 10.123,
                'type': 'temperature',
                'timestamp': 'november',
                'unit': {
                    'name': 'celsius',
                    'symbol': 'C'
                }
            }
        ]
    }


def test_read_scheme_with_precision_rounding_2():
    """Test that the read scheme matches the expected when the read value
    must be rounded to the specified precision.
    """
    dev = make_device_response()

    reading = api.Reading(
        timestamp='november',
        type='temperature',
        float64_value=10.98765432
    )

    response_scheme = ReadResponse(dev, [reading])

    assert response_scheme.data == {
        'kind': 'thermistor',
        'data': [
            {
                'info': '',
                'type': 'temperature',
                'value': 10.988,
                'timestamp': 'november',
                'unit': {
                    'name': 'celsius',
                    'symbol': 'C'
                }
            }
        ]
    }


def test_read_scheme_with_no_matching_readings():
    """Test that the read scheme matches the expected when no matching
    readings are provided.
    """
    dev = make_device_response()

    reading = api.Reading(
        timestamp='november',
        type='humidity',
        int32_value=5
    )

    response_scheme = ReadResponse(dev, [reading])

    assert response_scheme.data == {
        'kind': 'thermistor',
        'data': []
    }


def test_read_scheme_no_unit():
    """Test that the read scheme matches the expected when no unit is given
    for the device
    """
    dev = make_device_response()
    dev.output[0].unit.name = ''
    dev.output[0].unit.symbol = ''

    reading = api.Reading(
        timestamp='november',
        type='temperature',
        float64_value=10.98765432
    )

    response_scheme = ReadResponse(dev, [reading])

    assert response_scheme.data == {
        'kind': 'thermistor',
        'data': [
            {
                'info': '',
                'type': 'temperature',
                'value': 10.988,
                'timestamp': 'november',
                'unit': None
            }
        ]
    }


def test_read_scheme_no_precision():
    """Test that the read scheme matches the expected when no precision is given
    for the device
    """
    dev = make_device_response()
    dev.output[0].precision = 0

    reading = api.Reading(
        timestamp='november',
        type='temperature',
        float64_value=10.98765432
    )

    response_scheme = ReadResponse(dev, [reading])

    assert response_scheme.data == {
        'kind': 'thermistor',
        'data': [
            {
                'info': '',
                'type': 'temperature',
                'value': 10.98765432,
                'timestamp': 'november',
                'unit': {
                    'name': 'celsius',
                    'symbol': 'C'
                }
            }
        ]
    }
