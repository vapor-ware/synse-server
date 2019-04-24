
import asynctest
import pytest
from synse_grpc import client

from synse_server import errors, plugin
from synse_server import cmd
from synse_server.cmd.read import reading_to_dict


@pytest.mark.asyncio
async def test_read_no_plugins(mocker):
    # Mock test data
    mocker.patch.dict('synse_server.plugin.PluginManager.plugins', {})

    mock_read = mocker.patch(
        'synse_grpc.client.PluginClientV3.read',
    )

    # --- Test case -----------------------------
    resp = await cmd.read('default', ['default/foo'])
    assert len(resp) == 0

    mock_read.assert_not_called()


@pytest.mark.asyncio
async def test_read_fails_read(mocker, simple_plugin):
    # Mock test data
    mocker.patch.dict('synse_server.plugin.PluginManager.plugins', {
        '123': simple_plugin,
    })

    mock_read = mocker.patch(
        'synse_grpc.client.PluginClientV3.read',
        side_effect=ValueError(),
    )

    # --- Test case -----------------------------
    # Set the simple_plugin to active to start.
    simple_plugin.active = True

    with pytest.raises(errors.ServerError):
        await cmd.read('default', ['default/foo'])

    assert simple_plugin.active is False

    mock_read.assert_called_once()
    mock_read.assert_called_with(tags=['default/foo'])


@pytest.mark.asyncio
async def test_read_fails_read_multiple_one_fail(mocker, simple_plugin, temperature_reading):
    # Mock test data
    error_plugin = plugin.Plugin(
        client=client.PluginClientV3('localhost:5433', 'tcp'),
        info={
            'tag': 'test/bar',
            'id': '456',
            'vcs': 'https://github.com/vapor-ware/synse-server',
        },
        version={},
    )

    mocker.patch.dict('synse_server.plugin.PluginManager.plugins', {
        '123': simple_plugin,
        '456': error_plugin,
    })

    mock_read_ok = mocker.MagicMock(
        return_value=[
            temperature_reading,
        ],
    )
    mock_read_error = mocker.MagicMock(
        side_effect=ValueError(),
    )

    simple_plugin.client.read = mock_read_ok
    error_plugin.client.read = mock_read_error

    # --- Test case -----------------------------
    # Set the plugins to active to start.
    simple_plugin.active = True
    error_plugin.active = True

    with pytest.raises(errors.ServerError):
        await cmd.read('default', ['default/foo'])

    assert simple_plugin.active is True
    assert error_plugin.active is False

    mock_read_error.assert_called_once()
    mock_read_error.assert_called_with(tags=['default/foo'])
    # NOTE: can't check read_ok since dicts are unordered, we can't
    # ensure that it was actually called prior to the error read


@pytest.mark.asyncio
async def test_read_ok_no_tags(mocker, simple_plugin, temperature_reading, humidity_reading):
    # Mock test data
    mocker.patch.dict('synse_server.plugin.PluginManager.plugins', {
        '123': simple_plugin,
    })

    mock_read = mocker.patch(
        'synse_grpc.client.PluginClientV3.read',
        return_value=[
            temperature_reading,
            humidity_reading,
        ],
    )

    # --- Test case -----------------------------
    # Set the simple_plugin to active to start.
    simple_plugin.active = True

    resp = await cmd.read('default', [])
    assert resp == [
        {  # from temperature_reading fixture
            'device': 'aaa',
            'timestamp': '2019-04-22T13:30:00Z',
            'type': 'temperature',
            'device_type': 'temperature',
            'unit': {
                'name': 'celsius',
                'symbol': 'C',
            },
            'value': 30,
            'context': {
                'zone': '1',
            },
        },
        {  # from humidity_reading fixture
            'device': 'bbb',
            'timestamp': '2019-04-22T13:30:00Z',
            'type': 'humidity',
            'device_type': 'humidity',
            'unit': {
                'name': 'percent',
                'symbol': '%',
            },
            'value': 42.0,
            'context': {},
        },
    ]

    assert simple_plugin.active is True

    mock_read.assert_called_once()
    mock_read.assert_called_with(tags=[])


