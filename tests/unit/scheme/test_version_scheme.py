"""Test the 'synse.scheme.version' Synse Server module."""

from synse import version
from synse.scheme.version import VersionResponse


def test_version_scheme():
    """Check that the version scheme matches the expected."""

    response_scheme = VersionResponse()

    assert response_scheme.data == {
        'version': version.__version__,
        'api_version': version.__api_version__
    }
