
import pytest

from synse_server import cmd


@pytest.mark.asyncio
@pytest.mark.usefixtures('patch_utils_rfc3339now')
async def test_test():

    response = await cmd.test()

    assert response == {
        'status': 'ok',
        'timestamp': '2019-04-22T13:30:00Z',  # hardcoded in conftest fixture
    }
