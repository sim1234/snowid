import math
from enum import Enum

from gamepart.viewport import Circle


class ResourceType(str, Enum):
    IRON = "iron"
    COPPER = "copper"
    COAL = "coal"


RESOURCE_COLORS: dict[ResourceType, tuple[int, int, int, int]] = {
    ResourceType.IRON: (70, 130, 200, 255),
    ResourceType.COPPER: (184, 115, 51, 255),
    ResourceType.COAL: (40, 40, 40, 255),
}

PATCH_BASE_RADIUS = 12.0
PATCH_RADIUS_PER_RICHNESS = 0.15


def richness_to_radius(richness: int) -> float:
    return PATCH_BASE_RADIUS + math.sqrt(max(0, richness)) * PATCH_RADIUS_PER_RICHNESS


class ResourcePatch(Circle):
    def __init__(
        self,
        position: tuple[float, float],
        resource_type: ResourceType,
        richness: int,
    ) -> None:
        super().__init__()
        self.position = position
        self.angle = 0.0
        self.resource_type = resource_type
        self.richness = richness
        self.radius = richness_to_radius(richness)
        self.color = RESOURCE_COLORS[resource_type]

    def deplete(self, amount: int = 1) -> None:
        self.richness = max(0, self.richness - amount)
        self.radius = richness_to_radius(self.richness)

    def contains_point(self, world_pos: tuple[float, float]) -> bool:
        dx = world_pos[0] - self.position[0]
        dy = world_pos[1] - self.position[1]
        return math.hypot(dx, dy) <= self.radius
