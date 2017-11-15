"""Test the 'synse.scheme.info' Synse Server module.
"""

from synse.scheme.info import InfoResponse


def test_info_scheme():
    """Test that the info scheme matches the expected.
    """
    data = {
        'rack': 'rack-1',
        'boards': [
            '123456',
            '789012',
            'abcdef',
            'foo'
        ]
    }

    response_scheme = InfoResponse(data)

    # the info response just takes in whatever data it is given.
    assert response_scheme.data == data
