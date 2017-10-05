#!/usr/bin/env python
""" Wrappers around http methods to provide a common implementation for all
Vapor components to use.

    Author: Erick Daniszewski
    Date:   05/17/2016

    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

This file is part of Synse.

Synse is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

Synse is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Synse.  If not, see <http://www.gnu.org/licenses/>.
"""

import logging

import requests
import requests.exceptions

from synse.vapor_common.errors import (VaporError, VaporHTTPError,
                                       VaporRequestError)

logger = logging.getLogger(__name__)


# define package-level constants for all http methods
DEFAULT_TIMEOUT = 5

GET = 'get'
POST = 'post'


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
    try:
        response = requests.request(method=method, url=url, timeout=timeout, **kwargs)

    except requests.exceptions.RequestException as e:
        logger.error('Failed to issue request ({}): {}'.format(url, e))
        raise VaporRequestError(e)

    except Exception as e:
        logger.error('Unexpected exception encountered ({}): {}'.format(url, e))
        raise VaporError(e)

    else:
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
