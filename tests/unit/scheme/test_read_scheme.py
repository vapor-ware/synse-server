"""Test the 'synse.scheme.read' Synse Server module.
"""

from synse.scheme.read import ReadResponse

from synse_plugin import api


def make_metainfo_response():
    """Convenience method to create MetainfoResponse test data."""
    return api.MetainfoResponse(
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


def test_read_scheme():
    """Test that the read scheme matches the expected.
    """
    dev = make_metainfo_response()

    rr = api.ReadResponse(
        timestamp='november',
        type='temperature',
        value='10'
    )

    response_scheme = ReadResponse(dev, [rr])

    assert response_scheme.data == {
        'type': 'thermistor',
        'data': {
            'temperature': {
                'value': '10.0',
                'timestamp': 'november',
                'unit': {
                    'name': 'celsius',
                    'symbol': 'C'
                }
            }
        }
    }


def test_read_scheme_with_precision_rounding():
    """Test that the read scheme matches the expected when the read value
    must be rounded to the specified precision.
    """
    dev = make_metainfo_response()

    rr = api.ReadResponse(
        timestamp='november',
        type='temperature',
        value='10.1234567'
    )

    response_scheme = ReadResponse(dev, [rr])

    assert response_scheme.data == {
        'type': 'thermistor',
        'data': {
            'temperature': {
                'value': '10.123',
                'timestamp': 'november',
                'unit': {
                    'name': 'celsius',
                    'symbol': 'C'
                }
            }
        }
    }


def test_read_scheme_with_precision_rounding_2():
    """Test that the read scheme matches the expected when the read value
    must be rounded to the specified precision.
    """
    dev = make_metainfo_response()

    rr = api.ReadResponse(
        timestamp='november',
        type='temperature',
        value='10.98765432'
    )

    response_scheme = ReadResponse(dev, [rr])

    assert response_scheme.data == {
        'type': 'thermistor',
        'data': {
            'temperature': {
                'value': '10.988',
                'timestamp': 'november',
                'unit': {
                    'name': 'celsius',
                    'symbol': 'C'
                }
            }
        }
    }


def test_read_scheme_with_no_matching_readings():
    """Test that the read scheme matches the expected when no matching
    readings are provided.
    """
    dev = make_metainfo_response()

    rr = api.ReadResponse(
        timestamp='november',
        type='humidity',
        value='5'
    )

    response_scheme = ReadResponse(dev, [rr])

    assert response_scheme.data == {
        'type': 'thermistor',
        'data': {}
    }


def test_read_scheme_no_unit():
    """Test that the read scheme matches the expected when no unit is given
    for the device
    """
    dev = make_metainfo_response()
    dev.output[0].unit.name = ''
    dev.output[0].unit.symbol = ''

    rr = api.ReadResponse(
        timestamp='november',
        type='temperature',
        value='10.98765432'
    )

    response_scheme = ReadResponse(dev, [rr])

    assert response_scheme.data == {
        'type': 'thermistor',
        'data': {
            'temperature': {
                'value': '10.988',
                'timestamp': 'november',
                'unit': {
                    'name': '',
                    'symbol': ''
                }
            }
        }
    }


def test_read_scheme_no_precision():
    """Test that the read scheme matches the expected when no precision is given
    for the device
    """
    dev = make_metainfo_response()
    dev.output[0].precision = 0

    rr = api.ReadResponse(
        timestamp='november',
        type='temperature',
        value='10.98765432'
    )

    response_scheme = ReadResponse(dev, [rr])

    assert response_scheme.data == {
        'type': 'thermistor',
        'data': {
            'temperature': {
                'value': '10.98765432',
                'timestamp': 'november',
                'unit': {
                    'name': 'celsius',
                    'symbol': 'C'
                }
            }
        }
    }
