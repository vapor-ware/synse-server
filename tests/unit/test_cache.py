
import pytest


@pytest.mark.asyncio
async def test_get_transaction_ok():
    pass


@pytest.mark.asyncio
async def test_get_transaction_not_found():
    pass


def test_get_cached_transaction_ids_empty():
    pass


def test_get_cached_transaction_ids_one():
    pass


def test_get_cached_transaction_ids_multiple():
    pass


@pytest.mark.asyncio
async def test_add_transaction_new_transaction():
    pass


@pytest.mark.asyncio
async def test_add_transaction_existing_id():
    pass


@pytest.mark.asyncio
async def test_update_device_cache():
    # todo: may need multiple tests for this on different device
    #   configuration permutations?
    pass


@pytest.mark.asyncio
async def test_get_device_ok():
    pass


@pytest.mark.asyncio
async def test_get_device_not_found():
    pass


@pytest.mark.asyncio
async def test_get_devices_no_devices():
    # todo: parameterize
    pass


@pytest.mark.asyncio
async def test_get_devices_ok():
    # todo: parameterize
    pass


def test_get_cached_device_tags_no_tags():
    pass


def test_get_cached_device_tags_one_tag():
    pass


def test_get_cached_device_tags_multiple_tags():
    pass


@pytest.mark.asyncio
async def test_get_plugin_no_device():
    pass


@pytest.mark.asyncio
async def test_get_plugin_no_plugin():
    pass


@pytest.mark.asyncio
async def test_get_plugin_ok():
    pass
