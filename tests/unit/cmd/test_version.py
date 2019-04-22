
import pytest

import synse_server
from synse_server.cmd import version


@pytest.mark.asyncio
async def test_version():

    response = await version.version()

    assert response == {
        'version': synse_server.__version__,
        'api_version': synse_server.__api_version__,
    }
