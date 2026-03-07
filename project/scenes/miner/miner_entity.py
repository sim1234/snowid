from typing import TYPE_CHECKING

from gamepart.viewport import Polygon

if TYPE_CHECKING:
    from .patch import ResourcePatch


MINER_SIZE = 8.0


def _miner_points(
    center_x: float, center_y: float, size: float
) -> list[tuple[float, float]]:
    return [
        (center_x, center_y - size),
        (center_x + size, center_y),
        (center_x, center_y + size),
        (center_x - size, center_y),
    ]


class Miner(Polygon):
    def __init__(self, patch: "ResourcePatch") -> None:
        super().__init__()
        self.patch = patch
        self.position = patch.position
        self.angle = 0.0
        self.points = _miner_points(patch.position[0], patch.position[1], MINER_SIZE)
        self.color = (60, 60, 80, 255)

    def contains_point(self, world_pos: tuple[float, float]) -> bool:
        return self.patch.contains_point(world_pos)
