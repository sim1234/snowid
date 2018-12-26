import math
import typing

import sdl2.ext

from ..subsystem import SubSystemObject
from ..physics.vector import Vector


class GraphicalObject(SubSystemObject):
    position: typing.Tuple[float, float]
    angle: float

    def draw(self, vp: "ViewPort"):
        raise NotImplementedError()


class ComplexGraphicalObject(GraphicalObject):
    position = (0, 0)
    angle = 0

    def __init__(self, objects: typing.Iterable[GraphicalObject] = ()):
        super().__init__()
        self.objects = list(objects)

    def draw(self, vp: "ViewPort"):
        for obj in self.objects:
            obj.draw(vp)


class TexturedObject(GraphicalObject):
    texture: sdl2.ext.TextureSprite
    scale: float = 1.0

    def draw(self, vp: "ViewPort"):
        texture = self.texture
        w, h = texture.size
        w, h = vp.d_to_view(w) * self.scale, vp.d_to_view(h) * self.scale
        x, y = vp.to_view(self.position)
        x, y = x - w / 2, y - h / 2
        angle = (self.angle / (2 * math.pi)) * 360 + texture.angle
        dst = (int(x), int(y), int(w), int(h))
        vp.renderer.copy(texture.texture, None, dst, angle, None, texture.flip)


class GFXObject(GraphicalObject):
    color: typing.Union[
        typing.Tuple[int, int, int], typing.Tuple[int, int, int, int], sdl2.ext.Color
    ]


class Point(GFXObject):
    def draw(self, vp: "ViewPort"):
        vp.renderer.pixel([vp.to_view(self.position)], self.color)


class Line(GFXObject):
    end_points: typing.Tuple[typing.Tuple[float, float], typing.Tuple[float, float]]

    def draw(self, vp: "ViewPort"):
        start, end = self.end_points
        sx, sy = vp.to_view(start)
        ex, ey = vp.to_view(end)
        vp.renderer.line([(sx, sy, ex, ey)], self.color)


class Polygon(GFXObject):
    points: typing.Iterable[typing.Tuple[float, float]]

    def draw(self, vp: "ViewPort"):
        points = [vp.to_view(p) for p in self.points]
        vp.renderer.filled_polygon([points], self.color)


class Circle(GFXObject):
    radius: float

    def draw(self, vp: "ViewPort"):
        r = vp.d_to_view(self.radius)
        px, py = vp.to_view(self.position)
        lx, ly = tuple((px, py) + Vector.polar(r, self.angle))
        vp.renderer.filled_circle([(px, py, r)], self.color)
        vp.renderer.line([(px, py, lx, ly)], sdl2.ext.Color(0, 0, 0))


from .viewport import ViewPort  # noqa
