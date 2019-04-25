
import asynctest
import pytest
import ujson
from sanic.response import HTTPResponse

import synse_server
from synse_server.api import http


@pytest.mark.asyncio
async def test_core_test(mocker, make_request):
    # Mock test data
    mocker.patch(
        'synse_server.utils.rfc3339now',
        return_value='2019-04-22T13:30:00Z',
    )

    # --- Test case -----------------------------
    req = make_request('/test')

    resp = await http.test(req)

    assert isinstance(resp, HTTPResponse)
    assert resp.status == 200

    body = ujson.loads(resp.body)
    assert body == {
        'status': 'ok',
        'timestamp': '2019-04-22T13:30:00Z',
    }


@pytest.mark.asyncio
async def test_core_version(make_request):
    req = make_request('/version')

    resp = await http.version(req)

    assert isinstance(resp, HTTPResponse)
    assert resp.status == 200

    body = ujson.loads(resp.body)
    assert body == {
        'version': synse_server.__version__,
        'api_version': synse_server.__api_version__,
    }


@pytest.mark.asyncio
async def test_v3_config(mocker, make_request):
    # Mock test data
    mocker.patch.dict(
        'synse_server.config.options._full_config', {
            'logging': 'debug',
            'plugins': {
                'tcp': [
                    'localhost:5001'
                ],
            }
        }
    )

    # --- Test case -----------------------------
    req = make_request('/v3/config')

    resp = await http.config(req)

    assert isinstance(resp, HTTPResponse)
    assert resp.status == 200

    body = ujson.loads(resp.body)
    assert body == {
        'logging': 'debug',
        'plugins': {
            'tcp': [
                'localhost:5001'
            ],
        }
    }


@pytest.mark.asyncio
async def test_v3_plugins(make_request):
    with asynctest.patch('synse_server.cmd.plugins') as mock_plugins:
        mock_plugins.return_value = [
            {
                "description": "a plugin with emulated devices and data",
                "id": "12835beffd3e6c603aa4dd92127707b5",
                "name": "emulator plugin",
                "maintainer": "vapor io",
                "active": True
            },
            {
                "description": "a custom third party plugin",
                "id": "12835beffd3e6c603aa4dd92127707b6",
                "name": "custom-plugin",
                "maintainer": "third-party",
                "active": True
            },
        ]

        req = make_request('/v3/plugins')
        resp = await http.plugins(req)

        assert isinstance(resp, HTTPResponse)
        assert resp.status == 200

        body = ujson.loads(resp.body)
        assert body == mock_plugins.return_value
