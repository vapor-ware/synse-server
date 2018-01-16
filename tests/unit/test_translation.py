"""
Test that log messages are translated correctly.
    As more languages are supported, they should have their own tests.
"""

import pytest

from synse import config, factory


def test_locale_install():
    """Test that gettext correctly translates a given string.
    """
    config.options['locale'] = 'en_US'
    factory._setup_local()

    assert gettext('Running "scan" command.') == 'Running "scan" command.'

def test_locale_fallback():
    """Test that gettext correctly defaults to en_US when language is invalid.
    """
    config.options['locale'] = 'invalid'
    factory._setup_local()

    assert gettext('Running "scan" command.') == 'Running "scan" command.'

def test_locale_empty():
    """Test that gettext correctly defaults to en_US when language is blank.
    """
    config.options['locale'] = ''
    factory._setup_local()

    assert gettext('Running "scan" command.') == 'Running "scan" command.'

def test_locale_none():
    """Test that gettext correctly defaults to en_US when language is None.
    """
    config.options['locale'] = None
    with pytest.raises(AttributeError):
        factory._setup_local()
