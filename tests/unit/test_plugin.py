
from collections.abc import Iterable

import pytest
from grpc import RpcError
from synse_grpc import client, errors
from synse_grpc.api import V3Metadata, V3Version

from synse_server import plugin


@pytest.mark.usefixtures('clear_manager_plugins')
class TestPluginManager:
    """Test cases for the ``synse_server.plugin.PluginManager`` class."""

    def test_iterate_no_plugins(self):
        m = plugin.PluginManager()

        assert isinstance(m, Iterable)
        assert 0 == len(list(m))

    def test_iterate_has_plugins(self):
        m = plugin.PluginManager()
        m.plugins = {
            '1': 'placeholder',
            '2': 'placeholder',
            '3': 'placeholder',
            '4': 'placeholder',
        }

        assert isinstance(m, Iterable)
        assert 4 == len(list(m))

        # Ensure we iterate over the plugin dict values.
        for item in m:
            assert item == 'placeholder'

    def test_has_no_plugins(self):
        m = plugin.PluginManager()

        assert m.has_plugins() is False

    def test_has_plugins_one(self):
        m = plugin.PluginManager()
        m.plugins = {
            '1': 'placeholder',
        }

        assert m.has_plugins() is True

    def test_has_plugins_multiple(self):
        m = plugin.PluginManager()
        m.plugins = {
            '1': 'placeholder',
            '2': 'placeholder',
            '3': 'placeholder',
        }

        assert m.has_plugins() is True

    def test_get_plugin_not_found(self):
        m = plugin.PluginManager()

        result = m.get('1')
        assert result is None

    def test_get_plugin_found(self):
        m = plugin.PluginManager()
        m.plugins = {
            '1': 'placeholder',
        }

        result = m.get('1')
        assert result is not None
        assert result == 'placeholder'

    def test_register_fail_metadata_call(self, mocker):
        # Mock test data
        mock_metadata = mocker.patch(
            'synse_server.plugin.client.PluginClientV3.metadata',
            side_effect=RpcError(),
        )

        # --- Test case -----------------------------
        m = plugin.PluginManager()

        with pytest.raises(RpcError):
            m.register('localhost:5432', 'tcp')

        # Ensure nothing was added to the manager.
        assert len(m.plugins) == 0

        mock_metadata.assert_called_once()

    def test_register_fail_version_call(self, mocker):
        # Mock test data
        mock_metadata = mocker.patch(
            'synse_server.plugin.client.PluginClientV3.metadata',
            return_value=V3Metadata(),
        )
        mock_version = mocker.patch(
            'synse_server.plugin.client.PluginClientV3.version',
            side_effect=RpcError(),
        )

        # --- Test case -----------------------------
        m = plugin.PluginManager()

        with pytest.raises(RpcError):
            m.register('localhost:5432', 'tcp')

        # Ensure nothing was added to the manager.
        assert len(m.plugins) == 0

        mock_metadata.assert_called_once()
        mock_version.assert_called_once()

    def test_register_fail_plugin_init(self, mocker):
        # Mock test data
        mock_metadata = mocker.patch(
            'synse_server.plugin.client.PluginClientV3.metadata',
            return_value=V3Metadata(),
        )
        mock_version = mocker.patch(
            'synse_server.plugin.client.PluginClientV3.version',
            return_value=V3Version(),
        )

        # --- Test case -----------------------------
        m = plugin.PluginManager()

        with pytest.raises(ValueError):
            m.register('localhost:5432', 'tcp')

        # Ensure nothing was added to the manager.
        assert len(m.plugins) == 0

        mock_metadata.assert_called_once()
        mock_version.assert_called_once()

    def test_register_duplicate_plugin_id(self, mocker):
        # Mock test data
        mock_metadata = mocker.patch(
            'synse_server.plugin.client.PluginClientV3.metadata',
            return_value=V3Metadata(id='123', tag='foo'),
        )
        mock_version = mocker.patch(
            'synse_server.plugin.client.PluginClientV3.version',
            return_value=V3Version(),
        )

        # --- Test case -----------------------------
        m = plugin.PluginManager()
        m.plugins = {
            '123': plugin.Plugin(
                {'id': 'foo', 'tag': 'foo'},
                {},
                client.PluginClientV3('foo', 'tcp'),
            ),
        }

        plugin_id = m.register('localhost:5432', 'tcp')
        assert plugin_id == '123'
        # Ensure nothing new was added to the manager.
        assert len(m.plugins) == 1

        mock_metadata.assert_called_once()
        mock_version.assert_called_once()

    def test_register_success(self, mocker):
        # Mock test data
        mock_metadata = mocker.patch(
            'synse_server.plugin.client.PluginClientV3.metadata',
            return_value=V3Metadata(id='123', tag='foo'),
        )
        mock_version = mocker.patch(
            'synse_server.plugin.client.PluginClientV3.version',
            return_value=V3Version(),
        )

        # --- Test case -----------------------------
        m = plugin.PluginManager()

        plugin_id = m.register('localhost:5432', 'tcp')
        assert plugin_id == '123'
        assert len(m.plugins) == 1
        assert m.plugins[plugin_id].active is True

        mock_metadata.assert_called_once()
        mock_version.assert_called_once()

    def test_load_no_config(self, mocker):
        # Mock test data
        mocker.patch.dict('synse_server.config.options._full_config', {
            'plugin': {},
        })

        # --- Test case -----------------------------
        m = plugin.PluginManager()
        loaded = m.load()
        assert len(loaded) == 0

    def test_load_tcp_one(self, mocker):
        # Mock test data
        mocker.patch.dict('synse_server.config.options._full_config', {
            'plugin': {
                'tcp': [
                    'localhost:5001',
                ],
            },
        })

        # --- Test case -----------------------------
        m = plugin.PluginManager()
        loaded = m.load()
        assert len(loaded) == 1

    def test_load_tcp_multi(self, mocker):
        # Mock test data
        mocker.patch.dict('synse_server.config.options._full_config', {
            'plugin': {
                'tcp': [
                    'localhost:5001',
                    'localhost:5002',
                    'localhost:5003',
                ],
            },
        })

        # --- Test case -----------------------------
        m = plugin.PluginManager()
        loaded = m.load()
        assert len(loaded) == 3

    def test_load_unix_one(self, mocker):
        # Mock test data
        mocker.patch.dict('synse_server.config.options._full_config', {
            'plugin': {
                'unix': [
                    '/tmp/test/1',
                ],
            },
        })

        # --- Test case -----------------------------
        m = plugin.PluginManager()
        loaded = m.load()
        assert len(loaded) == 1

    def test_load_unix_multi(self, mocker):
        # Mock test data
        mocker.patch.dict('synse_server.config.options._full_config', {
            'plugin': {
                'unix': [
                    '/tmp/test/1',
                    '/tmp/test/2',
                    '/tmp/test/3',
                ],
            },
        })

        # --- Test case -----------------------------
        m = plugin.PluginManager()
        loaded = m.load()
        assert len(loaded) == 3

    def test_load_tcp_and_unix(self, mocker):
        # Mock test data
        mocker.patch.dict('synse_server.config.options._full_config', {
            'plugin': {
                'tcp': [
                    'localhost:5001',
                    'localhost:5002',
                    'localhost:5003',
                ],
                'unix': [
                    '/tmp/test/1',
                    '/tmp/test/2',
                    '/tmp/test/3',
                ],
            },
        })

        # --- Test case -----------------------------
        m = plugin.PluginManager()
        loaded = m.load()
        assert len(loaded) == 6

    def test_discover_no_addresses_found(self, mocker):
        # Mock test data
        mock_discover = mocker.patch(
            'synse_server.plugin.kubernetes.discover',
            return_value=[],
        )

        # --- Test case -----------------------------
        m = plugin.PluginManager()

        found = m.discover()

        assert len(found) == 0
        mock_discover.assert_called_once()

    def test_discover_one_address_found(self, mocker):
        # Mock test data
        mock_discover = mocker.patch(
            'synse_server.plugin.kubernetes.discover',
            return_value=['localhost:5001'],
        )

        # --- Test case -----------------------------
        m = plugin.PluginManager()

        found = m.discover()

        assert len(found) == 1
        assert ('localhost:5001', 'tcp') in found
        mock_discover.assert_called_once()

    def test_discover_multiple_addresses_found(self, mocker):
        # Mock test data
        mock_discover = mocker.patch(
            'synse_server.plugin.kubernetes.discover',
            return_value=['localhost:5001', 'localhost:5002'],
        )

        # --- Test case -----------------------------
        m = plugin.PluginManager()

        found = m.discover()

        assert len(found) == 2
        assert ('localhost:5001', 'tcp') in found
        assert ('localhost:5002', 'tcp') in found
        mock_discover.assert_called_once()

    def test_discover_fail_kubernetes_discovery(self, mocker):
        # Mock test data
        mock_discover = mocker.patch(
            'synse_server.plugin.kubernetes.discover',
            side_effect=ValueError(),
        )

        # --- Test case -----------------------------
        m = plugin.PluginManager()

        found = m.discover()

        assert len(found) == 0
        mock_discover.assert_called_once()

    def test_refresh_no_addresses(self):
        m = plugin.PluginManager()

        assert len(m.plugins) == 0
        m.refresh()
        assert len(m.plugins) == 0

    def test_refresh_loaded_ok(self, mocker):
        # Mock test data
        mock_load = mocker.patch(
            'synse_server.plugin.PluginManager.load',
            return_value=[('localhost:5001', 'tcp')],
        )
        mock_register = mocker.patch(
            'synse_server.plugin.PluginManager.register',
        )

        # --- Test case -----------------------------
        m = plugin.PluginManager()

        m.refresh()

        mock_load.assert_called_once()
        mock_register.assert_called_once()
        mock_register.assert_called_with(address='localhost:5001', protocol='tcp')

    def test_refresh_loaded_fail(self, mocker):
        # Mock test data
        mock_load = mocker.patch(
            'synse_server.plugin.PluginManager.load',
            return_value=[('localhost:5001', 'tcp')],
        )
        mock_register = mocker.patch(
            'synse_server.plugin.PluginManager.register',
            side_effect=ValueError(),
        )

        # --- Test case -----------------------------
        m = plugin.PluginManager()

        m.refresh()

        mock_load.assert_called_once()
        mock_register.assert_called_once()
        mock_register.assert_called_with(address='localhost:5001', protocol='tcp')

    def test_refresh_discover_ok(self, mocker):
        # Mock test data
        mock_discover = mocker.patch(
            'synse_server.plugin.PluginManager.discover',
            return_value=[('localhost:5001', 'tcp')],
        )
        mock_register = mocker.patch(
            'synse_server.plugin.PluginManager.register',
        )

        # --- Test case -----------------------------
        m = plugin.PluginManager()

        m.refresh()

        mock_discover.assert_called_once()
        mock_register.assert_called_once()
        mock_register.assert_called_with(address='localhost:5001', protocol='tcp')

    def test_refresh_discover_fail(self, mocker):
        # Mock test data
        mock_discover = mocker.patch(
            'synse_server.plugin.PluginManager.discover',
            return_value=[('localhost:5001', 'tcp')],
        )
        mock_register = mocker.patch(
            'synse_server.plugin.PluginManager.register',
            side_effect=ValueError(),
        )

        # --- Test case -----------------------------
        m = plugin.PluginManager()

        m.refresh()

        mock_discover.assert_called_once()
        mock_register.assert_called_once()
        mock_register.assert_called_with(address='localhost:5001', protocol='tcp')


