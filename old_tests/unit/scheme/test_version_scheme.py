"""Test the 'synse_server.scheme.version' Synse Server module."""

import synse_server
from synse_server.scheme.version import VersionResponse


def test_version_scheme():
    """Check that the version scheme matches the expected."""

    response_scheme = VersionResponse()

    assert response_scheme.data == {
        'version': synse_server.__version__,
        'api_version': synse_server.__api_version__
    }
