"""Test the 'synse.discovery.kubernetes' Synse Server module."""
# pylint: disable=unused-argument,missing-docstring

import kubernetes
import pytest

from synse import config
from synse.discovery import kubernetes as k8s


def test_discover_no_cfg():
    """Test discovery when it is not configured."""

    res = k8s.discover()
    assert res == []


def test_discovery_empty_endpoints():
    """Test discovery when nothing is set for the endpoints config."""

    config.options.set('plugin.discover.kubernetes.endpoints', {})
    res = k8s.discover()
    assert res == []


def test_register_from_endpoints_no_ns():
    """An empty namespace string is provided to the _register_from_endpoints function."""

    with pytest.raises(ValueError):
        k8s._register_from_endpoints('', {})


def test_register_from_endpoints_empty_cfg():
    """Pass an empty config to _register_from_endpoints."""

    res = k8s._register_from_endpoints(
        ns='default',
        cfg={}
    )
    assert res == []


def test_no_endpoints():
    """The specified labels result in no endpoints being found."""

    # mock out the 'load incluster config' fn so it does nothing
    k8s.kubernetes.config.load_incluster_config = lambda: None

    # mock out the CoreV1Api object's list_namespaced_endpoints
    # to return no endpoints.
    class MockCoreV1Api:
        def list_namespaced_endpoints(self, *args, **kwargs):
            return kubernetes.client.V1EndpointsList(items=[])
    k8s.kubernetes.client.CoreV1Api = MockCoreV1Api

    res = k8s._register_from_endpoints(
        ns='default',
        cfg={'labels': {'foo': 'bar'}}
    )
    assert res == []


def test_one_endpoint_no_subsets():
    """The endpoint contains no subsets."""

    # mock out the 'load incluster config' fn so it does nothing
    k8s.kubernetes.config.load_incluster_config = lambda: None

    # mock out the CoreV1Api object's list_namespaced_endpoints
    # to return no endpoints.
    class MockCoreV1Api:
        def list_namespaced_endpoints(self, *args, **kwargs):
            return kubernetes.client.V1EndpointsList(items=[
                kubernetes.client.V1Endpoints(
                    metadata=kubernetes.client.V1ObjectMeta(
                        name='test-ep'
                    ),
                    subsets=[]
                )
            ])

    k8s.kubernetes.client.CoreV1Api = MockCoreV1Api

    res = k8s._register_from_endpoints(
        ns='default',
        cfg={'labels': {'foo': 'bar'}}
    )
    assert res == []


def test_one_endpoint_no_addresses():
    """The endpoint has a single subset with no addresses."""

    # mock out the 'load incluster config' fn so it does nothing
    k8s.kubernetes.config.load_incluster_config = lambda: None

    # mock out the CoreV1Api object's list_namespaced_endpoints
    # to return no endpoints.
    class MockCoreV1Api:
        def list_namespaced_endpoints(self, *args, **kwargs):
            return kubernetes.client.V1EndpointsList(items=[
                kubernetes.client.V1Endpoints(
                    metadata=kubernetes.client.V1ObjectMeta(
                        name='test-ep'
                    ),
                    subsets=[
                        kubernetes.client.V1EndpointSubset(
                            addresses=[],
                            ports=[
                                kubernetes.client.V1EndpointPort(
                                    name='foo',
                                    port=7766,
                                    protocol='TCP'
                                )
                            ]
                        )
                    ]
                )
            ])

    k8s.kubernetes.client.CoreV1Api = MockCoreV1Api

    res = k8s._register_from_endpoints(
        ns='default',
        cfg={'labels': {'foo': 'bar'}}
    )
    assert res == []


def test_one_endpoint_no_ports():
    """The endpoint has a single subset with address but no port."""

    # mock out the 'load incluster config' fn so it does nothing
    k8s.kubernetes.config.load_incluster_config = lambda: None

    # mock out the CoreV1Api object's list_namespaced_endpoints
    # to return no endpoints.
    class MockCoreV1Api:
        def list_namespaced_endpoints(self, *args, **kwargs):
            return kubernetes.client.V1EndpointsList(items=[
                kubernetes.client.V1Endpoints(
                    metadata=kubernetes.client.V1ObjectMeta(
                        name='test-ep'
                    ),
                    subsets=[
                        kubernetes.client.V1EndpointSubset(
                            addresses=[
                                kubernetes.client.V1EndpointAddress(
                                    hostname='foobar',
                                    ip='127.0.0.1',
                                    node_name='test',
                                    target_ref=kubernetes.client.V1ObjectReference(
                                        kind='Pod',
                                        name='test-pod',
                                        namespace='default'
                                    )
                                )
                            ],
                            ports=[]
                        )
                    ]
                )
            ])

    k8s.kubernetes.client.CoreV1Api = MockCoreV1Api

    res = k8s._register_from_endpoints(
        ns='default',
        cfg={'labels': {'foo': 'bar'}}
    )
    assert res == []


