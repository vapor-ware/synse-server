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
    addresses = []

    cfg = config.options.get('plugin.discover.kubernetes')
    if not cfg:
        return addresses

    # Currently, everything we want to be able to discover (namely, endpoints)
    # should all be in the same namespace, so we define it globally. If other
    # methods of lookup are added later, we could also have a namespace per
    # resource, e.g. so we can look for endpoints in namespace X and pods in
    # namespace Y, etc.
    #
    # If no namespace is provided via user configuration, if will default to
    # the 'default' namespace.
    ns = config.options.get('plugin.discover.kubernetes.namespace')
    if not ns:
        ns = 'default'
    logger.debug(_('Using namespace "{}" for k8s discovery').format(ns))

    # Currently, we only support plugin discovery via kubernetes service
    # endpoints, under the `plugin.discover.kubernetes.endpoints` config
    # field.
    #
    # We can support other means later.
    endpoints_cfg = cfg.get('endpoints')
    if endpoints_cfg:
        addresses.extend(_register_from_endpoints(ns=ns, cfg=endpoints_cfg))

    return addresses


def _register_from_endpoints(ns, cfg):
    """Register plugins with Synse Server discovered via kubernetes
    service endpoints.

    Args:
        ns (str): The namespace to get the endpoints from.
        cfg (dict): The configuration for service discovery via
            kubernetes endpoints.

    Returns:
        list[str]: A list of host:port addresses for the plugin endpoints
            that matched the config.

    Raises:
        ValueError: The given namespace is empty.
    """
    if not ns:
        raise ValueError(
            'A namespace must be provided for discovery via k8s service endpoints.'
        )

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

    endpoints = v1.list_namespaced_endpoints(namespace=ns, label_selector=label_selector)

    # Now we parse out the endpoints to get the routing info to a plugin.
    # There are some assumptions here:
    #  - The port must have the name 'http'
    for endpoint in endpoints.items:
        name = endpoint.metadata.name
        logger.debug(_('Found endpoint with name: {}').format(name))

        for subset in endpoint.subsets:
            ips = []
            port = None

            addresses = subset.addresses
            if not addresses:
                logger.debug(_('No addresses for subset of endpoint - skipping ({})').format(name))
                continue

            # Iterate over all of the addresses. If there are multiple instances of a plugin
            # sitting behind a service, e.g. a DaemonSet or Deployment with replica count > 1,
            # then we will want to reach all of the plugins.
            for address in addresses:
                ref = address.target_ref
                if ref is None:
                    logger.debug(_('Address has no target_ref - skipping ({})').format(address))
                    continue

                kind = ref.kind
                if kind.lower() != 'pod':
                    logger.debug(_('Address is not a pod address - skipping ({})').format(address))
                    continue

                ips.append(address.ip)

            # If we don't have any IPs yet, there is no point in getting the port for
            # for this subset, so just continue.
            if not ips:
                logger.debug(_('No ips found for endpoint, will not search for port'))
                continue

            # Parse the ports. If there is only one port, use that port. Otherwise, use the
            # port named 'http'.
            ports = subset.ports
            if not ports:
                logger.debug(_('No ports for subset of endpoint - skipping ({})').format(name))
                continue

            if len(ports) == 1:
                port = ports[0].port
            else:
                # Search for a port with name 'http'
                for p in ports:
                    if p.name != 'http':
                        logger.debug(
                            _('skipping port (want name:http, but found name:{})')
                            .format(p.name)
                        )
                        continue

                    port = p.port
                    break

            # If we have addresses and we have a port, we can register those endpoints
            # as plugins. Otherwise, we move on.
            if ips and port is not None:
                for ip in ips:
                    logger.debug(_('found plugin: endpoint.name={}, ip={}, port={}').format(
                        name, ip, port
                    ))
                    found.append('{}:{}'.format(ip, port))

    if not found:
        logger.debug(
            _('Did not find any plugins via kubernetes endpoints (labels={})').format(labels)
        )
    return found
