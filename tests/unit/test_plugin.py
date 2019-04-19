
from collections.abc import Iterable
from unittest import mock
from grpc import RpcError

import pytest
from synse_grpc import errors as client_errors
from synse_grpc import client
from synse_grpc.api import V3Metadata, V3Version

from synse_server import errors, plugin


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

    @mock.patch('synse_server.plugin.client.PluginClientV3.metadata', side_effect=RpcError())
    def test_register_fail_metadata_call(self, mock_metadata):
        m = plugin.PluginManager()

        with pytest.raises(RpcError):
            m.register('localhost:5432', 'tcp')

        # Ensure nothing was added to the manager.
        assert len(m.plugins) == 0

        mock_metadata.assert_called_once()

    @mock.patch('synse_server.plugin.client.PluginClientV3.metadata', return_value=V3Metadata())
    @mock.patch('synse_server.plugin.client.PluginClientV3.version', side_effect=RpcError())
    def test_register_fail_version_call(self, mock_metadata, mock_version):
        m = plugin.PluginManager()

        with pytest.raises(RpcError):
            m.register('localhost:5432', 'tcp')

        # Ensure nothing was added to the manager.
        assert len(m.plugins) == 0

        mock_metadata.assert_called_once()
        mock_version.assert_called_once()

    @mock.patch('synse_server.plugin.client.PluginClientV3.metadata', return_value=V3Metadata())
    @mock.patch('synse_server.plugin.client.PluginClientV3.version', return_value=V3Version())
    def test_register_fail_plugin_init(self, mock_metadata, mock_version):
        m = plugin.PluginManager()

        with pytest.raises(ValueError):
            m.register('localhost:5432', 'tcp')

        # Ensure nothing was added to the manager.
        assert len(m.plugins) == 0

        mock_metadata.assert_called_once()
        mock_version.assert_called_once()

    @mock.patch('synse_server.plugin.client.PluginClientV3.metadata', return_value=V3Metadata(id='123', tag='foo'))
    @mock.patch('synse_server.plugin.client.PluginClientV3.version', return_value=V3Version())
    def test_register_duplicate_plugin_id(self, mock_metadata, mock_version):
        m = plugin.PluginManager()
        m.plugins = {
            '123': 'placeholder',
        }

        with pytest.raises(errors.ServerError):
            m.register('localhost:5432', 'tcp')

        # Ensure nothing new was added to the manager.
        assert len(m.plugins) == 1

        mock_metadata.assert_called_once()
        mock_version.assert_called_once()

    @mock.patch('synse_server.plugin.client.PluginClientV3.metadata', return_value=V3Metadata(id='123', tag='foo'))
    @mock.patch('synse_server.plugin.client.PluginClientV3.version', return_value=V3Version())
    def test_register_success(self, mock_metadata, mock_version):
        m = plugin.PluginManager()

        plugin_id = m.register('localhost:5432', 'tcp')
        assert plugin_id == '123'
        assert len(m.plugins) == 1
        assert m.plugins[plugin_id].active is True

        mock_metadata.assert_called_once()
        mock_version.assert_called_once()

    def test_load_no_config(self):
        pass

    def test_load_tcp_one(self):
        pass

    def test_load_tcp_multi(self):
        pass

    def test_load_unix_one(self):
        pass

    def test_load_unix_multi(self):
        pass

    def test_load_tcp_and_unix(self):
        pass

    def test_load_failed_tcp_register(self):
        pass

    def test_load_failed_unix_register(self):
        pass

    def test_discover_no_addresses_found(self):
        pass

    def test_discover_one_address_found(self):
        pass

    def test_discover_multiple_addresses_found(self):
        pass

    def test_discover_fail_kubernetes_discovery(self):
        pass

    def test_refresh_no_addresses(self):
        pass

    def test_refresh_discovered_plugin_already_exists(self):
        pass

    def test_refresh_discovered_plugin_does_not_exist(self):
        pass

    def test_refresh_discovered_plugin_fails_registration(self):
        pass

    def test_refresh_discover_with_no_current_plugins(self):
        pass

    def test_refresh_loaded_plugin_already_exists(self):
        # TODO: need to add loaded to refresh logic
        pass

    def test_refresh_loaded_plugin_does_not_exist(self):
        pass

    def test_refresh_loaded_plugin_fails_registration(self):
        pass

    def test_refresh_load_with_no_current_plugins(self):
        pass


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

    def test_str(self):
        p = plugin.Plugin(
            client=client.PluginClientV3('localhost:5432', 'tcp'),
            info={
                'tag': 'foo',
                'id': '123',
            },
            version={},
        )

        assert str(p) == '<Plugin (foo): 123>'

    def test_context_no_error(self):
        p = plugin.Plugin(
            client=client.PluginClientV3('localhost:5432', 'tcp'),
            info={
                'tag': 'foo',
                'id': '123',
            },
            version={},
        )

        assert p.active is False

        with p as cli:
            assert isinstance(cli, client.PluginClientV3)
            assert cli == p.client

        assert p.active is True

    def test_context_unexpected_error(self):
        p = plugin.Plugin(
            client=client.PluginClientV3('localhost:5432', 'tcp'),
            info={
                'tag': 'foo',
                'id': '123',
            },
            version={},
        )

        assert p.active is False

        with pytest.raises(ValueError):
            with p:
                raise ValueError('test error')

        assert p.active is False

    def test_context_plugin_error(self):
        p = plugin.Plugin(
            client=client.PluginClientV3('localhost:5432', 'tcp'),
            info={
                'tag': 'foo',
                'id': '123',
            },
            version={},
        )

        assert p.active is False

        with pytest.raises(client_errors.PluginError):
            with p:
                raise client_errors.PluginError('test error')

        assert p.active is True

    def test_mark_active_from_active(self):
        p = plugin.Plugin(
            client=client.PluginClientV3('localhost:5432', 'tcp'),
            info={
                'tag': 'foo',
                'id': '123',
            },
            version={},
        )

        p.active = True

        p.mark_active()
        assert p.active is True

    def test_mark_active_from_inactive(self):
        p = plugin.Plugin(
            client=client.PluginClientV3('localhost:5432', 'tcp'),
            info={
                'tag': 'foo',
                'id': '123',
            },
            version={},
        )

        p.active = False

        p.mark_active()
        assert p.active is True

    def test_mark_inactive_from_active(self):
        p = plugin.Plugin(
            client=client.PluginClientV3('localhost:5432', 'tcp'),
            info={
                'tag': 'foo',
                'id': '123',
            },
            version={},
        )

        p.active = True

        p.mark_inactive()
        assert p.active is False

    def test_mark_inactive_from_inactive(self):
        p = plugin.Plugin(
            client=client.PluginClientV3('localhost:5432', 'tcp'),
            info={
                'tag': 'foo',
                'id': '123',
            },
            version={},
        )

        p.active = False

        p.mark_inactive()
        assert p.active is False
