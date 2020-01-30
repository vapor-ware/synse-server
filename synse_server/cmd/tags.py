
from typing import List

from structlog import get_logger

from synse_server import cache
from synse_server.i18n import _

logger = get_logger()


async def tags(namespaces: List[str], with_id_tags: bool = False) -> List[str]:
    """Generate the tags response data.

    Args:
        namespaces: The namespace(s) of the tags to filter by.
        with_id_tags: Flag to toggle the inclusion/exclusion of ID tags.

    Returns:
        A list of all tags currently associated with devices.
    """
    logger.info(
        _('issuing command'), command='TAGS',
        namespaces=namespaces, with_id=with_id_tags,
    )

    cached_tags = cache.get_cached_device_tags()

    def matches_ns(t: str) -> bool:
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
