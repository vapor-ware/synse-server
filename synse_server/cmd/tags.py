
from synse_server import cache


async def tags(*namespaces, with_id_tags=False):
    """Generate the tags response data.

    Args:
        namespaces (list[string]): The namespace(s) of the tags to filter by.
        with_id_tags (bool): Flag to toggle the inclusion/exclusion of ID tags.

    Returns:
        list[string]: A list of all tags currently associated with devices.
    """
    cached_tags = list(cache.device_cache._cache.keys())

    def matches_ns(t):
        if '/' in t:
            ns = t.split('/')[0]
        else:
            ns = 'default'
        return ns in namespaces

    if not with_id_tags:
        cached_tags = filter(lambda t: t.startswith('system/id:'), cached_tags)

    if namespaces:
        cached_tags = filter(lambda t: matches_ns(t), cached_tags)

    return list(cached_tags)
