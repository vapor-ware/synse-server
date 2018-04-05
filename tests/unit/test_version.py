"""Test the 'synse.version' Synse Server module."""

import synse
import synse.version


def test_version():
    """Test that the version module returns the version correctly."""
    actual = synse.__version__

    act_maj, act_min, _ = actual.split('.')

    assert synse.version.major == act_maj
    assert synse.version.minor == act_min
    assert synse.version.__api_version__ == act_maj + '.' + act_min
    assert synse.version.__version__ == actual
