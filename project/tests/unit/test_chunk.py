from unittest.mock import MagicMock

import pytest
from gamepart.chunk import Chunk, ChunkManager


class SimpleChunkManager(ChunkManager[Chunk]):
    """Concrete implementation for testing."""

    def _load_chunk(self, coord: tuple[int, int]) -> Chunk:
        return Chunk(coord)


class TestChunk:
    def test_chunk_creation(self) -> None:
        chunk = Chunk((0, 0))
        assert chunk.coord == (0, 0)
        assert chunk.objects == []

    def test_chunk_with_objects(self) -> None:
        chunk = Chunk((1, 2))
        chunk.objects.append(MagicMock())
        chunk.objects.append(MagicMock())
        assert len(chunk.objects) == 2


class TestChunkManagerCoordinates:
    @pytest.fixture
    def manager(self) -> SimpleChunkManager:
        mock_system = MagicMock()
        return SimpleChunkManager(mock_system, chunk_size=1000)

    def test_get_chunk_coord_origin(self, manager: SimpleChunkManager) -> None:
        coord = manager.get_chunk_coord((0.0, 0.0))
        assert coord == (0, 0)

    def test_get_chunk_coord_positive(self, manager: SimpleChunkManager) -> None:
        coord = manager.get_chunk_coord((500.0, 500.0))
        assert coord == (0, 0)

    def test_get_chunk_coord_boundary(self, manager: SimpleChunkManager) -> None:
        coord = manager.get_chunk_coord((1000.0, 0.0))
        assert coord == (1, 0)

    def test_get_chunk_coord_negative(self, manager: SimpleChunkManager) -> None:
        coord = manager.get_chunk_coord((-500.0, -500.0))
        assert coord == (-1, -1)

    def test_get_chunk_coord_large_positive(self, manager: SimpleChunkManager) -> None:
        coord = manager.get_chunk_coord((2500.0, 3500.0))
        assert coord == (2, 3)


class TestChunkManagerRequiredChunks:
    @pytest.fixture
    def manager(self) -> SimpleChunkManager:
        mock_system = MagicMock()
        return SimpleChunkManager(mock_system, chunk_size=1000)

    def test_get_required_chunks_at_origin(self, manager: SimpleChunkManager) -> None:
        required = manager.get_required_chunks((0, 0))
        expected = {
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 0),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        }
        assert required == expected

    def test_get_required_chunks_count(self, manager: SimpleChunkManager) -> None:
        required = manager.get_required_chunks((5, 5))
        assert len(required) == 9

    def test_get_required_chunks_offset(self, manager: SimpleChunkManager) -> None:
        required = manager.get_required_chunks((2, 3))
        assert (2, 3) in required
        assert (1, 2) in required
        assert (3, 4) in required

    def test_get_required_chunks_custom_rings(
        self, manager: SimpleChunkManager
    ) -> None:
        required = manager.get_required_chunks((0, 0), rings=2)
        assert len(required) == 25


class TestChunkManagerLoadUnload:
    @pytest.fixture
    def mock_system(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def manager(self, mock_system: MagicMock) -> SimpleChunkManager:
        return SimpleChunkManager(mock_system, chunk_size=1000)

    def test_initial_state(self, manager: SimpleChunkManager) -> None:
        assert len(manager._loaded_chunks) == 0

    def test_load_chunk(
        self, manager: SimpleChunkManager, mock_system: MagicMock
    ) -> None:
        chunk = manager.load_chunk((0, 0))
        assert chunk.coord == (0, 0)
        assert (0, 0) in manager._loaded_chunks
        mock_system.add_all.assert_called()

    def test_unload_chunk(
        self, manager: SimpleChunkManager, mock_system: MagicMock
    ) -> None:
        manager.load_chunk((0, 0))
        mock_system.reset_mock()

        chunk = manager.unload_chunk((0, 0))
        assert chunk is not None
        assert (0, 0) not in manager._loaded_chunks
        mock_system.remove_all.assert_called()

    def test_unload_nonexistent_chunk(self, manager: SimpleChunkManager) -> None:
        chunk = manager.unload_chunk((99, 99))
        assert chunk is None


class TestChunkManagerUpdate:
    @pytest.fixture
    def mock_system(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def manager(self, mock_system: MagicMock) -> SimpleChunkManager:
        return SimpleChunkManager(mock_system, chunk_size=1000)

    def test_initial_update_loads_chunks(
        self, manager: SimpleChunkManager, mock_system: MagicMock
    ) -> None:
        manager.update((500.0, 500.0))

        assert len(manager._loaded_chunks) == 9
        assert mock_system.add_all.call_count == 9

    def test_no_reload_same_chunk(
        self, manager: SimpleChunkManager, mock_system: MagicMock
    ) -> None:
        manager.update((500.0, 500.0))
        initial_call_count = mock_system.add_all.call_count

        manager.update((600.0, 600.0))

        assert mock_system.add_all.call_count == initial_call_count

    def test_chunk_transition_loads_new_unloads_old(
        self, manager: SimpleChunkManager, mock_system: MagicMock
    ) -> None:
        manager.update((500.0, 500.0))
        mock_system.reset_mock()

        manager.update((1500.0, 500.0))

        assert mock_system.add_all.call_count == 3
        assert mock_system.remove_all.call_count == 3

    def test_clear(self, manager: SimpleChunkManager, mock_system: MagicMock) -> None:
        manager.update((500.0, 500.0))
        mock_system.reset_mock()

        manager.clear()

        assert len(manager._loaded_chunks) == 0
        assert mock_system.remove_all.call_count == 9
