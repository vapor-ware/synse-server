
import pytest

from synse_server.cmd import config

from .. import mocks


@pytest.mark.asyncio
async def test_config_no_items(monkeypatch):
    mock_config = mocks.OptionsMock({})
    monkeypatch.setattr(config, 'options', mock_config)

    resp = await config.config()

    assert resp == {}


@pytest.mark.asyncio
async def test_config_reserved_items(monkeypatch):
    mock_config = mocks.OptionsMock({
        '_a': 1,
        '_b': 2,
        '_c': 3,
    })
    monkeypatch.setattr(config, 'options', mock_config)

    resp = await config.config()

    assert resp == {}


@pytest.mark.asyncio
async def test_config_with_items(monkeypatch):
    mock_config = mocks.OptionsMock({
        'a': 1,
        'b': 2,
        'c': 3,
    })
    monkeypatch.setattr(config, 'options', mock_config)

    resp = await config.config()

    assert resp == {
        'a': 1,
        'b': 2,
        'c': 3,
    }
