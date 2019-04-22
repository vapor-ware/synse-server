
from sanic.response import HTTPResponse
from sanic.request import Request
import pytest
import json
from unittest import mock

from synse_server import errors


class TestSynseErrorHandler:
    """Test cases for the ``synse_server.errors.SynseErrorHandler`` class."""

    @pytest.mark.parametrize(
        'exception,code', [
            (errors.SynseError, 500),
            (errors.InvalidUsage, 400),
            (errors.NotFound, 404),
            (errors.UnsupportedAction, 405),
            (errors.ServerError, 500),
        ]
    )
    def test_default_synse_error(self, exception, code):
        handler = errors.SynseErrorHandler()

        actual = handler.default(None, exception('test'))

        assert isinstance(actual, HTTPResponse)
        assert actual.status == code

        data = json.loads(actual.body)
        assert data['description'] == exception.description
        assert data['context'] == 'test'
        assert data['http_code'] == code
        assert 'timestamp' in data

    def test_default_not_a_synse_error(self):
        handler = errors.SynseErrorHandler()

        exception = ValueError('foobar')
        request = Request(b'http://localhost', {}, None, 'GET', None)

        actual = handler.default(request, exception)

        assert isinstance(actual, HTTPResponse)
        assert actual.status == 500
        assert b'<h1>Internal Server Error</h1>' in actual.body


class TestSynseError:
    """Test cases for the ``synse_server.errors.SynseError`` Exception."""

    @mock.patch('synse_server.errors.rfc3339now', return_value='2019-04-22T13:30:00Z')
    def test_make_response(self, patched_rfc3339now):
        ex = errors.SynseError('context error message')
        resp = ex.make_response()

        assert isinstance(resp, dict)
        assert resp == {
            'http_code': 500,
            'description': 'an unexpected error occurred',
            'timestamp': '2019-04-22T13:30:00Z',
            'context': 'context error message',
        }

        patched_rfc3339now.assert_called_once()


class TestInvalidUsage:
    """Test cases for the ``synse_server.errors.InvalidUsage`` Exception."""

    @mock.patch('synse_server.errors.rfc3339now', return_value='2019-04-22T13:30:00Z')
    def test_make_response(self, patched_rfc3339now):
        ex = errors.InvalidUsage('context error message')
        resp = ex.make_response()

        assert isinstance(resp, dict)
        assert resp == {
            'http_code': 400,
            'description': 'invalid user input',
            'timestamp': '2019-04-22T13:30:00Z',
            'context': 'context error message',
        }

        patched_rfc3339now.assert_called_once()


class TestNotFound:
    """Test cases for the ``synse_server.errors.NotFound`` Exception."""

    @mock.patch('synse_server.errors.rfc3339now', return_value='2019-04-22T13:30:00Z')
    def test_make_response(self, patched_rfc3339now):
        ex = errors.NotFound('context error message')
        resp = ex.make_response()

        assert isinstance(resp, dict)
        assert resp == {
            'http_code': 404,
            'description': 'resource not found',
            'timestamp': '2019-04-22T13:30:00Z',
            'context': 'context error message',
        }

        patched_rfc3339now.assert_called_once()


class TestUnsupportedAction:
    """Test cases for the ``synse_server.errors.UnsupportedAction`` Exception."""

    @mock.patch('synse_server.errors.rfc3339now', return_value='2019-04-22T13:30:00Z')
    def test_make_response(self, patched_rfc3339now):
        ex = errors.UnsupportedAction('context error message')
        resp = ex.make_response()

        assert isinstance(resp, dict)
        assert resp == {
            'http_code': 405,
            'description': 'device action not supported',
            'timestamp': '2019-04-22T13:30:00Z',
            'context': 'context error message',
        }

        patched_rfc3339now.assert_called_once()


class TestServerError:
    """Test cases for the ``synse_server.errors.ServerError`` Exception."""

    @mock.patch('synse_server.errors.rfc3339now', return_value='2019-04-22T13:30:00Z')
    def test_make_response(self, patched_rfc3339now):
        ex = errors.ServerError('context error message')
        resp = ex.make_response()

        assert isinstance(resp, dict)
        assert resp == {
            'http_code': 500,
            'description': 'error processing the request',
            'timestamp': '2019-04-22T13:30:00Z',
            'context': 'context error message',
        }

        patched_rfc3339now.assert_called_once()
