
from synse_grpc import utils

import synse_server.plugin
import synse_server.utils


async def plugin(plugin_id):
    """Generate the plugin response data.

    Args:
        plugin_id (str): The ID of the plugin to get information for.

    Returns:
        dict: A dictionary representation of the plugin response.
    """
    p = synse_server.plugin.manager.get(plugin_id)
    if p is None:
        # FIXME
        raise ValueError

    # todo: exception handling
    health = p.client.health()

    response = {
        **p.metadata,
        'active': True,
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
    active_count = 0
    inactive_count = 0
    healthy = []
    unhealthy = []

    for p in synse_server.plugin.manager:
        # todo: exception handling - exception would be inactive
        health = p.client.health()
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
