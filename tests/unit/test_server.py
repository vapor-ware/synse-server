"""Unit tests for the ``synse_server.server`` module."""

import mock
import pytest

from synse_server import server


class TestSynse:
    """Tests for the ``synse_server.server.Synse`` class, which wraps the
    Sanic server and performs setup for the Synse Server application.
    """

    @mock.patch('synse_server.server.Synse._initialize')
    def test_init_ok(self, mock_init):
        synse = server.Synse()
        assert synse.host == '0.0.0.0'
        assert synse.port == 5000
        assert synse.log_header is True
        assert synse.app is not None

        mock_init.assert_called_once()

    @mock.patch('os.makedirs')
    @mock.patch('synse_server.server.setup_logger')
    @mock.patch('synse_server.server.Synse.reload_config')
    def test_initialize(self, mock_reload, mock_logger, mock_mkdirs):
        synse = server.Synse()

        mock_logger.assert_called_once()
        mock_reload.assert_called_once()
        mock_mkdirs.assert_has_calls([
            mock.call(synse._server_config_dir, exist_ok=True),
            mock.call(synse._socket_dir, exist_ok=True),
        ])

    @mock.patch.dict('synse_server.config.options._full_config', {'metrics': {'enabled': True}})
    @mock.patch('synse_server.server.Synse._initialize')
    @mock.patch('synse_server.loop.synse_loop.run_forever')
    @mock.patch('synse_server.loop.synse_loop.run_until_complete')
    @mock.patch('sys.stdout.write')
    def test_run_ok_with_metrics(self, mock_write, mock_ruc, mock_run, mock_init):
        synse = server.Synse()

        assert ('metrics',) not in synse.app.router.routes_all

        synse.run()

        assert ('metrics',) in synse.app.router.routes_all

        mock_write.assert_called_once()
        mock_init.assert_called_once()
        mock_ruc.assert_called_once()
        mock_run.assert_called_once()

    @mock.patch.dict(
        'synse_server.config.options._full_config',
        {'ssl': {'cert': 'test-cert', 'key': 'test-key'}},
    )
    @mock.patch('synse_server.server.Synse._initialize')
    @mock.patch('synse_server.loop.synse_loop.run_forever')
    @mock.patch('synse_server.loop.synse_loop.run_until_complete')
    @mock.patch('sys.stdout.write')
    def test_run_ok_with_ssl(self, mock_write, mock_ruc, mock_run, mock_init):
        synse = server.Synse(log_header=False)
        synse.run()

        mock_write.assert_not_called()
        mock_init.assert_called_once()
        mock_ruc.assert_called_once()
        mock_run.assert_called_once()

    @mock.patch.dict(
        'synse_server.config.options._full_config',
        {'grpc': {'tls': {'cert': 'test-cert'}}},
    )
    @mock.patch('synse_server.server.Synse._initialize')
    @mock.patch('synse_server.loop.synse_loop.run_forever')
    @mock.patch('synse_server.loop.synse_loop.run_until_complete')
    @mock.patch('sys.stdout.write')
    def test_run_grpc_cert_error(self, mock_write, mock_ruc, mock_run, mock_init):
        synse = server.Synse(log_header=False)

        with pytest.raises(FileNotFoundError):
            synse.run()

        mock_write.assert_not_called()
        mock_init.assert_called_once()
        mock_ruc.assert_not_called()
        mock_run.assert_not_called()

    @mock.patch('synse_server.server.Synse._initialize')
    @mock.patch('synse_server.loop.synse_loop.run_forever', side_effect=ValueError)
    def test_run_error(self, mock_run, mock_init):
        synse = server.Synse(log_header=False)

        with pytest.raises(ValueError):
            synse.run()

        mock_init.assert_called_once()
        mock_run.assert_called_once()

    @mock.patch('synse_server.server.Synse._initialize')
    @mock.patch('synse_server.loop.synse_loop.run_until_complete', side_effect=ValueError)
    @mock.patch('synse_server.loop.synse_loop.run_forever')
    def test_run_error2(self, mock_run, mock_ruc, mock_init):
        synse = server.Synse(log_header=False)

        with pytest.raises(ValueError):
            synse.run()

        mock_init.assert_called_once()
        mock_ruc.assert_called_once()
        mock_run.assert_not_called()

    @mock.patch('bison.Bison.parse')
    @mock.patch('bison.Bison.validate')
    @mock.patch('synse_server.server.Synse._initialize')
    def test_reload_config(self, mock_init, mock_validate, mock_parse):
        synse = server.Synse(log_header=False)
        synse.reload_config()

        mock_validate.assert_called_once()
        mock_parse.assert_called_once_with(requires_cfg=False)
        mock_init.assert_called_once()