@pytest.mark.asyncio
async def test_read_ok_tags_with_ns(mocker, simple_plugin, state_reading):
    # Mock test data
    mocker.patch.dict('synse_server.plugin.PluginManager.plugins', {
        '123': simple_plugin,
        '456': simple_plugin,
    })

    mock_read = mocker.patch(
        'synse_grpc.client.PluginClientV3.read',
        return_value=[
            state_reading,
        ],
    )

    # --- Test case -----------------------------
    # Set the simple_plugin to active to start.
    simple_plugin.active = True

    resp = await cmd.read('default', ['foo/bar', 'vapor/ware'])
    assert resp == [
        {  # from state_reading fixture
            'device': 'ccc',
            'timestamp': '2019-04-22T13:30:00Z',
            'type': 'state',
            'device_type': 'led',
            'value': 'on',
            'unit': None,
            'context': {},
        },
        {  # from state_reading fixture
            'device': 'ccc',
            'timestamp': '2019-04-22T13:30:00Z',
            'type': 'state',
            'device_type': 'led',
            'value': 'on',
            'unit': None,
            'context': {},
        },
    ]

    assert simple_plugin.active is True

    mock_read.assert_called()
    mock_read.assert_has_calls([
        mocker.call(tags=['foo/bar', 'vapor/ware']),
        mocker.call(tags=['foo/bar', 'vapor/ware']),
    ])


@pytest.mark.asyncio
async def test_read_ok_tags_without_ns(mocker, simple_plugin, state_reading):
    # Mock test data
    mocker.patch.dict('synse_server.plugin.PluginManager.plugins', {
        '123': simple_plugin,
        '456': simple_plugin,
    })

    mock_read = mocker.patch(
        'synse_grpc.client.PluginClientV3.read',
        return_value=[
            state_reading,
        ],
    )

    # --- Test case -----------------------------
    # Set the simple_plugin to active to start.
    simple_plugin.active = True

    resp = await cmd.read('default', ['foo', 'bar', 'vapor/ware'])
    assert resp == [
        {  # from state_reading fixture
            'device': 'ccc',
            'timestamp': '2019-04-22T13:30:00Z',
            'type': 'state',
            'device_type': 'led',
            'value': 'on',
            'unit': None,
            'context': {},
        },
        {  # from state_reading fixture
            'device': 'ccc',
            'timestamp': '2019-04-22T13:30:00Z',
            'type': 'state',
            'device_type': 'led',
            'value': 'on',
            'unit': None,
            'context': {},
        },
    ]

    assert simple_plugin.active is True

    mock_read.assert_called()
    mock_read.assert_has_calls([
        mocker.call(tags=['default/foo', 'default/bar', 'vapor/ware']),
        mocker.call(tags=['default/foo', 'default/bar', 'vapor/ware']),
    ])


@pytest.mark.asyncio
async def test_read_device_not_found():
    with asynctest.patch('synse_server.cache.get_plugin') as mock_get:
        mock_get.return_value = None

        with pytest.raises(errors.NotFound):
            await cmd.read_device('123')

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')


@pytest.mark.asyncio
async def test_read_device_error_getting_plugin():
    with asynctest.patch('synse_server.cache.get_plugin') as mock_get:
        mock_get.side_effect = ValueError()

        with pytest.raises(ValueError):
            await cmd.read_device('123')

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')


@pytest.mark.asyncio
async def test_read_device_fails_read(mocker, simple_plugin):
    # Mock test data
    mock_read = mocker.patch(
        'synse_grpc.client.PluginClientV3.read',
        side_effect=ValueError(),
    )

    # --- Test case -----------------------------
    with asynctest.patch('synse_server.cache.get_plugin') as mock_get:
        mock_get.return_value = simple_plugin

        with pytest.raises(errors.ServerError):
            await cmd.read_device('123')

    assert simple_plugin.active is False

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')
    mock_read.assert_called_once()
    mock_read.assert_called_with(device_id='123')


