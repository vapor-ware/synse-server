"""Test the 'synse.i18n' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-argument

import gettext

import pytest

from synse import config, i18n

# --- Helper Functions ---

def change_config_locale(value):
    """Helper method to change the locale key in synse.config.options.
    """
    config.options['locale'] = value


# --- Mock Methods ---

def mock_get_translator():
    """Used to replace i18n._get_translator().
        Returns: Nulltranslations object.
    """
    return gettext.translation('', '', fallback=True)


# --- Test Fixtures ---

@pytest.fixture()
def clean_i18n():
    """Temporarily reverses the i18n_passthrough fixture.
    """
    mock_trans = i18n.trans_func
    i18n.trans_func = i18n.old_trans_func

    yield

    i18n.trans_func = mock_trans


# --- Test Cases ---

def test_gettext_raises(clean_i18n):
    """Test that i18n.gettext() correctly raises an error when called before initialization.
    """
    error_string = 'i18n.gettext() not yet initialized, i18n.init_gettext() must be called first.'
    with pytest.raises(RuntimeError) as r_err:
        i18n.gettext('Gettext should not be initialized.')

    assert error_string in str(r_err)

def test_gettext_translates(clean_i18n):
    """Tests that i18n.gettext() correctly returns a string when using a Nulltranslations object.
    """
    i18n._get_translator = mock_get_translator
    i18n.init_gettext()
    assert i18n.gettext('Message string.') == 'Message string.'


def test_i18n_init(clean_i18n):
    """Tests that i18n.init_gettext() correctly initializes the module.
    """
    i18n._get_translator = mock_get_translator
    assert i18n.trans_func is None
    i18n.init_gettext()
    assert i18n.trans_func.__self__.__class__ == gettext.NullTranslations
    assert i18n.gettext('Message string.') == 'Message string.'


def test_get_language_none():
    """Tests that i18n._get_language() returns 'en_US' when config has None as locale key.
    """
    change_config_locale(None)
    assert i18n._get_language() == 'en_US'


def test_get_language_str():
    """Tests that i18n._get_language() returns the correct config key.
    """
    change_config_locale('this is a string')
    assert i18n._get_language() == 'this is a string'
