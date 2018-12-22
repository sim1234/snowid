import math
import typing

import sdl2.ext

from ..subsystem import SubSystemObject
from ..physics.vector import Vector


class GraphicalObject(SubSystemObject):
    @property
    def position(self) -> typing.Tuple[float, float]:
        return 0, 0

    @property
    def angle(self) -> float:
        return 0

    def draw(self, vp: "ViewPort"):
        raise NotImplementedError()


class TexturedObject(GraphicalObject):
    @property
    def texture(self) -> sdl2.ext.TextureSprite:
        raise NotImplementedError()

    def draw(self, vp: "ViewPort"):
        texture = self.texture
        x, y = vp.to_view(self.position)
        w, h = texture.size
        angle = (self.angle / 2 * math.pi) * 360
        dstrect = sdl2.SDL_Rect(int(x), int(y), int(w * vp.zoom), int(h * vp.zoom))
        ret = sdl2.SDL_RenderCopyEx(
            vp.renderer.sdlrenderer, texture.texture, None, dstrect, angle
        )
        if ret == -1:
            raise sdl2.ext.SDLError()


class GFXObject(GraphicalObject):
    @property
    def color(self) -> typing.Tuple[int, int, int]:
        raise NotImplementedError()


class Point(GFXObject):
    def draw(self, vp: "ViewPort"):
        vp.renderer.pixel([vp.to_view(self.position)], self.color)


class Line(GFXObject):
    @property
    def length(self) -> float:
        raise NotImplementedError()

    def draw(self, vp: "ViewPort"):
        dv = Vector.polar(self.length / 2, self.angle)
        pos = self.position
        start, end = pos - dv, pos + dv
        sx, sy = vp.to_view(start)
        ex, ey = vp.to_view(end)
        vp.renderer.line([sx, sy, ex, ey], self.color)


class Rectangle(GFXObject):
    @property
    def width(self) -> float:
        raise NotImplementedError()

    @property
    def height(self) -> float:
        raise NotImplementedError()


class Circle(GFXObject):
    @property
    def radius(self) -> float:
        raise NotImplementedError()

    def draw(self, vp: "ViewPort"):
        pos = self.position
        r = self.radius
        px, py = vp.to_view(pos)
        lx, ly = vp.to_view(pos + Vector.polar(r, self.angle))
        vp.renderer.filled_circle([px, py, r], self.color)
        vp.renderer.line([px, py, lx, ly], (0, 0, 0))


from .viewport import ViewPort  # noqa
