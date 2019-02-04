"""Test the 'synse_server.version' Synse Server module."""

import synse_server
import synse_server.version


def test_version():
    """Test that the version module returns the version correctly."""
    actual = synse_server.__version__

    act_maj, act_min, _ = actual.split('.')

    assert synse_server.version.major == act_maj
    assert synse_server.version.minor == act_min
    assert synse_server.version.__api_version__ == 'v' + act_maj
