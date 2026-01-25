import typing

from gamepart.subsystem import SubSystemObject, SystemManager


class Chunk:
    def __init__(self, coord: tuple[int, int]) -> None:
        self.coord = coord
        self.objects: list[SubSystemObject] = []


T = typing.TypeVar("T", bound=Chunk)


class ChunkManager(typing.Generic[T]):
    def __init__(
        self,
        system: SystemManager,
        chunk_size: int = 1000,
    ) -> None:
        self._system = system
        self._chunk_size = chunk_size
        self._loaded_chunks: dict[tuple[int, int], T] = {}

    def get_chunk_coord(self, position: tuple[float, float]) -> tuple[int, int]:
        return int(position[0] // self._chunk_size), int(
            position[1] // self._chunk_size
        )

    def get_required_chunks(
        self, center: tuple[int, int], rings: int = 1
    ) -> set[tuple[int, int]]:
        required: set[tuple[int, int]] = set()
        for dx in range(-rings, rings + 1):
            for dy in range(-rings, rings + 1):
                required.add((center[0] + dx, center[1] + dy))
        return required

    def _load_chunk(self, coord: tuple[int, int]) -> T:
        raise NotImplementedError

    def _unload_chunk(self, chunk: T) -> None:
        pass

    def load_chunk(self, coord: tuple[int, int]) -> T:
        chunk = self._load_chunk(coord)
        self._system.add_all(*chunk.objects)
        self._loaded_chunks[coord] = chunk
        return chunk

    def unload_chunk(self, coord: tuple[int, int]) -> T | None:
        chunk = self._loaded_chunks.pop(coord, None)
        if chunk is not None:
            self._unload_chunk(chunk)
            self._system.remove_all(*chunk.objects)
        return chunk

    def update(self, player_position: tuple[float, float]) -> None:
        player_chunk = self.get_chunk_coord(player_position)
        required = self.get_required_chunks(player_chunk)
        currently_loaded = set(self._loaded_chunks.keys())
        chunks_to_unload = currently_loaded - required
        chunks_to_load = required - currently_loaded
        for coord in chunks_to_unload:
            self.unload_chunk(coord)
        for coord in chunks_to_load:
            self.load_chunk(coord)

    def clear(self) -> None:
        for coord in list(self._loaded_chunks.keys()):
            self.unload_chunk(coord)
