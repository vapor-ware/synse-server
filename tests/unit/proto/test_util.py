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


def test_metainfo_to_dict():
    """Convert a MetainfoResponse object to dictionary."""

    meta = api.MetainfoResponse(
        timestamp='october',
        uid='12345',
        type='thermistor',
        model='test',
        manufacturer='vapor io',
        protocol='foo',
        info='bar',
        location=api.MetaLocation(
            rack='rack-1',
            board='vec'
        ),
        output=[
            api.MetaOutput(
                type='temperature',
                data_type='float',
                precision=3,
                unit=api.MetaOutputUnit(
                    name='celsius',
                    symbol='C'
                ),
                range=api.MetaOutputRange(
                    min=0,
                    max=100
                )
            )
        ]
    )

    actual = util.metainfo_to_dict(meta)

    assert actual == {
        'timestamp': 'october',
        'uid': '12345',
        'type': 'thermistor',
        'model': 'test',
        'manufacturer': 'vapor io',
        'protocol': 'foo',
        'info': 'bar',
        'comment': '',
        'location': {
            'rack': 'rack-1',
            'board': 'vec'
        },
        'output': [
            {
                'type': 'temperature',
                'data_type': 'float',
                'precision': 3,
                'unit': {
                    'name': 'celsius',
                    'symbol': 'C',
                },
                'range': {
                    'min': 0,
                    'max': 100
                }
            }
        ]
    }


def test_metaoutput_to_dict():
    """Convert a MetaOutput object to dictionary."""

    meta = api.MetaOutput(
        type='temperature',
        data_type='float',
        precision=3,
        unit=api.MetaOutputUnit(
            name='celsius',
            symbol='C'
        ),
        range=api.MetaOutputRange(
            min=0,
            max=100
        )
    )

    actual = util.metaoutput_to_dict(meta)

    assert actual == {
        'type': 'temperature',
        'data_type': 'float',
        'precision': 3,
        'unit': {
            'name': 'celsius',
            'symbol': 'C',
        },
        'range': {
            'min': 0,
            'max': 100
        }
    }
