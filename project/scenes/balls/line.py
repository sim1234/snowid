import typing

import sdl2.ext
from gamepart.physics import SimplePhysicalObject, pymunk
from gamepart.viewport import Line

from .category import cat_terrain, cat_terrain_collide


class BoundLine(Line, SimplePhysicalObject[pymunk.Segment]):
    color = sdl2.ext.Color(255, 0, 0)

    def __init__(
        self, static_body: pymunk.Body, p1x: float, p1y: float, p2x: float, p2y: float
    ):
        shape = pymunk.Segment(static_body, (p1x, p1y), (p2x, p2y), 0.0)
        shape.filter = cat_terrain.filter(cat_terrain_collide)
        shape.elasticity = 1.0
        shape.friction = 1.0
        super().__init__(None, shape, cat_terrain)

    @property
    def end_points(self):
        return self.shape.a, self.shape.b

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