def test_endpoint_no_addr_match():
    """The endpoint address does not match the criteria (pod, with target_ref)"""

    # mock out the 'load incluster config' fn so it does nothing
    k8s.kubernetes.config.load_incluster_config = lambda: None

    # mock out the CoreV1Api object's list_namespaced_endpoints
    # to return no endpoints.
    class MockCoreV1Api:
        def list_namespaced_endpoints(self, *args, **kwargs):
            return kubernetes.client.V1EndpointsList(items=[
                kubernetes.client.V1Endpoints(
                    metadata=kubernetes.client.V1ObjectMeta(
                        name='test-ep'
                    ),
                    subsets=[
                        kubernetes.client.V1EndpointSubset(
                            addresses=[
                                kubernetes.client.V1EndpointAddress(
                                    hostname='foobar',
                                    ip='127.0.0.1',
                                    node_name='test',
                                    target_ref=kubernetes.client.V1ObjectReference(
                                        kind='Service',
                                        name='test-service',
                                        namespace='default'
                                    )
                                )
                            ],
                            ports=[
                                kubernetes.client.V1EndpointPort(
                                    name='foo',
                                    port=7766,
                                    protocol='TCP'
                                )
                            ]
                        )
                    ]
                )
            ])

    k8s.kubernetes.client.CoreV1Api = MockCoreV1Api

    res = k8s._register_from_endpoints(
        ns='default',
        cfg={'labels': {'foo': 'bar'}}
    )
    assert res == []


def test_one_endpoint():
    """Endpoint has one subset with address and port."""

    # mock out the 'load incluster config' fn so it does nothing
    k8s.kubernetes.config.load_incluster_config = lambda: None

    # mock out the CoreV1Api object's list_namespaced_endpoints
    # to return no endpoints.
    class MockCoreV1Api:
        def list_namespaced_endpoints(self, *args, **kwargs):
            return kubernetes.client.V1EndpointsList(items=[
                kubernetes.client.V1Endpoints(
                    metadata=kubernetes.client.V1ObjectMeta(
                        name='test-ep'
                    ),
                    subsets=[
                        kubernetes.client.V1EndpointSubset(
                            addresses=[
                                kubernetes.client.V1EndpointAddress(
                                    hostname='foobar',
                                    ip='127.0.0.1',
                                    node_name='test',
                                    target_ref=kubernetes.client.V1ObjectReference(
                                        kind='Pod',
                                        name='test-pod',
                                        namespace='default'
                                    )
                                )
                            ],
                            ports=[
                                kubernetes.client.V1EndpointPort(
                                    name='foo',
                                    port=7766,
                                    protocol='TCP'
                                )
                            ]
                        )
                    ]
                )
            ])

    k8s.kubernetes.client.CoreV1Api = MockCoreV1Api

    res = k8s._register_from_endpoints(
        ns='default',
        cfg={'labels': {'foo': 'bar'}}
    )
    assert res == ['127.0.0.1:7766']


def test_one_endpoint_multiple_ports_ok():
    """Endpoint has multiple ports, one of which has the name 'http'."""

    # mock out the 'load incluster config' fn so it does nothing
    k8s.kubernetes.config.load_incluster_config = lambda: None

    # mock out the CoreV1Api object's list_namespaced_endpoints
    # to return no endpoints.
    class MockCoreV1Api:
        def list_namespaced_endpoints(self, *args, **kwargs):
            return kubernetes.client.V1EndpointsList(items=[
                kubernetes.client.V1Endpoints(
                    metadata=kubernetes.client.V1ObjectMeta(
                        name='test-ep'
                    ),
                    subsets=[
                        kubernetes.client.V1EndpointSubset(
                            addresses=[
                                kubernetes.client.V1EndpointAddress(
                                    hostname='foobar',
                                    ip='127.0.0.1',
                                    node_name='test',
                                    target_ref=kubernetes.client.V1ObjectReference(
                                        kind='Pod',
                                        name='test-pod',
                                        namespace='default'
                                    )
                                )
                            ],
                            ports=[
                                kubernetes.client.V1EndpointPort(
                                    name='http',
                                    port=7788,
                                    protocol='TCP'
                                ),
                                kubernetes.client.V1EndpointPort(
                                    name='bar',
                                    port=4321,
                                    protocol='TCP'
                                )
                            ]
                        )
                    ]
                )
            ])

    k8s.kubernetes.client.CoreV1Api = MockCoreV1Api

    res = k8s._register_from_endpoints(
        ns='default',
        cfg={'labels': {'foo': 'bar'}}
    )
    assert res == ['127.0.0.1:7788']


