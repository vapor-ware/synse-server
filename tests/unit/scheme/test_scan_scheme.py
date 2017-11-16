"""Test the 'synse.scheme.scan' Synse Server module."""

from synse.scheme.scan import ScanResponse


def test_scan_scheme():
    """Test that the scan scheme matches the expected."""

    data = {
        'rack': 'rack-1',
        'boards': [
            {
                'board': 'board-1',
                'devices': []
            }
        ]
    }

    response_scheme = ScanResponse(data)

    # the scan response just takes in whatever data it is given.
    assert response_scheme.data == data
