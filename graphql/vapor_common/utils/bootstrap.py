#!/usr/bin/env python
""" Common utilities for container bootstrapping.

    Author: Erick Daniszewski
    Date:   08/26/2016

    \\//
     \/apor IO
"""
import os
import time
from functools import wraps

from vapor_common.variables import VAPOR_EXEC_MODE, VAPOR_BOOTSTRAP_BLOCK


def bootstrap_retry(f):
    """ Method used to decorate bootstrap methods in order to provide them
    with retry capabilities.
    """
    @wraps(f)
    def retry_wrap(*args, **kwargs):
        timeout, delay, retry = get_bootstrap_block_state()

        if retry is None:
            retry = True

        # in the case where 'retry' is an int/float, it will decrement to 0
        # which will then serve as the breaking condition. in the case where
        # 'retry' is None, we set it to True so that it never breaks until the
        # wrapped function completes successfully.
        while retry:
            try:
                return f(*args, **kwargs)
            except:
                if isinstance(retry, (int, float)):
                    retry -= 1
                    if retry == 0:
                        raise
            time.sleep(delay)
    return retry_wrap


def has_execution_mode(mode):
    """ Check if the container is running under the specified execution mode.

    Args:
        mode (str): the name of the execution mode to check for.

    Returns:
        bool: True, if the container's execution mode matches the provided mode
            string; False otherwise.
    """
    env_mode = os.getenv(VAPOR_EXEC_MODE)
    if env_mode is None:
        return False
    return env_mode.lower() == mode.lower()


def execution_mode(mode, cache={}):
    """ Method used to decorate other methods. With this, a mode string is specified
    which forces the decorated method to run only when the specified mode is the
    same as the container's execution mode.
    """
    def _execution_mode(fn):
        fn_name = fn.__name__
        if fn_name not in cache:
            cache[fn_name] = fn

        @wraps(fn)
        def wrapper(*args, **kwargs):
            cached_fn = cache[fn_name]
            f = cached_fn if cached_fn != fn else fn

            env_mode = os.getenv(VAPOR_EXEC_MODE)
            if env_mode is None:
                # here we want to raise an exception since in the cases where this
                # is used, there should always be a value in the env variable.
                raise ValueError('{} variable is empty but a value is expected.'.format(VAPOR_EXEC_MODE))

            # only execute the decorated method if the specified execution modes match.
            if env_mode == mode:
                return f(*args, **kwargs)
        return wrapper
    return _execution_mode


def get_bootstrap_block_state():
    """ Get the block state for container bootstrap as determined by the
    VAPOR_BOOTSTRAP_BLOCK environment variable.

    Returns:
        tuple: a 3-tuple of the timeout value, delay value, and retry
            value for container bootstrap operations.
    """
    block_state = os.getenv(VAPOR_BOOTSTRAP_BLOCK, 'block')

    # since env variable values will be strings, we want to attempt to cast
    # it to the correct type. first we try to cast it to a numeric. if that
    # fails, we will attempt to cast to boolean values
    try:
        block_state = float(block_state)
    except:
        _block_state = block_state.lower()

        if _block_state in ['true', 'false']:
            block_state = _block_state == 'true'

        elif _block_state in ['none', 'null']:
            block_state = None

    # if block_state is None, False, or 0, allow only one try at bootstrap
    # and then move on.
    if not block_state:
        timeout, delay, retry = 1, 2, 1

    # if the block_state is specified as an a float, we take that to mean
    # the number of seconds we will permit each bootstrap step to wait
    # before moving on (if its data is not available)
    elif isinstance(block_state, float) and block_state > 0:
        timeout, delay, retry = abs(block_state), 2, max(abs(block_state) // 2, 1)

    # otherwise, we apply the default blocking behavior
    else:
        timeout, delay, retry = None, 2, None

    return timeout, delay, retry


def bootstrap_is_blocking():
    """ Convenience method to check whether the container's state for bootstrap
    blocking is set or not.

    Returns:
        bool: True if the container is set to block on bootstrap; False otherwise
    """
    # if the timeout / retry are anything other than None, we know that the
    # bootstrap is set to be not blocking or to only block for a period of
    # time. in either of those cases, we do not consider it blocking
    timeout, delay, retry = get_bootstrap_block_state()
    if timeout is None and retry is None:
        return True
    return False
