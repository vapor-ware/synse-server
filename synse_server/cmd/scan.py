
from synse_server import cache
from synse_server.log import logger
from synse_server.i18n import _


async def scan(ns, tags, sort, force=False):
    """Generate the scan response data.

    Args:
        ns (str): The default namespace to use for tags which do not
            specify one. If all tags specify a namespace, or no tags
            are defined, this is ignored.
        tags (list[str]): The tags to filter devices on. If no tags are
            given, no filtering is done.
        force (bool): Option to force rebuild the internal device cache.
            (default: False)
        sort (str): The fields to sort by.

    Returns:
         list[dict]: A list of dictionary representations of device
         summary response(s).
    """

    # If the force flag is set, rebuild the internal device cache. This
    # will ensure everything is up to date, but will ultimately make the
    # request take longer to fulfill.
    if force:
        logger.debug(_('forced scan: rebuilding device cache'))
        await cache.update_device_cache()

    # Apply the default namespace to the tags which do not have any
    # namespaces, if any are defined.
    for i, tag in enumerate(tags):
        if '/' not in tag:
            tags[i] = f'{ns}/{tag}'

    devices = await cache.get_devices(*tags)

    # Sort the devices based on the sort string. There may be multiple
    # components in the sort string separated by commas. The order in which
    # they are listed is equivalent to the order of their sort priority.
    sort_keys = sort.split(',')

    sorted_devices = sorted(
        devices,
        key=lambda dev: tuple(map(lambda key: getattr(dev, key), sort_keys))
    )

    return sorted_devices
