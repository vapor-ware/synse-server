"""Test the 'synse.scheme.test' Synse Server module.
"""

from synse.scheme.test import TestResponse as TResp


def test_test_scheme():
    """Test that the test scheme matches the expected.
    """
    response_scheme = TResp()

    assert 'status' in response_scheme.data
    assert 'timestamp' in response_scheme.data

    assert response_scheme.data['status'] == 'ok'
