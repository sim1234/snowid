import math
import typing

import sdl2.ext

from ..physics.vector import Vector
from ..subsystem import SubSystemObject


class GraphicalObject(SubSystemObject):
    position: tuple[float, float]
    angle: float

    def draw(self, vp: "ViewPort") -> None:
        raise NotImplementedError()


class ComplexGraphicalObject(GraphicalObject):
    def __init__(self, objects: typing.Iterable[GraphicalObject] = ()) -> None:
        super().__init__()
        self.position: tuple[float, float] = (0, 0)
        self.angle: float = 0.0
        self.objects = list(objects)

    def draw(self, vp: "ViewPort") -> None:
        for obj in self.objects:
            obj.draw(vp)


class TexturedObject(GraphicalObject):
    texture: sdl2.ext.TextureSprite
    scale: float = 1.0

    def draw(self, vp: "ViewPort") -> None:
        texture = self.texture
        w, h = texture.size
        w, h = vp.d_to_view(w) * self.scale, vp.d_to_view(h) * self.scale
        x, y = vp.to_view(self.position)
        x, y = x - w / 2, y - h / 2
        angle = (self.angle / (2 * math.pi)) * 360 + texture.angle
        dst = (int(x), int(y), int(w), int(h))
        vp.renderer.copy(texture.texture, None, dst, angle, None, texture.flip)


class GFXObject(GraphicalObject):
    color: tuple[int, int, int] | tuple[int, int, int, int] | sdl2.ext.Color


class Point(GFXObject):
    def draw(self, vp: "ViewPort") -> None:
        vp.renderer.pixel([vp.to_view_int(self.position)], self.color)


class Line(GFXObject):
    end_points: tuple[tuple[float, float], tuple[float, float]]

    def draw(self, vp: "ViewPort") -> None:
        start, end = self.end_points
        sx, sy = vp.to_view_int(start)
        ex, ey = vp.to_view_int(end)
        vp.renderer.line([(int(sx), int(sy), int(ex), int(ey))], self.color)


class Polygon(GFXObject):
    points: typing.Iterable[tuple[float, float]]

    def draw(self, vp: "ViewPort") -> None:
        vp.renderer.filled_polygon(
            [[vp.to_view_int(p) for p in self.points]], self.color
        )


class Circle(GFXObject):
    radius: float

    def draw(self, vp: "ViewPort") -> None:
        r = int(vp.d_to_view(self.radius))
        px, py = vp.to_view_int(self.position)
        polar_vec = Vector.polar(r, self.angle)
        lx, ly = int(px + polar_vec.x), int(py + polar_vec.y)
        vp.renderer.filled_circle([(px, py, r)], self.color)
        vp.renderer.line([(px, py, lx, ly)], sdl2.ext.Color(0, 0, 0))


from .viewport import ViewPort  # noqa