class TestPlugin:
    """Test cases for the ``synse_server.plugin.Plugin`` class."""

    def test_init_ok(self):
        c = client.PluginClientV3('localhost:5432', 'tcp')
        p = plugin.Plugin(
            client=c,
            info={
                'tag': 'foo',
                'id': '123',
            },
            version={},
        )

        assert p.active is False
        assert p.client == c
        assert p.address == 'localhost:5432'
        assert p.protocol == 'tcp'
        assert p.tag == 'foo'
        assert p.id == '123'

    def test_init_missing_tag(self):
        with pytest.raises(ValueError):
            plugin.Plugin(
                client=client.PluginClientV3('localhost:5432', 'tcp'),
                info={
                    'id': '123',
                },
                version={},
            )

    def test_init_missing_id(self):
        with pytest.raises(ValueError):
            plugin.Plugin(
                client=client.PluginClientV3('localhost:5432', 'tcp'),
                info={
                    'tag': 'foo',
                },
                version={},
            )

    def test_str(self, simple_plugin):
        assert str(simple_plugin) == '<Plugin (test/foo): 123>'

    def test_context_no_error(self, simple_plugin):
        simple_plugin.active = False
        assert simple_plugin.active is False

        with simple_plugin as cli:
            assert isinstance(cli, client.PluginClientV3)
            assert cli == simple_plugin.client

        assert simple_plugin.active is True

    def test_context_unexpected_error(self, simple_plugin):
        assert simple_plugin.active is True

        with pytest.raises(ValueError):
            with simple_plugin:
                raise ValueError('test error')

        assert simple_plugin.active is False

    def test_context_plugin_error(self, simple_plugin):
        simple_plugin.active = False
        assert simple_plugin.active is False

        with pytest.raises(errors.PluginError):
            with simple_plugin:
                raise errors.PluginError('test error')

        assert simple_plugin.active is True

    def test_mark_active_from_active(self, simple_plugin):
        simple_plugin.active = True
        simple_plugin.mark_active()
        assert simple_plugin.active is True

    def test_mark_active_from_inactive(self, simple_plugin):
        simple_plugin.active = False
        simple_plugin.mark_active()
        assert simple_plugin.active is True

    def test_mark_inactive_from_active(self, simple_plugin):
        simple_plugin.active = True
        simple_plugin.mark_inactive()
        assert simple_plugin.active is False

    def test_mark_inactive_from_inactive(self, simple_plugin):
        simple_plugin.active = False
        simple_plugin.mark_inactive()
        assert simple_plugin.active is False
