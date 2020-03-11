"""Unit tests for the ``synse_server.cmd.info`` module."""

import asynctest
import pytest
from synse_grpc import api

from synse_server import cmd, errors


@pytest.mark.asyncio
async def test_info_device_not_found():
    with asynctest.patch('synse_server.cache.get_device') as mock_get:
        mock_get.return_value = None

        with pytest.raises(errors.NotFound):
            await cmd.info('123')

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')


@pytest.mark.asyncio
async def test_info_device_found():
    with asynctest.patch('synse_server.cache.get_device') as mock_get:
        mock_get.return_value = api.V3Device(
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

        resp = await cmd.info('123')
        assert resp == {
            'id': '123',
            'alias': '',
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

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')
