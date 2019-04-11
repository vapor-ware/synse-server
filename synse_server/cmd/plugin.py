
from synse_grpc import utils

import synse_server.plugin
import synse_server.utils
from synse_server import errors
from synse_server.log import logger
from synse_server.i18n import _


async def plugin(plugin_id):
    """Generate the plugin response data.

    Args:
        plugin_id (str): The ID of the plugin to get information for.

    Returns:
        dict: A dictionary representation of the plugin response.
    """
    logger.debug(_('issuing command'), command='PLUGIN', plugin_id=plugin_id)

    # If there are no plugins registered, re-registering to ensure
    # the most up-to-date plugin state.
    if not synse_server.plugin.manager.has_plugins():
        synse_server.plugin.manager.refresh()

    p = synse_server.plugin.manager.get(plugin_id)
    if p is None:
        raise errors.NotFound(f'plugin not found: {plugin_id}')

    try:
        health = p.client.health()
    except Exception as e:
        raise errors.ServerError(
            'error while issuing gRPC request: plugin health'
        ) from e

    response = {
        **p.metadata,
        'active': True,  # fixme
        'network': {
            'address': p.address,
            'protocol': p.protocol,
        },
        'version': p.version,
        'health': utils.to_dict(health),
    }

    return response


async def plugins():
    """Generate the plugin summary response data.

    Returns:
        list[dict]: A list of dictionary representations of the plugin
        summary response(s).
    """
    logger.debug(_('issuing command'), command='PLUGINS')

    # If there are no plugins registered, re-registering to ensure
    # the most up-to-date plugin state.
    if not synse_server.plugin.manager.has_plugins():
        synse_server.plugin.manager.refresh()

    summaries = []
    for p in synse_server.plugin.manager:
        summary = p.metadata.copy()
        summary['active'] = True  # fixme
        del summary['vcs']
        summaries.append(summary)

    return summaries


async def plugin_health():
    """Generate the plugin health response data.

    Returns:
         dict: A dictionary representation of the plugin health.
    """
    logger.debug(_('issuing command'), command='PLUGIN HEALTH')

    # If there are no plugins registered, re-registering to ensure
    # the most up-to-date plugin state.
    if not synse_server.plugin.manager.has_plugins():
        synse_server.plugin.manager.refresh()

    active_count = 0
    inactive_count = 0
    healthy = []
    unhealthy = []

    for p in synse_server.plugin.manager:
        # TODO: all the logic + handling around active + inactive needs to be worked
        #   out a bunch more. What is currently here is good enough to get the ball
        #   rolling, but is not very comprehensive.
        try:
            health = p.client.health()
        except Exception as e:
            logger.warning(_('failed to get plugin health'), plugin=p.tag, error=e)
            inactive_count += 1
        else:
            if health.status == 1:  # OK
                active_count += 1
                healthy.append(p.id)
            else:
                active_count += 1
                unhealthy.append(p.id)

    is_healthy = len(synse_server.plugin.manager.plugins) == len(healthy)
    return {
        'status': 'healthy' if is_healthy else 'unhealthy',
        'updated': synse_server.utils.rfc3339now(),
        'healthy': healthy,
        'unhealthy': unhealthy,
        'active': active_count,
        'inactive': inactive_count,
    }
