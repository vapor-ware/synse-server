"""Service discovery for plugins using Kubernetes."""

from typing import List

import kubernetes.client
import kubernetes.config
from containerlog import get_logger

from synse_server import config

logger = get_logger()


def discover() -> List[str]:
    """Discover plugins for kubernetes based on the kubernetes service
    discovery configuration(s).

    Returns:
        list[str]: A list of host:port addresses for plugins discovered
            via kubernetes.
    """
    addresses = []

    cfg = config.options.get('plugin.discover.kubernetes')
    if not cfg:
        logger.debug('plugin discovery via Kubernetes is disabled')
        return addresses

    # Currently, everything we want to be able to discover (namely, endpoints)
    # should all be in the same namespace, so we define it globally. If other
    # methods of lookup are added later, we could also have a namespace per
    # resource, e.g. so we can look for endpoints in namespace X and pods in
    # namespace Y, etc.
    #
    # If no namespace is provided via user configuration, if will default to
    # the 'default' namespace.
    ns = config.options.get('plugin.discover.kubernetes.namespace', 'default')
    logger.info('plugin discovery via Kubernetes is enabled', namespace=ns)

    # Currently, we only support plugin discovery via kubernetes service
    # endpoints, under the `plugin.discover.kubernetes.endpoints` config
    # field.
    #
    # We can support other means later.
    endpoints_cfg = cfg.get('endpoints')
    if endpoints_cfg:
        addresses.extend(_register_from_endpoints(ns=ns, cfg=endpoints_cfg))
    else:
        # Since we currently only support endpoint discovery, if Kubernetes
        # discovery is configured, but there are no endpoints, issue a warning,
        # since this smells like a configuration issue.
        logger.warning('found no configured endpoints for plugin discovery via Kubernetes')

    return addresses


def _register_from_endpoints(ns: str, cfg: dict) -> List[str]:
    """Register plugins with Synse Server discovered via kubernetes
    service endpoints.

    Args:
        ns: The namespace to get the endpoints from.
        cfg: The configuration for service discovery via
            kubernetes endpoints.

    Returns:
        A list of host:port addresses for the plugin endpoints which
        match the config.

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
        logger.warning(
            'found no configured labels for plugin discovery via Kubernetes Endpoints',
        )
        return found

    # Each label is specified in the config as a key-value pair. Here, we
    # want to take each pair and join them into the appropriate label selector
    # string. For example,
    #   app: synse
    #   component: plugin
    # would become the selector string: 'app=synse,component=plugin'
    label_selector = ','.join([f'{k}={v}' for k, v in labels.items()])

    # Now, we can create a kubernetes client and search for endpoints with
    # the corresponding config.
    kubernetes.config.load_incluster_config()
    v1 = kubernetes.client.CoreV1Api()

    logger.debug('listing Kubernetes endpoint', namespace=ns, label_selector=label_selector)
    endpoints = v1.list_namespaced_endpoints(namespace=ns, label_selector=label_selector)

    # Now we parse out the endpoints to get the routing info to a plugin.
    # There are some assumptions here:
    #  - The port must have the name 'http'
    for endpoint in endpoints.items:
        name = endpoint.metadata.name
        logger.debug('discovered matching Endpoint', name=name)

        for i, subset in enumerate(endpoint.subsets):
            logger.debug('parsing EndpointSubset')
            ips = []
            port = None

            addresses = subset.addresses
            if not addresses:
                logger.debug('no addresses for EndpointSubset - skipping', name=name, subset=i)
                continue

            # Iterate over all of the addresses. If there are multiple instances of a plugin
            # sitting behind a service, e.g. a DaemonSet or Deployment with replica count > 1,
            # then we will want to reach all of the plugins.
            logger.debug('collecting available addresses for EndpointSubset',
                         name=name, subset=i)
            for address in addresses:
                logger.debug(
                    'parsing EndpointAddress',
                    name=name, hostname=address.hostname, ip=address.ip,
                    node=address.node_name, subset=i,
                )
                ref = address.target_ref
                if ref is None:
                    logger.debug('address has no target_ref - skipping', name=name, subset=i)
                    continue

                kind = ref.kind
                if kind.lower() != 'pod':
                    logger.debug('address is not a Pod address - skipping',
                                 name=name, kind=kind, subset=i)
                    continue

                ips.append(address.ip)

            # If we don't have any IPs yet, there is no point in getting the port for
            # for this subset, so just continue.
            if not ips:
                logger.debug('no IPs found for EndpointSubset - skipping', name=name, subset=i)
                continue

            logger.debug('found IPs for EndpointSubset', ips=ips)

            # Parse the ports. If there is only one port, use that port. Otherwise, use the
            # port named 'http'.
            ports = subset.ports
            if not ports:
                logger.debug('no ports for EndpointSubset - skipping', name=name, subset=i)
                continue

            if len(ports) == 1:
                port = ports[0].port
                logger.debug(
                    'found single port for EndpointSubset',
                    subset=i, name=ports[0].name, protocol=ports[0].protocol, port=port,
                )
            else:
                # Search for a port with name 'http'
                logger.debug('found multiple ports - searching for port named "http"')
                for p in ports:
                    logger.debug('found port', subset=i, name=p.name)
                    if p.name != 'http':
                        logger.debug('skipping port - does not match')
                        continue

                    logger.debug(
                        'found port name "http"',
                        subset=i, name=p.name, port=p.port, protocol=p.protocol,
                    )
                    port = p.port
                    break

            # If we have addresses and we have a port, we can register those endpoints
            # as plugins. Otherwise, we move on.
            if ips and port is not None:
                for ip in ips:
                    logger.info('discovered plugin via Endpoint', name=name, ip=ip, port=port)
                    found.append(f'{ip}:{port}')

    if not found:
        logger.debug('no plugins found via Kubernetes Endpoints', labels=labels)
    else:
        logger.info('found plugins via Kubernetes Endpoints', count=len(found))

    return found
