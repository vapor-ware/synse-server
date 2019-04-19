"""Test the 'synse_server.scheme.plugins' Synse Server module."""

from synse_server.scheme.plugins import PluginsResponse


def test_plugins_scheme():
    """Test that the plugins scheme matches the expected."""
    mock_plugins = [
        {
            'name': 'foo',
            'network': 'unix',
            'address': '/tmp/foo'
        }
    ]
    response_scheme = PluginsResponse(data=mock_plugins)

    assert len(response_scheme.data) == 1

    assert 'name' in response_scheme.data[0]
    assert 'network' in response_scheme.data[0]
    assert 'address' in response_scheme.data[0]

    assert response_scheme.data[0]['name'] == 'foo'
    assert response_scheme.data[0]['network'] == 'unix'
    assert response_scheme.data[0]['address'] == '/tmp/foo'
