#!/usr/bin/env python
""" Common utilities for all Vapor components.

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

from flask import jsonify
from werkzeug.exceptions import HTTPException, default_exceptions


def setup_json_errors(app):
    """ Setup JSON error responses for the given Flask application.

    Args:
        app (flask.Flask): A Flask application instance.
    """
    for code in default_exceptions.iterkeys():
        app.register_error_handler(code, _make_json_error)


def _make_json_error(ex):
    """ Create a JSON response for an exception raised in the endpoint.

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
