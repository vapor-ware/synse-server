"""Test the 'synse.proto.util' Synse Server module."""

import pytest
from synse_plugin import api

from synse.proto import util


def test_write_status_name():
    """Get the status name for supported statuses."""

    values = {
        0: 'unknown',
        1: 'pending',
        2: 'writing',
        3: 'done'
    }

    for value, expected in values.items():
        assert util.write_status_name(value) == expected


def test_write_status_name_invalid():
    """Get the status name for an invalid status."""

    with pytest.raises(ValueError):
        util.write_status_name(100)


def test_write_state_name():
    """Get the state name for supported states."""

    values = {
        0: 'ok',
        1: 'error'
    }

    for value, expected in values.items():
        assert util.write_state_name(value) == expected


def test_write_state_name_invalid():
    """Get the state name for an invalid state."""

    with pytest.raises(ValueError):
        util.write_state_name(100)


def test_device_info_to_dict():
    """Convert a Device object to dictionary."""

    meta = api.Device(
        timestamp='october',
        uid='12345',
        kind='thermistor',
        metadata=dict(
            model='test',
            manufacturer='vapor io',
        ),
        plugin='foo',
        info='bar',
        location=api.Location(
            rack='rack-1',
            board='vec'
        ),
        output=[
            api.Output(
                type='temperature',
                precision=3,
                unit=api.Unit(
                    name='celsius',
                    symbol='C'
                )
            )
        ]
    )

    actual = util.device_info_to_dict(meta)

    assert actual == {
        'timestamp': 'october',
        'uid': '12345',
        'kind': 'thermistor',
        'metadata': {
            'model': 'test',
            'manufacturer': 'vapor io',
        },
        'plugin': 'foo',
        'info': 'bar',
        'location': {
            'rack': 'rack-1',
            'board': 'vec'
        },
        'output': [
            {
                'name': '',
                'scaling_factor': 0.0,
                'type': 'temperature',
                'precision': 3,
                'unit': {
                    'name': 'celsius',
                    'symbol': 'C',
                }
            }
        ]
    }


def test_output_to_dict():
    """Convert an Output object to dictionary."""

    meta = api.Output(
        type='temperature',
        precision=3,
        unit=api.Unit(
            name='celsius',
            symbol='C'
        )
    )

    actual = util.output_to_dict(meta)

    assert actual == {
        'name': '',
        'type': 'temperature',
        'precision': 3,
        'scaling_factor': 0.0,
        'unit': {
            'name': 'celsius',
            'symbol': 'C',
        }
    }
