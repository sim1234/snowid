import pymunk
from gamepart.chunk import Chunk, ChunkManager
from gamepart.noise import PerlinNoise
from gamepart.subsystem import SystemManager

from .line import BoundLine

TERRAIN_BASE_Y = 50.0
TERRAIN_DETAIL_AMPLITUDE = 200.0
TERRAIN_LARGE_SCALE_FACTOR = 0.5


class TerrainChunkManager(ChunkManager[Chunk]):
    def __init__(
        self,
        system: SystemManager,
        static_body: pymunk.Body,
        seed: int = 42,
        chunk_size: int = 1000,
    ) -> None:
        super().__init__(system, chunk_size)
        self._static_body = static_body

        self._noise_detail = PerlinNoise(
            seed=seed,
            octaves=4,
            persistence=0.5,
            scale=500.0,
        )
        self._noise_large = PerlinNoise(
            seed=seed + 1000,
            octaves=2,
            persistence=0.5,
            scale=1000.0,
        )

    def _load_chunk(self, coord: tuple[int, int]) -> Chunk:
        chunk = Chunk(coord)
        chunk.objects.extend(self._generate_terrain(coord))
        return chunk

    def get_terrain_height(self, x: float) -> float:
        distance_factor = abs(x) * TERRAIN_LARGE_SCALE_FACTOR
        large_features = self._noise_large.get1d(x) * distance_factor
        detail = self._noise_detail.get1d(x) * TERRAIN_DETAIL_AMPLITUDE
        return TERRAIN_BASE_Y + large_features + detail

    def _line_overlaps_chunk(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        chunk_x_start: float,
        chunk_x_end: float,
        chunk_y_start: float,
        chunk_y_end: float,
    ) -> bool:
        x_min, x_max = min(x1, x2), max(x1, x2)
        y_min, y_max = min(y1, y2), max(y1, y2)
        x_overlaps = x_min < chunk_x_end and x_max >= chunk_x_start
        y_overlaps = y_min < chunk_y_end and y_max >= chunk_y_start
        return x_overlaps and y_overlaps

    def _generate_terrain(self, coord: tuple[int, int]) -> list[BoundLine]:
        chunk_x, chunk_y = coord
        chunk_x_start = chunk_x * self._chunk_size
        chunk_x_end = chunk_x_start + self._chunk_size
        chunk_y_start = chunk_y * self._chunk_size
        chunk_y_end = chunk_y_start + self._chunk_size
        step = 50

        lines: list[BoundLine] = []
        x1, y1 = float(chunk_x_start), self.get_terrain_height(float(chunk_x_start))
        for x in range(chunk_x_start + step, chunk_x_end + step, step):
            x2, y2 = float(x), self.get_terrain_height(float(x))

            if self._line_overlaps_chunk(
                x1, y1, x2, y2, chunk_x_start, chunk_x_end, chunk_y_start, chunk_y_end
            ):
                line = BoundLine(self._static_body, x1, y1, x2, y2)
                lines.append(line)

            x1, y1 = x2, y2

        return lines
