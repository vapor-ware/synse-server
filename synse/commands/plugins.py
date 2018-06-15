"""Command handler for the `plugins` route."""

import grpc

from synse import plugin, utils
from synse.i18n import _
from synse.log import logger
from synse.proto import util
from synse.scheme.plugins import PluginsResponse


async def get_plugins():
    """The handler for the Synse Server "plugins" API command.

    Returns:
        PluginsResponse: The "plugins" response scheme model.
    """
    logger.debug(_('Plugins Command'))

    # Register plugins. If no plugins exist, this will attempt to register
    # new ones. If plugins already exist, this will just ensure that all of
    # the tracked plugins are up to date.
    plugin.register_plugins()

    # We need to collect information from a few sources for each plugin:
    #  - config (network/address) .. this should be encoded in the plugin model
    #  - metadata (grpc metadata) .. we need to make a call for this
    #  - health (grpc health)     .. we need to make a call for this
    plugins = []
    async for p in plugin.get_plugins():
        _plugin = p[1]
        # Get the plugin config and add it to the plugin data
        plugin_data = {
            'tag': _plugin.tag,
            'name': _plugin.name,
            'description': _plugin.description,
            'maintainer': _plugin.maintainer,
            'vcs': _plugin.vcs,
            'version': {
                'plugin_version': _plugin.version.pluginVersion,
                'sdk_version': _plugin.version.sdkVersion,
                'build_date': _plugin.version.buildDate,
                'git_commit': _plugin.version.gitCommit,
                'git_tag': _plugin.version.gitTag,
                'arch': _plugin.version.arch,
                'os': _plugin.version.os,
            },
            'network': {
                'protocol': _plugin.protocol,
                'address': _plugin.address
            }
        }

        # Get the plugin health data
        try:
            health = _plugin.client.health()
        except grpc.RpcError as ex:
            plugin_data['health'] = {
                'timestamp': utils.rfc3339now(),
                'status': 'error',
                'message': str(ex),
                'checks': []
            }
        else:
            plugin_data['health'] = {
                'timestamp': health.timestamp,
                'status': util.plugin_health_status_name(health.status),
                'message': '',
                'checks': [
                    {
                        'name': check.name,
                        'status': util.plugin_health_status_name(check.status),
                        'message': check.message,
                        'timestamp': check.timestamp,
                        'type': check.type,
                    } for check in health.checks]
            }

        plugins.append(plugin_data)

    return PluginsResponse(data=plugins)
