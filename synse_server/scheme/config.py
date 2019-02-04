"""Response scheme for the `config` endpoint."""

from synse_server import config
from synse_server.scheme.base_response import SynseResponse


class ConfigResponse(SynseResponse):
    """A ConfigResponse is the response data for a Synse 'config' command.

    The JSON response returned by the Synse endpoint, constructed from
    the data here, should follow the configuration scheme as it is
    defined in the `synse.config` module.

    Response Example:
        {
          "logging": "debug",
          "pretty_json": true,
          "locale": "en_US",
          "plugin": {
            "unix": {
              "emulator": null
            }
          },
          "cache": {
            "meta": {
              "ttl": 20
            },
            "transaction": {
              "ttl": 300
            }
          },
          "grpc": {
            "timeout": 3
          }
        }
    """

    def __init__(self):
        self.data = {k: v for k, v in config.options.config.items() if not k.startswith('_')}
