import typing

import sdl2
import sdl2.sdlgfx
import sdl2.ext


_t_circle = typing.Tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt]
_t_circles = typing.Sequence[_t_circle]
_t_anys = typing.Sequence[typing.Sequence[typing.SupportsInt]]


class GfxRenderer(sdl2.ext.Renderer):
    """Renderer with sdl2_gfx support"""

    color: sdl2.ext.Color

    def __init__(self, *args, **kwargs):
        super(GfxRenderer, self).__init__(*args, **kwargs)
        self._blendmode: int = self.blendmode

    @property
    def blendmode(self) -> int:
        """Adds caching blendmode parameter"""
        self._blendmode = super(GfxRenderer, self).blendmode
        return self._blendmode

    @blendmode.setter
    def blendmode(self, value: int):
        self._blendmode = value
        super(GfxRenderer, self).blendmode = value

    def _shape(
        self,
        shapes: _t_anys,
        color: sdl2.ext.Color = (0, 0, 0),
        *,
        gfx_fun: typing.Callable = lambda: None,
        map_pos: type = int
    ):
        """Draws multiple shapes on the renderer using gfx_fun."""
        color = sdl2.ext.convert_to_color(color)
        if self._blendmode != sdl2.SDL_BLENDMODE_BLEND:  # Hack over sdl2_gfx
            color.a = 255
        for cords in shapes:
            ret = gfx_fun(
                self.sdlrenderer,
                *map(map_pos, cords),
                color.r,
                color.g,
                color.b,
                color.a
            )
            if ret == -1:
                raise sdl2.ext.SDLError()

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

    def polygon(self, polygons, color=None):
        return self._shape(polygons, color, gfx_fun=sdl2.sdlgfx.polygonRGBA)

    def aa_polygon(self, polygons, color=None):
        return self._shape(polygons, color, gfx_fun=sdl2.sdlgfx.aapolygonRGBA)

    def filled_polygon(self, polygons, color=None):
        return self._shape(polygons, color, gfx_fun=sdl2.sdlgfx.filledPolygonRGBA)

    # TODO: len(cords), texturedPolygon, bezierRGBA
