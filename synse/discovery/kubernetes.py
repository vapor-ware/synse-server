"""Service discovery for plugins using Kubernetes."""

import kubernetes.client
import kubernetes.config

from synse import config
from synse.i18n import _
from synse.log import logger


def discover():
    """Discover plugins for kubernetes based on the kubernetes service
    discovery configuration(s).

    Returns:
        list[str]: A list of host:port addresses for plugins discovered
            via kubernetes.
    """
    cfg = config.options.get('plugin.discover.kubernetes')

    # Currently, we only support plugin discovery via kubernetes service
    # endpoints, under the `plugin.discover.kubernetes.endpoints` config
    # field.
    #
    # We can support other means later.
    addresses = _register_from_endpoints(cfg.get('endpoints'))

    return addresses


def _register_from_endpoints(cfg):
    """Register plugins with Synse Server discovered via kubernetes
    service endpoints.

    Args:
        cfg (dict): The configuration for service discovery via kubernetes
            endpoints.

    Returns:
        list[str]: A list of host:port addresses for the plugin endpoints
            that matched the config.
    """
    found = []

    # Gather the filters/options needed to find the endpoints we are interested
    # in. Currently, the only filtering we support is by labels. If there are
    # no labels specified, then there is no registration to be done here.
    labels = cfg.get('labels')
    if not labels:
        logger.debug(_('No labels found for kubernetes service discovery via endpoints'))
        return found

    # Each label is specified in the config as a key-value pair. Here, we
    # want to take each pair and join them into the appropriate label selector
    # string. For example,
    #   app: synse
    #   component: plugin
    # would become the selector string: 'app=synse,component=plugin'
    label_selector = ','.join(['{}={}'.format(k, v) for k, v in labels.items()])
    logger.debug(_('Using endpoint label selector: {}').format(label_selector))

    # Now, we can create a kubernetes client and search for endpoints with
    # the corresponding config.
    kubernetes.config.load_incluster_config()
    v1 = kubernetes.client.CoreV1Api()

    endpoints = v1.list_endpoints_for_all_namespaces(label_selector=label_selector)

    # Now we parse out the endpoints to get the routing info to a plugin.
    # There are some assumptions here:
    #  - There is only one Pod address for the endpoint (e.g. the first address
    #    in the addresses list that is for kind Pod is used)
    #  - The port must have the name 'http'
    for endpoint in endpoints.items:
        name = endpoint.metadata.name
        logger.debug(_('Found endpoint with name: {}').format(name))

        ip = None
        port = None

        for subset in endpoint.subsets:
            addresses = subset.addresses
            if addresses is None:
                logger.debug(_('No addresses for subset of endpoint - skipping ({})').format(name))
                continue

            for address in addresses:
                ref = address.target_ref
                if ref is None:
                    logger.debug(_('Address has no target_ref - skipping ({})').format(address))
                    continue

                kind = ref.kind
                if kind.lower() != 'pod':
                    logger.debug(_('Address is not a pod address - skipping ({})').format(address))
                    continue

                ip = address.ip
                break

            # If we don't have the IP yet, there is no point in getting the port for
            # for this subset, so just continue.
            if not ip:
                logger.debug(_('No ip found for endpoint, will not search for port'))
                continue

            ports = subset.ports
            if ports is None:
                logger.debug(_('No ports for subset of endpoint - skipping ({})').format(name))
                continue

            for port in ports:
                if port.name != 'http':
                    logger.debug(_('skipping port (want name:http, but found name:{})').format(port.get('name')))
                    continue

                port = port.port
                break

            if ip is not None and port is not None:
                break

        logger.debug(_('endpoint.name={}, ip={}, port={}').format(name, ip, port))
        if ip is None or port is None:
            logger.debug(_('No ip/port found for endpoint {} - skipping').format(name))
            continue

        found.append('{}:{}'.format(ip, port))
    return found
