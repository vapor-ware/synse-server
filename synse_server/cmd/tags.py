
from synse_server import cache
from synse_server.i18n import _
from synse_server.log import logger


async def tags(*namespaces, with_id_tags=False):
    """Generate the tags response data.

    Args:
        namespaces (str): The namespace(s) of the tags to filter by.
        with_id_tags (bool): Flag to toggle the inclusion/exclusion of ID tags.

    Returns:
        list[str]: A list of all tags currently associated with devices.
    """
    logger.info(
        _('issuing command'), command='TAGS',
        namespaces=namespaces, with_id=with_id_tags,
    )

    cached_tags = cache.get_cached_device_tags()

    def matches_ns(t):
        if '/' in t:
            ns = t.split('/')[0]
        else:
            ns = 'default'
        return ns in namespaces

    if not with_id_tags:
        logger.debug(_('filtering ID tags'), command='TAGS')
        cached_tags = [t for t in cached_tags if not t.startswith('system/id:')]

    if namespaces:
        logger.debug(_('filtering tags by namespace'), command='TAGS', namespaces=namespaces)
        cached_tags = [t for t in cached_tags if matches_ns(t)]

    logger.debug(_('got tags'), command='TAGS', count=len(cached_tags))
    return sorted(cached_tags)
