"""Test the 'synse.scheme.read_cached' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-variable

from synse_grpc import api

from synse.scheme.read_cached import ReadCachedResponse


def test_read_cached_scheme():
    """Test that the read cached scheme matches the expected."""
    dev = api.Device(
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

    reading = api.DeviceReading(
        rack='rack-1',
        board='vec',
        device='12345',
        reading=api.Reading(
            timestamp='november',
            type='temperature',
            int64_value=10
        )
    )

    response_scheme = ReadCachedResponse(dev, reading)

    assert response_scheme.data == {
        'provenance': {
            'rack': 'rack-1',
            'board': 'vec',
            'device': '12345'
        },
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
