
from synse_grpc import api, utils

import synse_server.utils
from synse_server import errors
from synse_server.i18n import _
from synse_server.log import logger
from synse_server.plugin import manager


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
    if not manager.has_plugins():
        manager.refresh()

    p = manager.get(plugin_id)
    if p is None:
        raise errors.NotFound(f'plugin not found: {plugin_id}')

    try:
        with p as client:
            health = client.health()
    except Exception as e:
        raise errors.ServerError(
            'error while issuing gRPC request: plugin health'
        ) from e

    response = {
        **p.metadata,
        'active': p.active,
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
    if not manager.has_plugins():
        manager.refresh()

    summaries = []
    for p in manager:
        summary = p.metadata.copy()
        summary['active'] = p.active
        if 'vcs' in summary:
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
    if not manager.has_plugins():
        manager.refresh()

    active_count = 0
    inactive_count = 0
    healthy = []
    unhealthy = []

    for p in manager:
        try:
            with p as client:
                health = client.health()
        except Exception as e:
            logger.warning(_('failed to get plugin health'), plugin=p.tag, error=e)
        else:
            if health.status == api.OK:
                healthy.append(p.id)
            else:
                unhealthy.append(p.id)
        finally:
            if p.active:
                active_count += 1
            else:
                inactive_count += 1

    is_healthy = len(manager.plugins) == len(healthy)
    return {
        'status': 'healthy' if is_healthy else 'unhealthy',
        'updated': synse_server.utils.rfc3339now(),
        'healthy': healthy,
        'unhealthy': unhealthy,
        'active': active_count,
        'inactive': inactive_count,
    }
