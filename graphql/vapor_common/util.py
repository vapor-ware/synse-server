#!/usr/bin/env python
""" Common utilities for all Vapor components.

    Author: Erick Daniszewski
    Date:   05/17/2016
    
    \\//
     \/apor IO
"""
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from flask import jsonify


def setup_json_errors(app):
    """ Setup JSON error responses for the given Flask application.

    Args:
        app (Flask): A Flask application instance.
    """
    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = _make_json_error


def _make_json_error(ex):
    """ Crate a JSON response for an exception raised in the endpoint.

    Args:
        ex (Exception): The exception raised.

    Returns:
        Response: a Flask response with the proper json error message and
            status code.
    """
    if isinstance(ex, HTTPException):
        message = ex.description
        http_code = ex.code
    else:
        message = ex.message
        http_code = 500

    response = jsonify(
        message=str(message),
        http_code=http_code
    )
    response.status_code = http_code

    return response
