"""Unit tests for the ``synse_server.utils`` module."""

import mock
import pytest
from sanic.response import HTTPResponse

from synse_server import utils


@pytest.mark.parametrize(
    'data,expected',
    [
        ({}, {},),
        ({'foo': 'bar'}, {'foo': 'bar'},),
        ({'context': {'data': 'abc'}}, {'context': {'data': 'abc'}},),
        ({'context': {'data': b'abc'}}, {'context': {'data': 'abc'}},),
        ({'context': {'transaction': None}}, {'context': {}},),
        ({'context': {'transaction': ''}}, {'context': {}},),
        ({'context': {'transaction': '123'}}, {'context': {'transaction': '123'}},),
        (
            {'context': {'data': b'10', 'transaction': '', 'action': 'a'}},
            {'context': {'data': '10', 'action': 'a'}},
        ),
    ],
)
def test_normalize_write_ctx(data, expected):
    utils.normalize_write_ctx(data)
    assert data == expected


@pytest.mark.usefixtures('patch_datetime_utcnow')
def test_rfc3339now():
    actual = utils.rfc3339now()
    assert actual == '2019-04-19T02:01:53Z'


@pytest.mark.parametrize(
    'data,expected',
    [
        ({'foo': 'bar'}, '{"foo":"bar"}\n'),
        ({'one': 1}, '{"one":1}\n'),
        ({'foo': 'bar', 'one': 1}, '{"foo":"bar","one":1}\n'),
        ({'foo': 'bar', 'one': {'two': 2}}, '{"foo":"bar","one":{"two":2}}\n'),
        ({'foo': 'bar', 'one': [1, 2, 3]}, '{"foo":"bar","one":[1,2,3]}\n'),
        ([1, 2, 3], '[1,2,3]\n'),
        ([1, 2, [2, 3, 4]], '[1,2,[2,3,4]]\n'),
        ([{'one': 1}, {'two': 2}], '[{"one":1},{"two":2}]\n'),
    ],
)
def test_dumps(data, expected):
    actual = utils._dumps(data)
    assert actual == expected


def test_http_json_response_from_dict():
    actual = utils.http_json_response({'status': 'ok'})

    assert isinstance(actual, HTTPResponse)
    assert actual.body == b'{"status":"ok"}'
    assert actual.status == 200
    assert actual.content_type == 'application/json'


def test_http_json_response_from_list():
    actual = utils.http_json_response([1, 2, 3])

    assert isinstance(actual, HTTPResponse)
    assert actual.body == b'[1,2,3]'
    assert actual.status == 200
    assert actual.content_type == 'application/json'


@mock.patch('synse_server.config.options.get', return_value=True)
def test_http_json_response_from_dict_pretty(mock_get):
    actual = utils.http_json_response({'status': 'ok'})

    assert isinstance(actual, HTTPResponse)
    assert actual.body == b'{\n  "status": "ok"\n}\n'
    assert actual.status == 200
    assert actual.content_type == 'application/json'

    mock_get.assert_called_with('pretty_json')


@mock.patch('synse_server.config.options.get', return_value=True)
def test_http_json_response_from_list_pretty(mock_get):
    actual = utils.http_json_response(['a', 'b', 'c'])

    assert isinstance(actual, HTTPResponse)
    assert actual.body == b'[\n  "a",\n  "b",\n  "c"\n]\n'
    assert actual.status == 200
    assert actual.content_type == 'application/json'

    mock_get.assert_called_with('pretty_json')
