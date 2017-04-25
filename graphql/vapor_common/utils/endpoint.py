#!/usr/bin/env python
""" Vapor Common Endpoint Utilities

    Author: Erick Daniszewski
    Date:   13 Dec 2016
    
    \\//
     \/apor IO
"""
import logging
from functools import partial
from werkzeug.contrib.cache import SimpleCache
from flask import current_app
from flask import request
from flask import abort

from vapor_common.headers import VAPOR_IDENTITY_HASH
import trust


logger = logging.getLogger(__name__)


def make_url_builder(base):
    """ Make a partial function that can be used to cleanly generate URLs.

    The partial function hides the common pieces of the URL leaving only
    the unique part -- the URI -- visible to the caller. This helps to
    keep endpoint definitions clean and readable.

    Args:
        base (str): the base of the URL which everything will be build off
            of - this is the common part of the URL.

    Returns:
        partial: a partial object that can be used to build urls.
    """
    def _url_builder(uri, url_base):
        return url_base + uri
    return partial(_url_builder, url_base=base)


def setup_trust_validation(app, cache_timeout=600, cache_threshold=500):
    """ Configure a Flask application instance to include the methods for
    trust validation.

    Args:
        app: the Flask app to setup trust validation for.
        cache_timeout (int): the timeout value to be set on the identity
            hash cache.
        cache_threshold (int): the threshold limit for the max number
            of entries in the identity hash cache.
    """
    _cache = SimpleCache(default_timeout=cache_timeout, threshold=cache_threshold)
    app.config['IDENTITY_HASH_CACHE'] = _cache

    # the key None in the before_request_funcs dict applies to all routes in all
    # blueprints for the app. we will want to put trust validation here since all
    # endpoints should check for trust.
    fns = app.before_request_funcs.get(None, [])
    fns.append(_validate_trust_on_request)
    app.before_request_funcs[None] = fns

    fns = app.after_request_funcs.get(None, [])
    fns.append(_set_trust_on_response)
    app.after_request_funcs[None] = fns


def _validate_trust_on_request():
    """ Validate that the request originates from a trusted entity.

    Before handling any incoming request, we want to validate that said
    incoming request originated from an entity which we trust. This is
    done in two parts:
      i.  check the header for the requester's identity
      ii. lookup the record for that entity and ensure that other
          bits of metadata support the identity claim.

    There are some exceptions to this, however. If we are running in
    trusted mode and we have internal traffic (e.g. communication
    between containers on the same machine, behind the auth/routing
    component) then we do not need to validate trust since the origin
    of the request is the machine that is validating the trust; a
    machine should always trust itself.

    The other exception here is when we are running in "untrusted"
    mode. In this mode, there are no identity certificates in place
    so there is no basis for trust. This case will be treated as a
    "trust everyone" scenario.

    If the identity of an incoming request cannot be validated, the
    request will terminate with a 403 error. Otherwise, the request
    will continue on through to its appropriate route handler.
    """
    if trust.trust_enabled():
        _cache = current_app.config['IDENTITY_HASH_CACHE']
        if not trust.validate_request(request, _cache):
            logger.error('Failed to validate incoming request: {}'.format(request))
            abort(403)


def _set_trust_on_response(response):
    """ Set the Vapor identity hash header on the outgoing response.

    This identity hash can be used by the caller to perform validation
    that the response is coming from an entity it trusts.

    Args:
        response (Response): the Flask response to set the headers on
    """
    if trust.trust_enabled():
        _cache = current_app.config['IDENTITY_HASH_CACHE']
        identity = _cache.get('local_hash') or trust.get_local_hash()
        if identity is None:
            logger.error('Failed to set identity headers on response: {}'.format(response))
            abort(500)
        response.headers[VAPOR_IDENTITY_HASH] = identity
        return response
    return response