def test_one_endpoint_multiple_ports_invalid():
    """Endpoint has multiple ports, none of which has the name 'http'."""

    # mock out the 'load incluster config' fn so it does nothing
    k8s.kubernetes.config.load_incluster_config = lambda: None

    # mock out the CoreV1Api object's list_namespaced_endpoints
    # to return no endpoints.
    class MockCoreV1Api:
        def list_namespaced_endpoints(self, *args, **kwargs):
            return kubernetes.client.V1EndpointsList(items=[
                kubernetes.client.V1Endpoints(
                    metadata=kubernetes.client.V1ObjectMeta(
                        name='test-ep'
                    ),
                    subsets=[
                        kubernetes.client.V1EndpointSubset(
                            addresses=[
                                kubernetes.client.V1EndpointAddress(
                                    hostname='foobar',
                                    ip='127.0.0.1',
                                    node_name='test',
                                    target_ref=kubernetes.client.V1ObjectReference(
                                        kind='Pod',
                                        name='test-pod',
                                        namespace='default'
                                    )
                                )
                            ],
                            ports=[
                                kubernetes.client.V1EndpointPort(
                                    name='foo',
                                    port=7788,
                                    protocol='TCP'
                                ),
                                kubernetes.client.V1EndpointPort(
                                    name='bar',
                                    port=4321,
                                    protocol='TCP'
                                )
                            ]
                        )
                    ]
                )
            ])

    k8s.kubernetes.client.CoreV1Api = MockCoreV1Api

    res = k8s._register_from_endpoints(
        ns='default',
        cfg={'labels': {'foo': 'bar'}}
    )
    assert res == []


def test_one_endpoint_multiple_addrs():
    """Endpoint has multiple addresses, some ok, others not what we are looking
    for, and a single port.
    """

    # mock out the 'load incluster config' fn so it does nothing
    k8s.kubernetes.config.load_incluster_config = lambda: None

    # mock out the CoreV1Api object's list_namespaced_endpoints
    # to return no endpoints.
    class MockCoreV1Api:
        def list_namespaced_endpoints(self, *args, **kwargs):
            return kubernetes.client.V1EndpointsList(items=[
                kubernetes.client.V1Endpoints(
                    metadata=kubernetes.client.V1ObjectMeta(
                        name='test-ep'
                    ),
                    subsets=[
                        kubernetes.client.V1EndpointSubset(
                            addresses=[
                                # ok
                                kubernetes.client.V1EndpointAddress(
                                    hostname='foobar',
                                    ip='127.0.0.1',
                                    node_name='test',
                                    target_ref=kubernetes.client.V1ObjectReference(
                                        kind='Pod',
                                        name='test-pod',
                                        namespace='default'
                                    )
                                ),
                                # no target_ref
                                kubernetes.client.V1EndpointAddress(
                                    hostname='foobar',
                                    ip='127.0.0.2',
                                    node_name='test'
                                ),
                                # not a pod
                                kubernetes.client.V1EndpointAddress(
                                    hostname='foobar',
                                    ip='127.0.0.3',
                                    node_name='test',
                                    target_ref=kubernetes.client.V1ObjectReference(
                                        kind='Service',
                                        name='test-service',
                                        namespace='default'
                                    )
                                ),
                                # ok
                                kubernetes.client.V1EndpointAddress(
                                    hostname='foobar',
                                    ip='127.0.0.4',
                                    node_name='test',
                                    target_ref=kubernetes.client.V1ObjectReference(
                                        kind='Pod',
                                        name='test-pod',
                                        namespace='default'
                                    )
                                )
                            ],
                            ports=[
                                kubernetes.client.V1EndpointPort(
                                    name='foo',
                                    port=7766,
                                    protocol='TCP'
                                )
                            ]
                        )
                    ]
                )
            ])

    k8s.kubernetes.client.CoreV1Api = MockCoreV1Api

    res = k8s._register_from_endpoints(
        ns='default',
        cfg={'labels': {'foo': 'bar'}}
    )
    assert res == ['127.0.0.1:7766', '127.0.0.4:7766']


