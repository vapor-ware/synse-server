"""Synse Server wrapper object definition.

The global server state and server initialization and setup functionality
are defined here.
"""

import asyncio
import functools
import os
import signal
import sys
import warnings

import containerlog.proxy.std
from containerlog import get_logger

import synse_server
from synse_server import app, cache, config, loop, metrics, plugin, tasks

# Patch the sanic loggers to use the containerlog proxy.
containerlog.proxy.std.patch("sanic*")
containerlog.enable_contextvars()

logger = get_logger()


class Synse:
    """Synse is a wrapper around the Sanic application that defines the API
    for Synse Server.

    This class provides the functionality to properly initialize, configure,
    and run the application. It should be used to initialize all instances
    of Synse Server.

    Synse can be configured from:
      * YAML config file (either in the current working directory '.',
        or the Synse config directory '/etc/synse/server'.
      * Environment variable with the 'SYNSE' prefix.

    Args:
        host (str): The address to host the Synse Server application on.
            (default: "0.0.0.0")
        port (int): The port to host the Synse Server application on.
            (default: 5000)
        log_header (bool): Log out the application header information. This
            includes application version information and other pieces of
            metadata. (default: True)
    """

    # Define the well-known paths that will be used by Synse Server
    _current_dir = '.'
    _server_config_dir = '/etc/synse/server'
    _socket_dir = '/tmp/synse'

    # Header information that can be logged out for information on
    # the Synse Server instance.
    _header = fr'''
   __
  / _\_   _ _ __  ___  ___
  \ \| | | | '_ \/ __|/ _ \
  _\ \ |_| | | | \__ \  __/
  \__/\__, |_| |_|___/\___|
      |___/

    {synse_server.__description__}

    author:  {synse_server.__author__}
    version: {synse_server.__version__}
    api:     {synse_server.__api_version__}
    url:     {synse_server.__url__}
    license: {synse_server.__license__}

'''

    def __init__(self, host: str = None, port: int = 5000, log_header: bool = True):
        self.host = host or '0.0.0.0'
        self.port = port
        self.log_header = log_header

        # Prior to initializing the Sanic application, we want to load the
        # configuration and various other components. This will allow us to
        # fully initialize the app, as well as have logging, etc. ready to go.
        self._initialize()

        # With setup complete, we can initialize a new Sanic application.
        self.app = app.app

        # The Sanic asyncio server
        self.server = None

    def _initialize(self) -> None:
        """Setup the Synse Server instance.

        This is intended to be run on initialization of the Synse class.
        Setting up on init ensure that we have all the config we need for
        the backing Sanic application. Additionally, it lets us set up
        logging early on.
        """
        logger.info('initializing synse server')

        # Load the application configuration(s).
        self.reload_config()
        logger.info(
            'loaded config',
            source_file=config.options.config_file,
            config=config.options.config,
        )

        # Make sure that the filesystem layout needed by Synse Server
        # is present. If not, create the required directories.
        os.makedirs(self._server_config_dir, exist_ok=True)
        os.makedirs(self._socket_dir, exist_ok=True)
        logger.info(
            'created server directories on filesystem',
            dirs=(self._server_config_dir, self._socket_dir),
        )

        # Configure caches
        cache.transaction_cache.ttl = config.options.get('cache.transaction.ttl', None)

    def run(self) -> None:
        """Run Synse Server."""

        # Set up application logging. Default is debug mode enabled. Set the level
        # to INFO if debug disabled.
        # FIXME (also checking the historical "logging" configuration option, which
        #  is now deprecated. This will be removed in an upcoming release.)
        _log_opt_debug = config.options.get('logging') != 'debug'
        if not config.options.get('debug') or _log_opt_debug:
            if _log_opt_debug:
                warnings.warn(
                    'You are using a deprecated configuration option (logging). '
                    'Instead, use "debug" (debug=True / debug=False)'
                )
            containerlog.set_level(containerlog.INFO)  # pragma: nocover

        # Register signals for graceful termination
        for sig in ('SIGINT', 'SIGTERM'):
            logger.info('adding signal handler to synse loop')
            loop.synse_loop.add_signal_handler(
                sig=getattr(signal, sig),
                callback=functools.partial(_handle_signal, sig, loop.synse_loop),
            )

        logger.info('running synse server')

        # If we are configured to log the header, write it to stdout instead
        # of using the logger, since the structured logger will not format
        # this info correctly.
        if self.log_header:
            sys.stdout.write(self._header)

        # Add background tasks. This needs to be done at run so any tasks
        # that take config options have the loaded config available to them.
        logger.debug('registering tasks with application')
        tasks.register_with_app(self.app)

        # If application metrics are enabled, configure the application now.
        if config.options.get('metrics.enabled'):
            logger.info('application performance metrics enabled (/metrics)')
            metrics.Monitor(self.app).register()

        # Load the SSL configuration, if defined.
        ssl_context = None
        if config.options.get('ssl'):
            ssl_context = {
                'cert': config.options.get('ssl.cert'),
                'key': config.options.get('ssl.key'),
            }
            logger.info('SSL configured for Synse Server', config=ssl_context)
        else:
            logger.info('running server without SSL (no key/cert configured)')

        # Check if the gRPC cert is configured, and if so, verify that the cert
        # exists. (https://github.com/vapor-ware/synse-server/issues/388)
        # This is done here as opposed to waiting to fail on client creation
        # so the server can hard fail with certs that don't exist.
        if config.options.get('grpc.tls.cert'):
            cert = config.options.get('grpc.tls.cert')
            logger.debug('checking for gRPC cert', cert=cert)
            if not os.path.exists(cert):
                raise FileNotFoundError(
                    f'gRPC cert not found: {cert}'
                )

        # Load the plugins defined in the configuration.
        plugin.manager.refresh()

        logger.debug('serving API endpoints')
        self.server = self.app.create_server(
            host=self.host,
            port=self.port,
            ssl=ssl_context,
            return_asyncio_server=True,
            access_log=False,
        )
        t = asyncio.ensure_future(self.server, loop=loop.synse_loop)

        # Wait until the server has been created and run. If there was an error
        # creating the server, this will raise an exception.
        loop.synse_loop.run_until_complete(t)

        # The server is now running on the loop, so run the loop forever.
        loop.synse_loop.run_forever()

    def reload_config(self) -> None:
        """(Re)loads the application configuration.

        The application configuration can be loaded from two placed:
          * YAML config file
          * Environment variable

        This will attempt to load from each, where any environment-defined configuration
        will take precedence over any YAML-defined configuration.
        """
        # Set the default config file search paths.
        config.options.add_config_paths(
            self._current_dir,
            self._server_config_dir,
        )

        # Enable environment-based configuration.
        config.options.env_prefix = 'SYNSE'
        config.auto_env = True

        # Load and validate the configuration values.
        config.options.parse(requires_cfg=False)
        config.options.validate()


def _handle_signal(signame, loop):
    """Handler function for when the Synse loop receives a registered signal.

    This indicates that the server should shut down gracefully.
    """
    logger.info('received termination signal, stopping loop', signal=signame, loop=loop)
    loop.stop()
