import typing

import sdl2.ext
from gamepart.physics import SimplePhysicalObject, pymunk
from gamepart.viewport import Line

from .category import cat_terrain, cat_terrain_collide


class BoundLine(Line, SimplePhysicalObject[pymunk.Segment]):
    color = sdl2.ext.Color(255, 0, 0)

    def __init__(
        self, static_body: pymunk.Body, p1x: float, p1y: float, p2x: float, p2y: float
    ) -> None:
        shape = pymunk.Segment(static_body, (p1x, p1y), (p2x, p2y), 0.0)
        shape.filter = cat_terrain.filter(cat_terrain_collide)
        shape.elasticity = 1.0
        shape.friction = 1.0
        super().__init__(None, shape, cat_terrain)

    @property
    def end_points(self) -> tuple[tuple[float, float], tuple[float, float]]:
        return self.shape.a, self.shape.b

    @end_points.setter
    def end_points(
        self, value: tuple[tuple[float, float], tuple[float, float]]
    ) -> None:
        raise NotImplementedError()

    @property
    def position(self) -> tuple[float, float]:
        # Return midpoint of the line segment
        a, b = self.end_points
        return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)

    @position.setter
    def position(self, value: tuple[float, float]) -> None:
        raise NotImplementedError()

    @property
    def angle(self) -> float:
        # Return angle of the line segment
        a, b = self.end_points
        import math

        return math.atan2(b[1] - a[1], b[0] - a[0])

    @angle.setter
    def angle(self, value: float) -> None:
        raise NotImplementedError()

    @classmethod
    def make_box(
        cls,
        static_body: pymunk.Body,
        width: float,
        height: float,
        start_x: float = 0.0,
        start_y: float = 0.0,
    ) -> typing.Generator["BoundLine", None, None]:
        end_x = start_x + width
        end_y = start_y + height
        yield cls(static_body, start_x, start_y, end_x, start_y)
        yield cls(static_body, end_x, start_y, end_x, end_y)
        yield cls(static_body, end_x, end_y, start_x, end_y)
        yield cls(static_body, start_x, end_y, start_x, start_y)
