
import pytest
import ujson

from sanic.response import HTTPResponse
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
