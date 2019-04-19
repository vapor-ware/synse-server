

class TestPluginManager:
    """Test cases for the ``synse_server.plugin.PluginManager`` class."""

    def test_has_no_plugins(self):
        pass

    def test_has_plugins_one(self):
        pass

    def test_has_plugins_multiple(self):
        pass

    def test_get_plugin_not_found(self):
        pass

    def test_get_plugin_found(self):
        pass

    def test_register_fail_metadata_call(self):
        pass

    def test_register_fail_version_call(self):
        pass

    def test_register_duplicate_plugin_id(self):
        pass

    def test_register_fail_plugin_init(self):
        pass

    def test_register_success(self):
        pass

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
        pass

    def test_init_missing_tag(self):
        pass

    def test_init_missing_id(self):
        pass

    def test_str(self):
        pass

    def test_context_no_error(self):
        pass

    def test_context_unexpected_error(self):
        pass

    def test_context_plugin_error(self):
        pass

    def test_mark_active_from_active(self):
        pass

    def test_mark_active_from_inactive(self):
        pass

    def test_mark_inactive_from_active(self):
        pass

    def test_mark_inactive_from_inactive(self):
        pass
