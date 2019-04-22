
import pytest

from synse_server.cmd import test


@pytest.mark.asyncio
async def test_test(patch_utils_rfc3339now):

    response = await test.test()

    assert response == {
        'status': 'ok',
        'timestamp': '2019-04-19T02:01:53Z',  # hardcoded in conftest fixture
    }
