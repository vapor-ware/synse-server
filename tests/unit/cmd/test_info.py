
import pytest
from synse_grpc import api

from synse_server import errors
from synse_server.cmd import info


@pytest.mark.asyncio
async def test_info_device_not_found(monkeypatch):
    async def patched(device_id):
        return None
    monkeypatch.setattr(info.cache, 'get_device', patched)

    with pytest.raises(errors.NotFound):
        await info.info('123')


@pytest.mark.asyncio
async def test_info_device_found(monkeypatch):
    async def patched(device_id):
        return api.V3Device(
            id='123',
            info='foo',
            metadata={'a': 'b'},
            plugin='xyz',
            type='test',
            tags=[
                api.V3Tag(
                    namespace='default',
                    annotation='foo',
                    label='bar',
                ),
                api.V3Tag(
                    namespace='default',
                    label='test',
                ),
                api.V3Tag(
                    label='example',
                ),
            ]
        )

    monkeypatch.setattr(info.cache, 'get_device', patched)

    resp = await info.info('123')
    assert resp == {
        'id': '123',
        'type': 'test',
        'info': 'foo',
        'metadata': {
            'a': 'b',
        },
        'plugin': 'xyz',
        'tags': [
            'default/foo:bar',
            'default/test',
            'example',
        ],
        'outputs': [],
        'sort_index': 0,
        'timestamp': '',
    }
