#!/usr/bin/env python
""" Utility methods for Container Trust and Trust Management

    Author: Erick Daniszewski
    Date:   06 Dec 2016
    
    \\//
     \/apor IO
"""
import os
import hashlib
import logging
from netaddr import IPAddress, IPNetwork

from vapor_common.constants import LICENSE_PATH, LOCAL_HASH
from vapor_common.headers import VAPOR_IDENTITY_HASH

# crate will not always be available, set a flag if unavailable to more
# easily gate the usage of crate components.
try:
    from crate_api.utils.identity_utils import get_vec_with_identity
    from crate_api.utils.state_handling import has_state_file, get_state, get_vec_leader
    from crate_api.definitions.variables import VAPOR_VEC_LEADER
    crate_enabled = True
except ImportError:
    crate_enabled = False


logger = logging.getLogger()


def ip_is_local(ip):
    """ Convenience method to check if an IP address falls within the
    CIDR range that is used by Docker (default 172.17.0.0/16).

    If it does fall within that range, we consider the request to be
    made locally, and should be considered trusted. If it is not within
    the range, we will have to validate the IP off of Vec records in the
    Manifest.

    Args:
        ip (str): the IP from the response to validate

    Returns:
        bool: True, if IP is within the CIDR range; False otherwise.
    """
    try:
        # FIXME (etd) -- CIDR range should be configurable (vapor_common#54)
        return ip == '127.0.0.1' or (IPAddress(ip) in IPNetwork('172.17.0.0/16') if ip else False)
    except Exception as e:
        logger.warning('Failed check for local ip: {}'.format(e))
        return False


def validate_response(response, response_ip, cache):
    """ Validate the HTTP response's trust header, if it exists.

    This is similar to the `validate_request` method except that here, the response
    will be a requests.Response object which does not have the knowledge of 'remote
    addr' which the request flask.Request object does have the knowledge of. This
    means that while the request validation will check that the identity hash belongs
    to the incoming IP, the response validation will not.

    Args:
        response (Response): the object representing the HTTP response.
        response_ip (str): the ip associated with the responding entity.
        cache (SimpleCache): the cache used by the Flask application instance.

    Returns:
        bool: True if the response is validated as trusted; False otherwise.
    """
    if trust_enabled():
        identity_hash = response.headers.get(VAPOR_IDENTITY_HASH)
        logger.debug('RESPONSE IDENTITY HASH: {}'.format(identity_hash))

        # here, we don't need to check the response IP because we didn't get a
        # trust header, so validation would fail either way.
        if identity_hash is None:
            logger.warning('No identity hash found in response header.')
            return False

        # in this case, the header indicates it is local, so the ip should corroborate.
        # if it doesn't, we fail, otherwise the response is local and we're all good.
        if check_local_trust(cache, identity_hash) and ip_is_local(response_ip):
            logger.debug('Response trust established: local response.')
            return True

        leader = get_vec_leader()
        if not leader:
            return False

        resp = _validate_response(cache, identity_hash, response_ip, leader)
        return resp

    # if trusted mode is not enabled, everything should be considered trusted.
    else:
        return True


def validate_request(request, cache):
    """ Convenience method to wrap all identity hash validation into a simple common
    interface which can be used across all Vapor endpoints.

    This is intended to be called in a Flask application's `before_request`-decorated
    method.

    Args:
        request (Request): the incoming request object.
        cache (SimpleCache): the cache used by the Flask application instance.

    Returns:
        bool: True if the request was validated as trusted; False otherwise.
    """
    if trust_enabled():
        identity_hash = request.headers.get(VAPOR_IDENTITY_HASH)
        logger.debug('REQUEST IDENTITY HASH: {}'.format(identity_hash))

        if identity_hash is None:
            logger.warning('No identity hash found in request header.')
            return False

        # first, check if the incoming hash corresponds with local traffic,
        # e.g. if it originates from the same vec. in this case, it is trusted.
        #
        # if the incoming hash is untrusted or otherwise fails to successfully
        # validate through the local check, continue validation
        if check_local_trust(cache, identity_hash):
            logger.debug('Request trust established: local request.')
            return True

        leader = get_vec_leader()
        if not leader:
            return False

        return _validate_request(cache, request, identity_hash, leader)

    # if trusted mode is not enabled, everything should be considered trusted
    else:
        return True


def _validate_request(cache, request, identity_hash, manifest_ip='localhost'):
    """ Perform request validation.

    Args:
        cache (SimpleCache): the cache used by the Flask application instance.
        request (Request): the incoming request object.
        identity_hash (str): the identity hash associated with the incoming
            request which we are validating.
        manifest_ip (str): the ip/hostname to use for connecting to the
            Manifest, if available. (default: 'localhost')

    Returns:
        bool: True if the request is validated as trusted; False otherwise
    """
    if crate_enabled:
        vec = _get_vec(cache, identity_hash, manifest_ip)
        if vec is None:
            return False

        remote_addr = request.remote_addr
        vec_addr = vec.ip

        return remote_addr == vec_addr

    else:
        logger.warning('Crate/Manifest is not enabled - unable to run in trusted mode.')
        return False


