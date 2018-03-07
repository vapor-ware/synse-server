"""Test the 'synse.validate' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-argument,line-too-long

import asynctest
import pytest
from synse_plugin import api

from synse import cache, errors, validate


async def make_metainfo_response(rack, board, device):
    """Helper method to make a new MetainfoResponse object."""
    await cache._plugins_cache.set(cache.PLUGINS_CACHE_KEY, {device: 'test-plugin'})

    return api.MetainfoResponse(
        timestamp='october',
        uid=device,
        type='thermistor',
        model='test',
        manufacturer='vapor io',
        protocol='foo',
        info='bar',
        location=api.MetaLocation(
            rack=rack,
            board=board
        ),
        output=[
            api.MetaOutput(
                type='temperature',
                data_type='float',
                precision=3,
                unit=api.MetaOutputUnit(
                    name='celsius',
                    symbol='C'
                ),
                range=api.MetaOutputRange(
                    min=0,
                    max=100
                )
            )
        ]
    )

# --- Mock Methods ---


async def mock_get_metainfo_cache():
    """Mock method for get_metainfo_cache - returns a single device."""
    return {
        'rack-1-vec-12345': await make_metainfo_response('rack-1', 'vec', '12345')
    }


@pytest.fixture()
def patch_metainfo(monkeypatch):
    """Fixture to monkeypatch the get_metainfo_cache method."""
    mock = asynctest.CoroutineMock(cache.get_metainfo_cache, side_effect=mock_get_metainfo_cache)
    monkeypatch.setattr(cache, 'get_metainfo_cache', mock)
    return patch_metainfo


@pytest.mark.asyncio
async def test_validate_device_type(patch_metainfo, clear_caches):
    """Test successfully validating a device."""
    cases = [
        'thermistor',
        'Thermistor',
        'THERMISTOR'
    ]

    for case in cases:
        await validate.validate_device_type(case, 'rack-1', 'vec', '12345')


@pytest.mark.asyncio
async def test_validate_device_type_no_device():
    """Test validating a device when the specified device doesn't exist."""
    with pytest.raises(errors.DeviceNotFoundError):
        await validate.validate_device_type('thermistor', 'foo', 'bar', 'baz')


@pytest.mark.asyncio
async def test_validate_device_type_no_match(patch_metainfo, clear_caches):
    """Test validating a device when the types don't match."""
    with pytest.raises(errors.InvalidDeviceType):
        await validate.validate_device_type('led', 'rack-1', 'vec', '12345')
