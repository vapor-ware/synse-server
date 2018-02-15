"""Functions to setup gettext translations.
"""
import gettext as _gettext
import os

from synse import config
from synse.log import logger

trans_func = None


def _get_locale_dir():
    """Returns path to `locale` directory adjacent to this source file if it exists,
        otherwise raises an IOError.
    """
    # TODO This is not the most robust method of finding the locale file.
    locale_dir = '{}/locale'.format(os.path.dirname(os.path.realpath(__file__)))
    if os.path.isdir(locale_dir):
        return locale_dir
    else:
        raise IOError(
            '{} locale directory does not exit.'
            .format(locale_dir)
            )


def _get_language():
    """Attempts to load the value of the "locale" key from the config.
        If there is a value for "locale", it is returned, otherwise we return "en_US".
    """
    lang = config.options.get('locale')
    if lang:
        return lang

    # If lang is None for some reason (i.e. config isn't loaded)
    # log a warning and just use en_US.
    logger.warning('No language found in config, defaulting to en_US.')
    return 'en_US'


def _get_translator():
    """Attempts to intialize a translations object based on the provided language.
        If the provided language is not supported, it will default to en_US.

        Returns: NullTranslations object.
    """
    locale_dir = _get_locale_dir()
    language = _get_language()
    trans = _gettext.translation('synse', locale_dir, languages=[language], fallback=True)

    if trans.__class__ == _gettext.NullTranslations:
        # If gettext failed to find a translation file, it will fallback to the default messages.
        logger.warning(
            'Translation files for {} were not found. Using default language (en_US)'
            .format(language)
            )

    return trans


def init_gettext():
    """Initializes a translator, and makes it's gettext method publicly available.
    """
    global trans_func
    trans_func = _get_translator().gettext


def gettext(text):
    """Takes a string, and passes it through the translator that was created during initialization.
        This function will raise an error if it is called before init_gettext()

        Args:
            text (string): String to be translated.

        Returns:
            string: Translated string (if gettext can translate it).
    """
    if trans_func:
        return trans_func(text)
    else:
        # If this method is called before initialization, something is wrong, so we raise.
        raise RuntimeError(
            'i18n.gettext() not yet initialized, i18n.init_gettext() must be called first.'
            )
