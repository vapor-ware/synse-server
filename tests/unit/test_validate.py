"""Test the 'synse_server.validate' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-argument,line-too-long

import asynctest
import pytest
from synse_grpc import api

from synse_server import cache, errors, validate
from tests import utils


async def make_device_info_response(rack, board, device):
    """Helper method to make a new Device object."""
    await cache._plugins_cache.set(cache.PLUGINS_CACHE_KEY, {device: 'test-plugin'})

    return api.Device(
        timestamp='october',
        uid=device,
        kind='thermistor',
        metadata=dict(
            model='test',
            manufacturer='vapor io',
        ),
        plugin='foo',
        info='bar',
        location=api.Location(
            rack=rack,
            board=board
        ),
        output=[
            api.Output(
                type='temperature',
                precision=3,
                unit=api.Unit(
                    name='celsius',
                    symbol='C'
                )
            )
        ]
    )

# --- Mock Methods ---


async def mock_get_device_info_cache():
    """Mock method for get_device_info_cache - returns a single device."""
    return {
        'rack-1-vec-12345': await make_device_info_response('rack-1', 'vec', '12345')
    }


@pytest.fixture()
def patch_device_info(monkeypatch):
    """Fixture to monkeypatch the get_device_info_cache method."""
    mock = asynctest.CoroutineMock(cache.get_device_info_cache, side_effect=mock_get_device_info_cache)
    monkeypatch.setattr(cache, 'get_device_info_cache', mock)
    return patch_device_info


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'device_type', [
        ['thermistor'],
        ['Thermistor'],
        ['THERMISTOR'],
        ['ThErMiStOr'],
        # multiple types can be permissible for validation
        ['led', 'fan', 'thermistor'],
        ['system', 'THERMISTOR'],
        ['LOCK', 'Thermistor']
    ]
)
async def test_validate_device_type(patch_device_info, clear_caches, device_type):
    """Test successfully validating a device."""
    await validate.validate_device_type(device_type, 'rack-1', 'vec', '12345')


@pytest.mark.asyncio
async def test_validate_device_type_no_device():
    """Test validating a device when the specified device doesn't exist."""
    with pytest.raises(errors.DeviceNotFoundError):
        await validate.validate_device_type(['thermistor'], 'foo', 'bar', 'baz')


@pytest.mark.asyncio
async def test_validate_device_type_no_match(patch_device_info, clear_caches):
    """Test validating a device when the types don't match."""
    with pytest.raises(errors.InvalidDeviceType):
        await validate.validate_device_type(['led'], 'rack-1', 'vec', '12345')


@pytest.mark.asyncio
async def test_validate_device_type_no_match_multiple(patch_device_info, clear_caches):
    """Test validating a device when the types don't match."""
    with pytest.raises(errors.InvalidDeviceType):
        await validate.validate_device_type(['led', 'something'], 'rack-1', 'vec', '12345')


@pytest.mark.parametrize(
    'params,valid,expected', [
        ({}, ['test'], {}),
        ({'test': 'value'}, ['test'], {'test': 'value'}),
        ({'test': 'value'}, ['test', 'other'], {'test': 'value'}),
        ({'test': 'value', 'other': 1}, ['test', 'other'], {'test': 'value', 'other': 1}),
    ]
)
def test_validate_query_params(params, valid, expected):
    """Test validating query parameters successfully."""
    assert validate.validate_query_params(params, *valid) == expected


@pytest.mark.parametrize(
    'params,valid', [
        ({'test': 'value'}, ['other']),
        ({'test': 'value', 'other': 1}, ['other']),
        ({'a': 1, 'b': 2, 'c': 3}, ['a', 'b', 'd']),
    ]
)
def test_validate_query_params_invalid(params, valid):
    """Test validating query parameters when invalid parameters are given."""
    with pytest.raises(errors.InvalidArgumentsError):
        validate.validate_query_params(params, *valid)


@pytest.mark.asyncio
async def test_validate_no_query_params():
    """Test validating that an incoming request has no query params, when there
    are no query params.
    """

    @validate.no_query_params()
    async def test_fn(request, *args, **kwargs):
        """Dummy function for testing the decorator."""
        return request

    await test_fn(utils.make_request('/synse/endpoint'))


@pytest.mark.asyncio
async def test_validate_no_query_params2():
    """Test validating that an incoming request has no query params, when there
    are query params. In this case, we expect an error.
    """

    @validate.no_query_params()
    async def test_fn(request, *args, **kwargs):
        """Dummy function for testing the decorator."""
        return request

    with pytest.raises(errors.InvalidArgumentsError):
        await test_fn(utils.make_request('/synse/endpoint?test=param'))
