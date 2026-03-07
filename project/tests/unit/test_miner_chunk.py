"""Tests for miner scene chunk module."""

from unittest.mock import MagicMock

import pytest
from gamepart.subsystem import SystemManager
from scenes.miner.chunk import ResourceChunk, ResourceChunkManager


class TestResourceChunk:
    def test_extends_chunk_with_patches_list(self) -> None:
        chunk = ResourceChunk((1, 2))
        assert chunk.coord == (1, 2)
        assert chunk.patches == []
        assert chunk.objects == []


class TestResourceChunkManagerUpdate:
    """ResourceChunkManager.update() only loads chunks, never unloads."""

    @pytest.fixture
    def mock_system(self) -> MagicMock:
        return MagicMock(spec=SystemManager)

    @pytest.fixture
    def manager(self, mock_system: MagicMock) -> ResourceChunkManager:
        return ResourceChunkManager(mock_system, seed=42, chunk_size=512)

    def test_update_loads_chunks_around_center(
        self, manager: ResourceChunkManager, mock_system: MagicMock
    ) -> None:
        manager.update((0.0, 0.0), rings=1)
        loaded = set(manager._loaded_chunks.keys())
        assert len(loaded) == 9
        assert (0, 0) in loaded
        assert (-1, -1) in loaded
        assert (1, 1) in loaded
        assert mock_system.add_all.call_count == 9

    def test_update_does_not_unload_when_center_moves(
        self, manager: ResourceChunkManager, mock_system: MagicMock
    ) -> None:
        manager.update((0.0, 0.0), rings=1)
        mock_system.reset_mock()
        manager.update((2000.0, 2000.0), rings=1)
        mock_system.remove_all.assert_not_called()
        assert len(manager._loaded_chunks) == 9 + 9

    def test_update_loads_only_missing_chunks(
        self, manager: ResourceChunkManager, mock_system: MagicMock
    ) -> None:
        manager.update((0.0, 0.0), rings=1)
        mock_system.reset_mock()
        manager.update((100.0, 100.0), rings=1)
        assert mock_system.add_all.call_count == 0


class TestResourceChunkManagerGetPatchAt:
    @pytest.fixture
    def mock_system(self) -> MagicMock:
        return MagicMock(spec=SystemManager)

    @pytest.fixture
    def manager(self, mock_system: MagicMock) -> ResourceChunkManager:
        return ResourceChunkManager(mock_system, seed=42, chunk_size=512)

    def test_get_patch_at_returns_none_when_no_chunks_loaded(
        self, manager: ResourceChunkManager
    ) -> None:
        assert manager.get_patch_at((100.0, 100.0)) is None

    def test_get_patch_at_returns_patch_when_point_inside(
        self, manager: ResourceChunkManager
    ) -> None:
        manager.update((0.0, 0.0), rings=1)
        for chunk in manager._loaded_chunks.values():
            for patch in chunk.patches:
                px, py = patch.position
                found = manager.get_patch_at((px, py))
                assert found is patch
                assert found.contains_point((px, py))

    def test_get_patch_at_returns_none_for_point_outside_all_patches(
        self, manager: ResourceChunkManager
    ) -> None:
        manager.update((0.0, 0.0), rings=1)
        result = manager.get_patch_at((-1e6, -1e6))
        assert result is None
