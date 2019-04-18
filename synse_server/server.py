""""""

import os
import sys

from sanic_prometheus import monitor

import synse_server
from synse_server import app, config, plugin
from synse_server.i18n import _
from synse_server.log import logger, setup_logger


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
    _header = f'''
   __
  / _\_   _ _ __  ___  ___
  \ \| | | | '_ \/ __|/ _ \\
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

    def __init__(self, host='0.0.0.0', port=5000, log_header=True):
        self.host = host
        self.port = port
        self.log_header = log_header

        # Prior to initializing the Sanic application, we want to load the
        # configuration and various other components. This will allow us to
        # fully setup the app, as well as have logging, etc. ready to go.
        self._setup()

        # With setup complete, we can initialize a new Sanic application.
        self.app = app.new_app()

    def _setup(self):
        """Setup the Synse Server instance.

        This is intended to be run on initialization of the Synse class.
        Setting up on init ensure that we have all the config we need for
        the backing Sanic application. Additionally, it lets us set up
        logging early on.
        """
        # Load the application configuration(s).
        self.reload_config()
        logger.info(_('loaded config'), config=config.options.config)

        # Configure logging, using the loaded config.
        setup_logger()

        logger.debug(_('setting up synse server'))

        # Make sure that the filesystem layout needed by Synse Server
        # is present. If not, create the required directories.
        os.makedirs(self._server_config_dir, exist_ok=True)
        os.makedirs(self._socket_dir, exist_ok=True)

    def run(self):
        """Run Synse Server."""
        logger.info(_('running synse server'))

        # If application metrics are enabled, configure the application now.
        if config.options.get('metrics.enabled'):
            logger.debug(_('application performance metrics enabled'))
            monitor(self.app).expose_endpoint()

        # If we are configured to log the header, write it to stdout instead
        # of using the logger, since the structured logger will not format
        # this info correctly.
        if self.log_header:
            sys.stdout.write(self._header)

        # Load the plugins defined in the configuration.
        plugin.manager.load()

        logger.debug(_('starting Sanic application'))
        self.app.run(
            host=self.host,
            port=self.port,
            access_log=False,
        )

    def reload_config(self):
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
