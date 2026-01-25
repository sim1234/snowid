import typing

import pymunk

from gamepart.noise import PerlinNoise
from gamepart.subsystem import SystemManager

from .line import BoundLine

from gamepart.chunk import Chunk, ChunkManager

TERRAIN_BASE_Y = 50.0
TERRAIN_AMPLITUDE = 400.0


class TerrainChunkManager(ChunkManager[Chunk]):
    def __init__(
        self,
        system: SystemManager,
        static_body: pymunk.Body,
        noise: PerlinNoise,
        chunk_size: int = 1000,
    ) -> None:
        super().__init__(system, chunk_size)
        self._static_body = static_body
        self._noise = noise

    def _load_chunk(self, coord: tuple[int, int]) -> Chunk:
        chunk = Chunk(coord)
        chunk.objects.extend(self._generate_terrain(coord))
        return chunk

    def _generate_terrain(self, coord: tuple[int, int]) -> list[BoundLine]:
        start_x = coord[0] * self._chunk_size
        end_x = start_x + self._chunk_size
        step = 50

        points: list[tuple[float, float]] = []
        for x in range(start_x, end_x + step, step):
            y = TERRAIN_BASE_Y + self._noise.get1d(float(x)) * TERRAIN_AMPLITUDE
            points.append((float(x), y))

        lines: list[BoundLine] = []
        for i in range(len(points) - 1):
            line = BoundLine(
                self._static_body,
                points[i][0],
                points[i][1],
                points[i + 1][0],
                points[i + 1][1],
            )
            lines.append(line)

        return lines
