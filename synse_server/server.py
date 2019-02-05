""""""

import sys

import synse_server
from synse_server import app, config
from synse_server.log import logger


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

    version: {synse_server.__version__}
    author:  {synse_server.__author__}
    url:     {synse_server.__url__}
    license: {synse_server.__license__}

'''

    def __init__(self, host='0.0.0.0', port=5000, log_header=True):
        self.host = host
        self.port = port

        self.log_header = log_header

        self.app = app.new_app()

        self.is_setup = False

    def setup(self):
        """Setup the Synse Server instance."""
        # FIXME (etd): this should probably just run on init to ensure
        #  we have everything set up when needed
        logger.info('setting up synse server')

        # TODO (etd): on init, we should ensure that the necessary directories
        #  in the filesystem are present, if not we should create them.
        self.is_setup = True

    def run(self):
        """Run Synse Server."""
        logger.info('running synse server')

        if not self.is_setup:
            self.setup()

        # If we are configured to log the header, write it to stdout instead
        # of using the logger, since the structured logger will not format
        # this info correctly.
        if self.log_header:
            sys.stdout.write(self._header)

        self.app.run(
            host=self.host,
            port=self.port,
        )

    def load_config(self):
        """Load the application configuration.

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
