
import pytest

from synse_server import server


class TestSynse:
    """Tests for the ``synse_server.server.Synse`` class, which wraps the
    Sanic server and performs setup for the Synse Server application.
    """

    def test_init_ok(self, mocker):
        # Mock test data
        mock_initialize = mocker.patch(
            'synse_server.server.Synse._initialize',
        )

        # --- Test case -----------------------------
        synse = server.Synse()
        assert synse.host == '0.0.0.0'
        assert synse.port == 5000
        assert synse.log_header is True
        assert synse.app is not None

        mock_initialize.assert_called_once()

    def test_initialize(self, mocker):
        # Mock test data
        mock_mkdirs = mocker.patch(
            'os.makedirs',
        )
        mock_logger = mocker.patch(
            'synse_server.server.setup_logger'
        )
        mock_reload_config = mocker.patch(
            'synse_server.server.Synse.reload_config',
        )

        # --- Test case -----------------------------
        synse = server.Synse()

        mock_logger.assert_called_once()
        mock_reload_config.assert_called_once()
        mock_mkdirs.assert_called()
        mock_mkdirs.assert_has_calls([
            mocker.call(synse._server_config_dir, exist_ok=True),
            mocker.call(synse._socket_dir, exist_ok=True),
        ])

    def test_run_ok_with_metrics(self, mocker):
        # Mock test data
        mocker.patch.dict('synse_server.config.options._full_config', {
            'metrics': {
                'enabled': True,
            },
        })
        mock_initialize = mocker.patch(
            'synse_server.server.Synse._initialize',
        )
        mock_run = mocker.patch(
            'synse_server.loop.synse_loop.run_forever'
        )
        mock_write = mocker.patch('sys.stdout.write')

        # --- Test case -----------------------------
        synse = server.Synse()
        assert 'metrics' not in synse.app.router.routes_names.keys()

        synse.run()
        assert 'metrics' in synse.app.router.routes_names.keys()

        mock_write.assert_called_once()
        mock_initialize.assert_called_once()
        mock_run.assert_called_once()

    def test_run_ok_with_ssl(self, mocker):
        # Mock test data
        mocker.patch.dict('synse_server.config.options._full_config', {
            'ssl': {
                'cert': 'test-cert',
                'key': 'test-key',
            },
        })
        mock_initialize = mocker.patch(
            'synse_server.server.Synse._initialize',
        )
        mock_run = mocker.patch(
            'synse_server.loop.synse_loop.run_forever'
        )
        mock_write = mocker.patch('sys.stdout.write')

        # --- Test case -----------------------------
        synse = server.Synse(log_header=False)
        synse.run()

        mock_write.assert_not_called()
        mock_initialize.assert_called_once()
        mock_run.assert_called_once()

    def test_run_error(self, mocker):
        # Mock test data
        mocker.patch.dict('synse_server.config.options._full_config', {
            'ssl': {
                'cert': 'test-cert',
                'key': 'test-key',
            },
        })
        mock_initialize = mocker.patch(
            'synse_server.server.Synse._initialize',
        )
        mock_run = mocker.patch(
            'synse_server.loop.synse_loop.run_forever',
            side_effect=ValueError(),
        )

        # --- Test case -----------------------------
        synse = server.Synse(log_header=False)

        with pytest.raises(ValueError):
            synse.run()

        mock_initialize.assert_called_once()
        mock_run.assert_called_once()

    def test_reload_config(self, mocker):
        # Mock test data
        mock_parse = mocker.patch(
            'bison.Bison.parse',
        )
        mock_validate = mocker.patch(
            'bison.Bison.validate'
        )
        mock_initialize = mocker.patch(
            'synse_server.server.Synse._initialize',
        )

        # --- Test case -----------------------------
        synse = server.Synse(log_header=False)
        synse.reload_config()

        mock_validate.assert_called_once()
        mock_parse.assert_called_once()
        mock_parse.assert_called_with(requires_cfg=False)
        mock_initialize.assert_called_once()
