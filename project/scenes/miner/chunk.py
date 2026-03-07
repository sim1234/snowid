import math

from gamepart.chunk import Chunk, ChunkManager
from gamepart.noise import PerlinNoise
from gamepart.subsystem import SystemManager

from .patch import ResourcePatch, ResourceType

PATCH_GRID_STEP = 80
RICHNESS_BASE = 20
RICHNESS_DISTANCE_FACTOR = 0.08
RICHNESS_NOISE_SCALE = 50
RICHNESS_MIN = 10
RICHNESS_MAX = 500
PATCH_THRESHOLD = 0.35
TYPE_SCALE = 200.0


class ResourceChunk(Chunk):
    def __init__(self, coord: tuple[int, int]) -> None:
        super().__init__(coord)
        self.patches: list[ResourcePatch] = []


class ResourceChunkManager(ChunkManager[ResourceChunk]):
    def __init__(
        self,
        system: SystemManager,
        seed: int = 42,
        chunk_size: int = 512,
    ) -> None:
        super().__init__(system, chunk_size)
        self._noise_patch = PerlinNoise(
            seed=seed,
            octaves=4,
            persistence=0.5,
            scale=180.0,
        )
        self._noise_iron = PerlinNoise(
            seed=seed + 1000,
            octaves=2,
            persistence=0.5,
            scale=TYPE_SCALE,
        )
        self._noise_copper = PerlinNoise(
            seed=seed + 2000,
            octaves=2,
            persistence=0.5,
            scale=TYPE_SCALE,
        )
        self._noise_coal = PerlinNoise(
            seed=seed + 3000,
            octaves=2,
            persistence=0.5,
            scale=TYPE_SCALE,
        )

    def update(self, center: tuple[float, float], rings: int = 2) -> None:
        center_chunk = self.get_chunk_coord(center)
        required = self.get_required_chunks(
            (center_chunk[0], center_chunk[1]), rings=rings
        )
        loaded = set(self._loaded_chunks.keys())
        for coord in required - loaded:
            self.load_chunk(coord)

    def _load_chunk(self, coord: tuple[int, int]) -> ResourceChunk:
        chunk = ResourceChunk(coord)
        cx, cy = coord
        x_start = cx * self._chunk_size
        y_start = cy * self._chunk_size
        x_end = x_start + self._chunk_size
        y_end = y_start + self._chunk_size
        x = x_start + PATCH_GRID_STEP // 2
        while x < x_end:
            y = y_start + PATCH_GRID_STEP // 2
            while y < y_end:
                patch_val = self._noise_patch.get2d(x, y)
                if patch_val >= PATCH_THRESHOLD:
                    resource_type = self._type_from_noise(x, y)
                    distance = math.hypot(x, y)
                    richness_raw = (
                        RICHNESS_BASE
                        + distance * RICHNESS_DISTANCE_FACTOR
                        + (patch_val + 1) * 0.5 * RICHNESS_NOISE_SCALE
                    )
                    richness = int(max(RICHNESS_MIN, min(RICHNESS_MAX, richness_raw)))
                    patch = ResourcePatch(
                        position=(float(x), float(y)),
                        resource_type=resource_type,
                        richness=richness,
                    )
                    chunk.patches.append(patch)
                    chunk.objects.append(patch)
                y += PATCH_GRID_STEP
            x += PATCH_GRID_STEP
        return chunk

    def _type_from_noise(self, x: float, y: float) -> ResourceType:
        iron_val = self._noise_iron.get2d(x, y)
        copper_val = self._noise_copper.get2d(x, y)
        coal_val = self._noise_coal.get2d(x, y)
        if iron_val >= copper_val and iron_val >= coal_val:
            return "iron"
        if copper_val >= coal_val:
            return "copper"
        return "coal"

    def get_patch_at(self, world_pos: tuple[float, float]) -> ResourcePatch | None:
        for chunk in self._loaded_chunks.values():
            for patch in chunk.patches:
                if patch.contains_point(world_pos):
                    return patch
        return None
