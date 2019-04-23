
import pytest

from synse_server.cmd import plugin


@pytest.mark.asyncio
async def test_plugin_not_found():
    pass


@pytest.mark.asyncio
async def test_plugin_client_error():
    pass


@pytest.mark.asyncio
async def test_plugin_ok():
    pass


@pytest.mark.asyncio
async def test_plugin_ok_refresh():
    pass


@pytest.mark.asyncio
async def test_plugins_no_plugin():
    pass


@pytest.mark.asyncio
async def test_plugins_ok():
    pass


@pytest.mark.asyncio
async def test_plugins_ok_refresh():
    pass


@pytest.mark.asyncio
async def test_plugin_health_no_plugins():
    pass


@pytest.mark.asyncio
async def test_plugin_health_healthy():
    pass


@pytest.mark.asyncio
async def test_plugin_health_unhealthy():
    pass


@pytest.mark.asyncio
async def test_plugin_health_ok():
    pass


@pytest.mark.asyncio
async def test_plugin_health_ok_refresh():
    pass
