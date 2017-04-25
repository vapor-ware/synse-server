#!/usr/bin/env python
""" Wrappers around http methods to provide a common implementation for all
Vapor components to use.

    Author: Erick Daniszewski
    Date:   05/17/2016
    
    \\//
     \/apor IO
"""
import requests.exceptions
import requests
import logging

from errors import *
from headers import VAPOR_IDENTITY_HASH
from utils.trust import get_local_hash, trust_enabled, validate_response
from utils.cache import Cache
from constants import LOCAL_HASH

logger = logging.getLogger(__name__)


# define package-level constants for all http methods
DEFAULT_TIMEOUT = 5

GET = 'get'
POST = 'post'

# check whether trust is enabled. this will only happen once on
# module import. the assumption being that if the container starts
# up in trusted mode, we expect it to stay in trusted mode and vice
# versa.
#
# FIXME: is the above assumption ok, or will we want to periodically
#        re-evaluate this?
_trust_enabled = trust_enabled()

# create a global cache for the http module. this will be used to store
# the known trusted identity hashes.
# TODO - could make the ttl configurable, but its a bit less obvious how
#        since there is no set config for vapor_common (vapor_common#54)
_CACHE = Cache(ttl=300)


def _update_local_hash():
    """ Update the cache with the value for the local cache.
    """
    try:
        _identity_hash = get_local_hash()
    except Exception as e:
        logger.warning('Failed to get local hash for http module ({})'.format(e))
        _identity_hash = None

    if _identity_hash is not None:
        _CACHE.set(LOCAL_HASH, _identity_hash)


def disable_warnings():
    """ Disable the warnings raised by urllib3 around ssl certs.

    The warning in question::

        SecurityWarning: Certificate has no `subjectAltName`, falling back
        to check for a `commonName` for now.
    """
    requests.packages.urllib3.disable_warnings()


def request_ok(status_code):
    """ Check if a request is ok.

    Here, we define "ok" as having a response code within [200, 300).
    See https://httpstatuses.com/ for more details.

    Args:
        status_code (int):

    Returns:
        bool
    """
    return 200 <= status_code < 300


def _request(method, url, timeout, **kwargs):
    """ Base method for sending an HTTP request.

    All other methods defined in this module which send HTTP requests should
    call this method.

    Args:
        method (str): the HTTP method for the requests. supported methods are
            defined as module level constants.
        url (str): URL to issue the request against.
        timeout (int | tuple): the timeout period for the request.
        **kwargs (dict): additional arguments for the request.
            (see `requests.request` for supported kwargs)

    Returns:
        requests.Response: the `requests.Response` object returned by the request.

    Raises:
        VaporRequestError: a requests error was encountered when sending the
            HTTP request.
        VaporError: an unexpected exception was encountered when sending the
            HTTP request.
    """
    if _trust_enabled:
        if LOCAL_HASH not in _CACHE:
            _update_local_hash()

        identity_hash = _CACHE.get(LOCAL_HASH)
        if identity_hash is None:
            raise RequestValidationError(
                'Trusted mode is enabled, but the identity hash could not be determined.'
            )

        if kwargs:
            if 'headers' in kwargs:
                kwargs['headers'][VAPOR_IDENTITY_HASH] = identity_hash
            else:
                kwargs['headers'] = {VAPOR_IDENTITY_HASH: identity_hash}
        else:
            kwargs = {'headers': {VAPOR_IDENTITY_HASH: identity_hash}}

    try:
        # as per the stack overflow solution below (for getting response IP), we need
        # to have the request issued with stream=True. In this case, stream=False is
        # only possible if explicitly set in the request kwargs. Note that in this case
        # trust validation is almost assured to fail, since we will not be able to get
        # the response_ip.
        if 'stream' not in kwargs:
            kwargs['stream'] = True
        response = requests.request(method=method, url=url, timeout=timeout, **kwargs)

        try:
            # see: http://stackoverflow.com/a/22513161
            response_ip = response.raw._connection.sock.getpeername()[0]
            logger.debug('Response IP: {}'.format(response_ip))
        except Exception as e:
            logger.warning('Failed to get IP of response: {}'.format(e))
            response_ip = None

    except requests.exceptions.RequestException as e:
        logger.error('Failed to issue request ({}): {}'.format(url, e))
        raise VaporRequestError(e)

    except Exception as e:
        logger.error('Unexpected exception encountered ({}): {}'.format(url, e))
        raise VaporError(e)

    else:
        # we will only want to perform validation if the request is OK.
        if request_ok(response.status_code):
            if _trust_enabled:
                validated = validate_response(response, response_ip, _CACHE)
                if not validated:
                    raise RequestValidationError('Failed to validate request response! ({})'.format(response_ip))

        return response


def request(method, url, timeout=DEFAULT_TIMEOUT, **kwargs):
    """ Send a request and assess the requests success based on the response
    status code.

    Args:
        method (str): the HTTP method for the requests. supported methods are
            defined as module level constants.
        url (str): URL to issue the request against.
        timeout (int | tuple): the timeout period for the request.
            (default: `DEFAULT_TIMEOUT`)
        **kwargs (dict): additional arguments for the request.
            (see `requests.request` for supported kwargs)

    Returns:
        requests.Response: the `requests.Response` object returned by the request.

    Raises:
        VaporRequestError: a requests error was encountered when sending the
            HTTP request.
        VaporError: an unexpected exception was encountered when sending the
            HTTP request.
        VaporHTTPError: a request was made but the response came back with a status
            that has been deemed as not OK.
    """
    response = _request(method=method, url=url, timeout=timeout, **kwargs)

    if not request_ok(response.status_code):
        raise VaporHTTPError(response)

    else:
        return response


def get(url, **kwargs):
    """ Send a GET request to the specified URL.

    Args:
        url (str): URL to issue the request against.
        **kwargs (dict): additional arguments for the request.
            (see `requests.request` for supported kwargs)

    Returns:
        requests.Response: the `requests.Response` object returned by the request.
    """
    return request(GET, url, **kwargs)


def post(url, **kwargs):
    """ Send a POST request to the specified URL.

    Args:
        url (str): URL to issue the request against.
        **kwargs (dict): additional arguments for the request.
            (see `requests.request` for supported kwargs)

    Returns:
        requests.Response: the `requests.Response` object returned by the request.
    """
    return request(POST, url, **kwargs)