@pytest.mark.asyncio
async def test_read_device_ok(mocker, simple_plugin, temperature_reading):
    # Mock test data
    mock_read = mocker.patch(
        'synse_grpc.client.PluginClientV3.read',
        return_value=[
            temperature_reading,
        ],
    )

    # --- Test case -----------------------------
    with asynctest.patch('synse_server.cache.get_plugin') as mock_get:
        mock_get.return_value = simple_plugin

        resp = await cmd.read_device('123')
        assert resp == [
            {  # from temperature_reading fixture
                'device': 'aaa',
                'timestamp': '2019-04-22T13:30:00Z',
                'type': 'temperature',
                'device_type': 'temperature',
                'unit': {
                    'name': 'celsius',
                    'symbol': 'C',
                },
                'value': 30,
                'context': {
                    'zone': '1',
                },
            },
        ]

    assert simple_plugin.active is True

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')
    mock_read.assert_called_once()
    mock_read.assert_called_with(device_id='123')


@pytest.mark.asyncio
async def test_read_cache_no_plugins(mocker):
    # Mock test data
    mocker.patch.dict('synse_server.plugin.PluginManager.plugins', {})

    mock_read = mocker.patch(
        'synse_grpc.client.PluginClientV3.read_cache',
    )

    # --- Test case -----------------------------
    res = [r async for r in cmd.read_cache()]
    assert len(res) == 0

    mock_read.assert_not_called()


@pytest.mark.asyncio
async def test_read_cache_fails_read_cache(mocker, simple_plugin):
    # Mock test data
    mocker.patch.dict('synse_server.plugin.PluginManager.plugins', {
        '123': simple_plugin,
    })

    mock_read = mocker.patch(
        'synse_grpc.client.PluginClientV3.read_cache',
        side_effect=ValueError(),
    )

    # --- Test case -----------------------------
    with pytest.raises(errors.ServerError):
        _ = [r async for r in cmd.read_cache()]

    assert simple_plugin.active is False

    mock_read.assert_called_once()
    mock_read.assert_called_with(start=None, end=None)


@pytest.mark.asyncio
async def test_read_cache_ok(mocker, simple_plugin, humidity_reading):
    # Mock test data
    mocker.patch.dict('synse_server.plugin.PluginManager.plugins', {
        '123': simple_plugin,
    })

    def patchreadcache(*args, **kwargs):
        data = [
            humidity_reading,
            humidity_reading,
            humidity_reading,
        ]

        for d in data:
            yield d

    mock_read = mocker.patch(
        'synse_grpc.client.PluginClientV3.read_cache',
        side_effect=patchreadcache,
    )

    # --- Test case -----------------------------
    resp = [r async for r in cmd.read_cache('2019-04-22T13:30:00Z', '2019-04-22T13:35:00Z')]
    assert len(resp) == 3
    for reading in resp:
        assert reading == {
            # from humidity_reading fixture
            'device': 'bbb',
            'timestamp': '2019-04-22T13:30:00Z',
            'type': 'humidity',
            'device_type': 'humidity',
            'unit': {
                'name': 'percent',
                'symbol': '%',
            },
            'value': 42.0,
            'context': {},
        }

    assert simple_plugin.active is True

    mock_read.assert_called_once()
    mock_read.assert_called_with(start='2019-04-22T13:30:00Z', end='2019-04-22T13:35:00Z')


def test_reading_to_dict_1(temperature_reading):
    actual = reading_to_dict(temperature_reading)
    assert actual == {
        # from temperature_reading fixture
        'device': 'aaa',
        'timestamp': '2019-04-22T13:30:00Z',
        'type': 'temperature',
        'device_type': 'temperature',
        'unit': {
            'name': 'celsius',
            'symbol': 'C',
        },
        'value': 30,
        'context': {
            'zone': '1',
        },
    }


def test_reading_to_dict_2(humidity_reading):
    actual = reading_to_dict(humidity_reading)
    assert actual == {
        # from humidity_reading fixture
        'device': 'bbb',
        'timestamp': '2019-04-22T13:30:00Z',
        'type': 'humidity',
        'device_type': 'humidity',
        'unit': {
            'name': 'percent',
            'symbol': '%',
        },
        'value': 42.0,
        'context': {},
    }


def test_reading_to_dict_3(state_reading):
    actual = reading_to_dict(state_reading)
    assert actual == {
        # from state_reading fixture
        'device': 'ccc',
        'timestamp': '2019-04-22T13:30:00Z',
        'type': 'state',
        'device_type': 'led',
        'value': 'on',
        'unit': None,
        'context': {},
    }
