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


class TexturedObject(GraphicalObject):
    texture: sdl2.ext.TextureSprite

    def draw(self, vp: "ViewPort"):
        texture = self.texture
        x, y = vp.to_view(self.position)
        w, h = texture.size
        angle = (self.angle / 2 * math.pi) * 360
        dstrect = sdl2.SDL_Rect(
            int(x), int(y), int(vp.d_to_view(w)), int(vp.d_to_view(h))
        )
        ret = sdl2.SDL_RenderCopyEx(
            vp.renderer.sdlrenderer, texture.texture, None, dstrect, angle
        )
        if ret == -1:
            raise sdl2.ext.SDLError()


class GFXObject(GraphicalObject):
    color: typing.Union[typing.Tuple[int, int, int], typing.Tuple[int, int, int, int]]


class Point(GFXObject):
    def draw(self, vp: "ViewPort"):
        vp.renderer.pixel([vp.to_view(self.position)], self.color)


class Line(GFXObject):
    end_points: typing.Tuple[typing.Tuple[float, float], typing.Tuple[float, float]]

    def draw(self, vp: "ViewPort"):
        start, end = self.end_points
        sx, sy = vp.to_view(start)
        ex, ey = vp.to_view(end)
        vp.renderer.line([sx, sy, ex, ey], self.color)


class Rectangle(GFXObject):
    width: float
    height: float


class Circle(GFXObject):
    radius: float

    def draw(self, vp: "ViewPort"):
        pos = self.position
        r = vp.d_to_view(self.radius)
        px, py = vp.to_view(pos)
        lx, ly = tuple((px, py) + Vector.polar(r, self.angle))
        vp.renderer.filled_circle((px, py, r), self.color)
        vp.renderer.line([px, py, lx, ly], (0, 0, 0))


from .viewport import ViewPort  # noqa
