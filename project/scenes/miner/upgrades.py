from collections.abc import Callable

UPGRADE_MINER_SPEED = "miner_speed"


def production_rate_per_miner(speed_level: int) -> float:
    return 1.0 + speed_level * 0.2


def _cost_speed(level: int) -> tuple[int, int, int]:
    base_iron = 30
    base_copper = 20
    base_coal = 20
    mult = 1.5**level
    return (
        int(base_iron * mult),
        int(base_copper * mult),
        int(base_coal * mult),
    )


class UpgradeDef:
    def __init__(
        self,
        id: str,
        name: str,
        cost_fn: Callable[[int], tuple[int, int, int]],
        max_level: int = 10,
    ) -> None:
        self.id = id
        self.name = name
        self.cost_fn = cost_fn
        self.max_level = max_level

    def cost(self, level: int) -> tuple[int, int, int]:
        return self.cost_fn(level)


UPGRADES: list[UpgradeDef] = [
    UpgradeDef(
        id=UPGRADE_MINER_SPEED,
        name="Miner speed",
        cost_fn=_cost_speed,
        max_level=10,
    ),
]
