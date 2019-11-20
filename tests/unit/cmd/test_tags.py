
import pytest

from synse_server import cmd


@pytest.mark.asyncio
async def test_tags_failed_get_cached_tags(mocker):
    # Mock test data
    mock_get = mocker.patch(
        'synse_server.cache.get_cached_device_tags',
        side_effect=ValueError(),
    )

    # --- Test case -----------------------------
    with pytest.raises(ValueError):
        await cmd.tags(['default'])

    mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_tags_matches_tag_with_single_ns(mocker):
    # Mock test data
    mock_get = mocker.patch(
        'synse_server.cache.get_cached_device_tags',
        return_value=[
            'default/foo',
            'default/annotation:bar',
            'test/foo',
            'test/annotation:bar',
            'foo',
            'annotation:bar',
            'system/id:1',
            'system/id:2',
            'system/id:3',
            'system/type:temperature',
            'z/123',
        ],
    )

    # --- Test case -----------------------------
    resp = await cmd.tags(['default'])
    assert resp == [
        'annotation:bar',
        'default/annotation:bar',
        'default/foo',
        'foo',
    ]

    mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_tags_matches_tag_with_multiple_ns(mocker):
    # Mock test data
    mock_get = mocker.patch(
        'synse_server.cache.get_cached_device_tags',
        return_value=[
            'default/foo',
            'default/annotation:bar',
            'test/foo',
            'test/annotation:bar',
            'foo',
            'annotation:bar',
            'system/id:1',
            'system/id:2',
            'system/id:3',
            'system/type:temperature',
            'z/123',
        ],
    )

    # --- Test case -----------------------------
    resp = await cmd.tags(['default', 'test'])
    assert resp == [
        'annotation:bar',
        'default/annotation:bar',
        'default/foo',
        'foo',
        'test/annotation:bar',
        'test/foo',
    ]

    mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_tags_matches_tag_no_ns(mocker):
    # Mock test data
    mock_get = mocker.patch(
        'synse_server.cache.get_cached_device_tags',
        return_value=[
            'default/foo',
            'default/annotation:bar',
            'test/foo',
            'test/annotation:bar',
            'foo',
            'annotation:bar',
            'system/id:1',
            'system/id:2',
            'system/id:3',
            'system/type:temperature',
            'z/123',
        ],
    )

    # --- Test case -----------------------------
    resp = await cmd.tags([])
    assert resp == [
        'annotation:bar',
        'default/annotation:bar',
        'default/foo',
        'foo',
        'system/type:temperature',
        'test/annotation:bar',
        'test/foo',
        'z/123',
    ]

    mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_tags_with_id_tags_all_tags_matching_ns(mocker):
    # Mock test data
    mock_get = mocker.patch(
        'synse_server.cache.get_cached_device_tags',
        return_value=[
            'default/foo',
            'default/annotation:bar',
            'test/foo',
            'test/annotation:bar',
            'foo',
            'annotation:bar',
            'system/id:1',
            'system/id:2',
            'system/id:3',
            'system/type:temperature',
            'z/123',
        ],
    )

    # --- Test case -----------------------------
    resp = await cmd.tags([], with_id_tags=True)
    assert resp == [
        'annotation:bar',
        'default/annotation:bar',
        'default/foo',
        'foo',
        'system/id:1',
        'system/id:2',
        'system/id:3',
        'system/type:temperature',
        'test/annotation:bar',
        'test/foo',
        'z/123',
    ]

    mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_tags_with_id_tags_some_tags_matching_ns(mocker):
    # Mock test data
    mock_get = mocker.patch(
        'synse_server.cache.get_cached_device_tags',
        return_value=[
            'default/foo',
            'default/annotation:bar',
            'test/foo',
            'test/annotation:bar',
            'foo',
            'annotation:bar',
            'system/id:1',
            'system/id:2',
            'system/id:3',
            'system/type:temperature',
            'z/123',
        ],
    )

    # --- Test case -----------------------------
    resp = await cmd.tags(['default', 'system'], with_id_tags=True)
    assert resp == [
        'annotation:bar',
        'default/annotation:bar',
        'default/foo',
        'foo',
        'system/id:1',
        'system/id:2',
        'system/id:3',
        'system/type:temperature',
    ]

    mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_tags_with_id_tags_no_tags_matching_ns(mocker):
    # Mock test data
    mock_get = mocker.patch(
        'synse_server.cache.get_cached_device_tags',
        return_value=[
            'default/foo',
            'default/annotation:bar',
            'test/foo',
            'test/annotation:bar',
            'foo',
            'annotation:bar',
            'system/id:1',
            'system/id:2',
            'system/id:3',
            'system/type:temperature',
            'z/123',
        ],
    )

    # --- Test case -----------------------------
    resp = await cmd.tags(['no-such-namespace'], with_id_tags=True)
    assert resp == []

    mock_get.assert_called_once()
