import ctypes
import typing

import sdl2
import sdl2.ext
import sdl2.sdlgfx
from sdl2 import Sint16

_t_circle = tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt]
_t_circles = typing.Sequence[_t_circle]
_t_anys = typing.Sequence[typing.Sequence[typing.SupportsInt]]


class GfxRenderer(sdl2.ext.Renderer):
    """Renderer with sdl2_gfx support"""

    color: sdl2.ext.Color
    blendmode: int

    @property
    def clip(self) -> tuple[int, int, int, int]:
        rect = sdl2.SDL_Rect()
        ret = sdl2.SDL_RenderGetClipRect(self.sdlrenderer, ctypes.byref(rect))
        if ret:
            raise sdl2.ext.SDLError()
        return rect.x, rect.y, rect.w, rect.h

    @clip.setter
    def clip(self, value: tuple[int, int, int, int]):
        rect = sdl2.SDL_Rect(*value)
        ret = sdl2.SDL_RenderSetClipRect(self.sdlrenderer, ctypes.byref(rect))
        if ret:
            raise sdl2.ext.SDLError()

    def _shape(
        self,
        shapes: _t_anys,
        color: sdl2.ext.Color = (0, 0, 0),
        *,
        gfx_fun: typing.Callable = lambda: None,
        map_pos: typing.Callable = int,
    ):
        """Draws multiple shapes on the renderer using gfx_fun."""
        color = sdl2.ext.convert_to_color(color)
        blendmode = self.blendmode
        for cords in shapes:
            ret = gfx_fun(
                self.sdlrenderer,
                *map(map_pos, cords),
                color.r,
                color.g,
                color.b,
                color.a,
            )
            if ret == -1:
                raise sdl2.ext.SDLError()
            self.blendmode = blendmode

    def circle(self, circles: _t_circles, color=None):
        return self._shape(circles, color, gfx_fun=sdl2.sdlgfx.circleRGBA)

    def filled_circle(self, circles: _t_circles, color=None):
        return self._shape(circles, color, gfx_fun=sdl2.sdlgfx.filledCircleRGBA)

    def aa_circle(self, circles: _t_circles, color=None):
        return self._shape(circles, color, gfx_fun=sdl2.sdlgfx.aacircleRGBA)

    def pixel(self, pixels, color=None):
        return self._shape(pixels, color, gfx_fun=sdl2.sdlgfx.pixelRGBA)

    def rounded_rectangle(self, rects, color=None):
        return self._shape(rects, color, gfx_fun=sdl2.sdlgfx.roundedRectangleRGBA)

    def rounded_box(self, rects, color=None):
        return self._shape(rects, color, gfx_fun=sdl2.sdlgfx.roundedBoxRGBA)

    def line(self, lines, color=None):
        return self._shape(lines, color, gfx_fun=sdl2.sdlgfx.lineRGBA)

    def aa_line(self, lines, color=None):
        return self._shape(lines, color, gfx_fun=sdl2.sdlgfx.aalineRGBA)

    def thick_line(self, lines, color=None):
        return self._shape(lines, color, gfx_fun=sdl2.sdlgfx.thickLineRGBA)

    def arc(self, arcs, color=None):
        return self._shape(arcs, color, gfx_fun=sdl2.sdlgfx.arcRGBA)

    def ellipse(self, ellipses, color=None):
        return self._shape(ellipses, color, gfx_fun=sdl2.sdlgfx.ellipseRGBA)

    def aa_ellipse(self, ellipses, color=None):
        return self._shape(ellipses, color, gfx_fun=sdl2.sdlgfx.aaellipseRGBA)

    def filled_ellipse(self, ellipses, color=None):
        return self._shape(ellipses, color, gfx_fun=sdl2.sdlgfx.filledEllipseRGBA)

    def pie(self, pies, color=None):
        return self._shape(pies, color, gfx_fun=sdl2.sdlgfx.pieRGBA)

    def filled_pie(self, pies, color=None):
        return self._shape(pies, color, gfx_fun=sdl2.sdlgfx.pieRGBA)

    def trigon(self, trigons, color=None):
        return self._shape(trigons, color, gfx_fun=sdl2.sdlgfx.trigonRGBA)

    def aa_trigon(self, trigons, color=None):
        return self._shape(trigons, color, gfx_fun=sdl2.sdlgfx.aatrigonRGBA)

    def filled_trigon(self, trigons, color=None):
        return self._shape(trigons, color, gfx_fun=sdl2.sdlgfx.filledTrigonRGBA)

    def _polygon(self, polygons, color=None, *, gfx_fun=lambda: None):
        """[[(p1x, p1y), (p2y, p2y), ...], ...]"""
        polys = []
        for points in polygons:
            num = len(points)
            vx = (Sint16 * num)(*[int(p[0]) for p in points])
            vy = (Sint16 * num)(*[int(p[1]) for p in points])
            polys.append((vx, vy, num))
        return self._shape(polys, color, gfx_fun=gfx_fun, map_pos=lambda x: x)

    def polygon(self, polygons, color=None):
        return self._polygon(polygons, color, gfx_fun=sdl2.sdlgfx.polygonRGBA)

    def aa_polygon(self, polygons, color=None):
        return self._polygon(polygons, color, gfx_fun=sdl2.sdlgfx.aapolygonRGBA)

    def filled_polygon(self, polygons, color=None):
        return self._polygon(polygons, color, gfx_fun=sdl2.sdlgfx.filledPolygonRGBA)

    def bezier(self, beziers, color=None):
        """[(s, [(p1x, p1y), (p2y, p2y), ...]), ...]"""
        curves = []
        for s, points in beziers:
            num = len(points)
            vx = (Sint16 * num)(*[int(p[0]) for p in points])
            vy = (Sint16 * num)(*[int(p[1]) for p in points])
            curves.append((vx, vy, num, s))
        return self._shape(
            curves, color, gfx_fun=sdl2.sdlgfx.bezierRGBA, map_pos=lambda x: x
        )

    # TODO: texturedPolygon

    def fill_color(self, color=None):
        if color is not None:
            tmp = self.color
            self.color = color
        ret = sdl2.SDL_RenderFillRect(self.sdlrenderer, None)
        if color is not None:
            self.color = tmp
        if ret == -1:
            raise sdl2.ext.SDLError()