def _validate_response(cache, identity_hash, vec_ip, manifest_ip='localhost'):
    """ Perform response validation.

    Args:
        cache (SimpleCache): the cache used by the Flask application instance.
        identity_hash (str): the identity hash associated with the response
            which we are validating.
        vec_ip (str): the ip of the responding Vec.
        manifest_ip (str): the ip/hostname to use for connecting to the
            Manifest, if available. (default: 'localhost')

    Returns:
        bool: True if the response is validated as trusted; False otherwise
    """
    if crate_enabled:
        vec = _get_vec(cache, identity_hash, manifest_ip, vec_ip=vec_ip)
        return vec is not None

    else:
        logger.warning('Crate/Manifest is not enabled - unable to run in trusted mode.')
        return False


def _get_vec(cache, identity, manifest_ip, vec_ip=None):
    """ Convenience method to get the Vec associated with the given hash, if
    any exists.

    This will first look in the cache for the Vec. If it does not exist there,
    it will attempt to lookup from the Manifest. If it is found in the Manifest,
    the cache is updated and the Vec is returned.

    If the Vec can not be found through any means, None is returned.

    Args:
        cache (SimpleCache): the cache used by the Flask application instance.
        identity (str): the identity hash associated with the request/response
            which we are validating.
        manifest_ip (str): the ip/hostname to use for connecting to the
            Manifest, if available. (default: 'localhost')
        vec_ip (str): the ip of the responding Vec. (optional)

    Returns:
        Vec: the Vec record associates with the given identity hash
        None: if no Vec record is found for the given identity hash
    """
    vec = cache.get(identity)

    if vec is None:
        try:
            vec = get_vec_with_identity(manifest_ip, identity, vec_ip=vec_ip)

        except Exception as e:
            logger.error('Unable to get Vec from Manifest: {}'.format(e))
            return False

        if vec is not None:
            cache.set(identity, vec)

    return vec


def get_local_hash():
    """ Get the hash of the local license/trust cert.

    If no local license/trust cert is found, None will be returned.

    Returns:
        str: the hash string of the license/trust cert.
        None: if no local cert exists.

    Raises:
        ValueError: Multiple certificates are defined in the license path.
    """
    # if the license path does not exist, we will not outright fail. this
    # could be the case where things are running locally for dev or demo
    # and all is not properly configured. in this case, we should return
    # as if there is no cert specified, but will log out a message for
    # external visibility.
    if not os.path.isdir(LICENSE_PATH):
        logger.warning('License path does not exist - will assume no certs are configured.')
        return None

    # otherwise, the path does exist. we will want to look for the cert that
    # is defined in the directory. since the cert name does not matter, we
    # only look that it ends with .crt
    crt_files = os.listdir(LICENSE_PATH)
    certs = [f for f in crt_files if f.endswith('.crt')]

    _count = len(certs)
    if _count > 1:
        raise ValueError(
            'Multiple certificates defined in the license path, but only a single '
            'certificate (or no certificate) was expected -- ({})'.format(certs)
        )

    elif _count == 0:
        # No certs specified -- return None to inform upstream that we are
        # running in "untrusted" mode.
        return None

    else:
        cert = certs[0]

    try:
        # hash the contents of the cert -- this value will act as the Vec's
        # unique system-wide ID.
        # TODO - validate that the cert is still valid
        with open(os.path.join(LICENSE_PATH, cert), 'r') as f:
            hash = hashlib.sha256(f.read())

        digest = hash.hexdigest()

    except (OSError, IOError) as e:
        logger.error('{}: Unable to hash certificate -- {}'.format(e.__name__, e.message))
        logger.exception(e)
        raise

    except Exception as e:
        logger.error('Unexpected Exception when hashing identity certificate: {}'.format(e))
        raise

    return digest


def check_local_trust(cache, identity_hash):
    """ Check whether the incoming identity hash can be trusted by virtue of it
    being a local (intra-VEC) request.

    Args:
        cache (SimpleCache): Flask application cache which is used for quick
            lookup of trust hashes.
        identity_hash (str): the incoming identity hash to validate.

    Returns:
        bool: True if trust is validated because of local origin; False otherwise.
    """
    # here, LOCAL_HASH is a special key which should map to the hash of the local Vec
    local_hash = cache.get(LOCAL_HASH)

    if not local_hash:
        try:
            local_hash = get_local_hash()
        except Exception as e:
            logger.warning('Unable to determine local hash. Skipping local check ({})'.format(e))
            return False

        if local_hash is None:
            logger.info('Unable to find valid local hash - assuming "untrusted" mode.')
            return False

        # add the newly found value for local_hash to the cache
        cache.set('local_hash', local_hash)

    return local_hash == identity_hash


def trust_enabled():
    """ Check if the container is running in trusted mode.

    Returns:
        bool: True if trusted mode is enabled; False otherwise
    """
    # TODO - this would be good to cache one way or another since os operations
    # tend to be slow, and this result really shouldn't be changing all that frequently.
    try:
        if os.path.isdir(LICENSE_PATH):
            return len([f for f in os.listdir(LICENSE_PATH) if f.endswith('.crt')]) == 1
    except Exception as e:
        logger.debug('Exception when checking if trust is enabled: {}'.format(e))
        pass
    return False
