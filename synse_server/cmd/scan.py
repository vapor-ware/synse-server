
from synse_grpc import utils

from synse_server import cache, errors
from synse_server.i18n import _
from synse_server.log import logger


async def scan(ns, tag_groups, sort, force=False):
    """Generate the scan response data.

    Args:
        ns (str): The default namespace to use for tags which do not
            specify one. If all tags specify a namespace, or no tags
            are defined, this is ignored.
        tag_groups (list[iterable[string]]): The tags groups used to filter
            devices. If no tag groups are given (and thus no tags), no
            filtering is done.
        force (bool): Option to force rebuild the internal device cache.
            (default: False)
        sort (str): The fields to sort by.

    Returns:
         list[dict]: A list of dictionary representations of device
         summary response(s).
    """
    logger.info(
        _('issuing command'), command='SCAN',
        ns=ns, tag_groups=tag_groups, sort=sort, force=force,
    )

    # If the force flag is set, rebuild the internal device cache. This
    # will ensure everything is up to date, but will ultimately make the
    # request take longer to fulfill.
    if force:
        logger.debug(_('forced scan: rebuilding device cache'), command='SCAN')
        try:
            await cache.update_device_cache()
        except Exception as e:
            raise errors.ServerError(_('failed to rebuild device cache')) from e

    # If no tags are specified, get devices with no tag filter.
    if len(tag_groups) == 0:
        logger.debug(_('getting devices with no tag filter'), command='SCAN')
        try:
            devices = await cache.get_devices()
        except Exception as e:
            logger.exception(e)
            raise errors.ServerError(_('failed to get all devices from cache')) from e

    else:
        # Otherwise, there is at least one tag group. We need to get the devices for
        # each tag group and collect the results of each group.
        results = {}
        logger.debug(_('parsing tag groups'), command='SCAN')
        for group in tag_groups:
            # Apply the default namespace to the tags in the group which do not
            # have any namespace defined.
            for i, tag in enumerate(group):
                if '/' not in tag:
                    group[i] = f'{ns}/{tag}'

            try:
                device_group = await cache.get_devices(*group)
            except Exception as e:
                logger.exception(e)
                raise errors.ServerError(_('failed to get devices from cache')) from e

            for device in device_group:
                results[device.id] = device

        devices = list(results.values())

    # Sort the devices based on the sort string. There may be multiple
    # components in the sort string separated by commas. The order in which
    # they are listed is equivalent to the order of their sort priority.
    sort_keys = sort.split(',')

    try:
        logger.debug(_('sorting devices'), command='SCAN')
        sorted_devices = sorted(
            devices,
            key=lambda dev: tuple(map(lambda key: getattr(dev, key), sort_keys))
        )
    except AttributeError as e:
        raise errors.InvalidUsage('invalid sort key(s) provided') from e

    response = []
    for device in sorted_devices:
        response.append({
            'id': device.id,
            'alias': device.alias,
            'info': device.info,
            'type': device.type,
            'plugin': device.plugin,
            'tags': [utils.tag_string(tag) for tag in device.tags],
            'metadata': dict(device.metadata),
        })
    logger.debug(_('got devices'), count=len(response), command='SCAN')
    return response
