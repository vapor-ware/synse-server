"""Response scheme for the `plugins` endpoint."""

from synse.scheme.base_response import SynseResponse


class PluginsResponse(SynseResponse):
    """A PluginsResponse is the response data for the Synse 'plugins' command.

    Response Example:
        [
          {
            "network":{
              "protocol":"tcp",
              "address":"emulator-plugin:5001"
            },
            "name":"emulator plugin",
            "maintainer":"vaporio",
            "tag":"vaporio\/emulator-plugin",
            "description":"A plugin with emulated devices and data",
            "vcs":"github.com\/vapor-ware\/synse-emulator-plugin",
            "version":{
              "plugin_version":"2.0.0",
              "sdk_version":"1.0.0",
              "build_date":"2018-06-14T16:24:09",
              "git_commit":"13e6478",
              "git_tag":"1.0.2-5-g13e6478",
              "arch":"amd64",
              "os":"linux"
            },
            "health":{
              "timestamp":"2018-06-14T16:45:50.245596Z",
              "status":"ok",
              "checks":[
                {
                  "name":"read buffer health",
                  "status":"ok",
                  "message":"",
                  "timestamp":"",
                  "type":"periodic"
                },
                {
                  "name":"write buffer health",
                  "status":"ok",
                  "message":"",
                  "timestamp":"",
                  "type":"periodic"
                }
              ]
            }
          }
        ]

    Args:
        data (list): List of dictionaries containing the name, network,
            and address of the registered plugins.
    """

    def __init__(self, data):
        self.data = data