def test_one_endpoint_multiple_subsets():
    """One endpoint with multiple valid subsets."""

    # mock out the 'load incluster config' fn so it does nothing
    k8s.kubernetes.config.load_incluster_config = lambda: None

    # mock out the CoreV1Api object's list_namespaced_endpoints
    # to return no endpoints.
    class MockCoreV1Api:
        def list_namespaced_endpoints(self, *args, **kwargs):
            return kubernetes.client.V1EndpointsList(items=[
                kubernetes.client.V1Endpoints(
                    metadata=kubernetes.client.V1ObjectMeta(
                        name='test-ep'
                    ),
                    subsets=[
                        kubernetes.client.V1EndpointSubset(
                            addresses=[
                                kubernetes.client.V1EndpointAddress(
                                    hostname='foobar',
                                    ip='127.0.0.1',
                                    node_name='test',
                                    target_ref=kubernetes.client.V1ObjectReference(
                                        kind='Pod',
                                        name='test-pod',
                                        namespace='default'
                                    )
                                )
                            ],
                            ports=[
                                kubernetes.client.V1EndpointPort(
                                    name='foo',
                                    port=7766,
                                    protocol='TCP'
                                )
                            ]
                        ),
                        kubernetes.client.V1EndpointSubset(
                            addresses=[
                                kubernetes.client.V1EndpointAddress(
                                    hostname='foobar',
                                    ip='129.0.0.1',
                                    node_name='test',
                                    target_ref=kubernetes.client.V1ObjectReference(
                                        kind='Pod',
                                        name='test-pod',
                                        namespace='default'
                                    )
                                )
                            ],
                            ports=[
                                kubernetes.client.V1EndpointPort(
                                    name='bar',
                                    port=7799,
                                    protocol='TCP'
                                )
                            ]
                        )
                    ]
                )
            ])

    k8s.kubernetes.client.CoreV1Api = MockCoreV1Api

    res = k8s._register_from_endpoints(
        ns='default',
        cfg={'labels': {'foo': 'bar'}}
    )
    assert res == ['127.0.0.1:7766', '129.0.0.1:7799']


def test_multiple_endpoints():
    """Multiple valid endpoints."""

    # mock out the 'load incluster config' fn so it does nothing
    k8s.kubernetes.config.load_incluster_config = lambda: None

    # mock out the CoreV1Api object's list_namespaced_endpoints
    # to return no endpoints.
    class MockCoreV1Api:
        def list_namespaced_endpoints(self, *args, **kwargs):
            return kubernetes.client.V1EndpointsList(items=[
                kubernetes.client.V1Endpoints(
                    metadata=kubernetes.client.V1ObjectMeta(
                        name='test-ep1'
                    ),
                    subsets=[
                        kubernetes.client.V1EndpointSubset(
                            addresses=[
                                kubernetes.client.V1EndpointAddress(
                                    hostname='foobar',
                                    ip='127.0.0.1',
                                    node_name='test',
                                    target_ref=kubernetes.client.V1ObjectReference(
                                        kind='Pod',
                                        name='test-pod',
                                        namespace='default'
                                    )
                                )
                            ],
                            ports=[
                                kubernetes.client.V1EndpointPort(
                                    name='foo',
                                    port=7766,
                                    protocol='TCP'
                                )
                            ]
                        )
                    ]
                ),
                kubernetes.client.V1Endpoints(
                    metadata=kubernetes.client.V1ObjectMeta(
                        name='test-ep2'
                    ),
                    subsets=[
                        kubernetes.client.V1EndpointSubset(
                            addresses=[
                                kubernetes.client.V1EndpointAddress(
                                    hostname='foobar',
                                    ip='128.0.0.1',
                                    node_name='test',
                                    target_ref=kubernetes.client.V1ObjectReference(
                                        kind='Pod',
                                        name='test-pod',
                                        namespace='default'
                                    )
                                )
                            ],
                            ports=[
                                kubernetes.client.V1EndpointPort(
                                    name='foo',
                                    port=7755,
                                    protocol='TCP'
                                )
                            ]
                        )
                    ]
                )
            ])

    k8s.kubernetes.client.CoreV1Api = MockCoreV1Api

    res = k8s._register_from_endpoints(
        ns='default',
        cfg={'labels': {'foo': 'bar'}}
    )
    assert res == ['127.0.0.1:7766', '128.0.0.1:7755']
