import ctypes
import typing
from collections.abc import Sequence
from typing import Any, TypeVarTuple

import sdl2
import sdl2.ext
import sdl2.sdlgfx
from sdl2.stdinc import Sint16

_Ts = TypeVarTuple("_Ts")
_Color = sdl2.ext.Color | tuple[int, int, int] | tuple[int, int, int, int] | int | str


class GfxRenderer(sdl2.ext.Renderer):
    """Renderer with sdl2_gfx support."""

    color: sdl2.ext.Color

    @property
    def clip(self) -> tuple[int, int, int, int]:
        rect = sdl2.SDL_Rect()
        sdl2.SDL_RenderGetClipRect(
            self.sdlrenderer,
            ctypes.byref(rect),  # type: ignore[arg-type]
        )
        return rect.x, rect.y, rect.w, rect.h

    @clip.setter
    def clip(self, value: tuple[int, int, int, int]) -> None:
        rect = sdl2.SDL_Rect(*value)
        ret = sdl2.SDL_RenderSetClipRect(
            self.sdlrenderer,
            ctypes.byref(rect),  # type: ignore[arg-type]
        )
        if ret:
            raise sdl2.ext.SDLError()

    def _shape(
        self,
        shapes: Sequence[tuple[*_Ts]],
        color: _Color,
        *,
        gfx_fun: typing.Callable[[Any, *_Ts, int, int, int, int], int],
    ) -> None:
        """Draws multiple shapes on the renderer using the provided gfx function."""
        clr = sdl2.ext.convert_to_color(color)
        for cords in shapes:
            ret = gfx_fun(
                self.sdlrenderer,
                *cords,
                clr.r,
                clr.g,
                clr.b,
                clr.a,
            )
            if ret:
                raise sdl2.ext.SDLError()

    def circle(
        self,
        circles: Sequence[tuple[int, int, int]],
        color: _Color,
    ) -> None:
        """Draws unfilled circles.

        Args:
            circles: Sequence of (x, y, radius) tuples where x, y is the center.
            color: The color to draw with.
        """
        return self._shape(circles, color, gfx_fun=sdl2.sdlgfx.circleRGBA)

    def filled_circle(
        self,
        circles: Sequence[tuple[int, int, int]],
        color: _Color,
    ) -> None:
        """Draws filled circles.

        Args:
            circles: Sequence of (x, y, radius) tuples where x, y is the center.
            color: The color to draw with.
        """
        return self._shape(circles, color, gfx_fun=sdl2.sdlgfx.filledCircleRGBA)

    def aa_circle(
        self,
        circles: Sequence[tuple[int, int, int]],
        color: _Color,
    ) -> None:
        """Draws anti-aliased unfilled circles.

        Args:
            circles: Sequence of (x, y, radius) tuples where x, y is the center.
            color: The color to draw with.
        """
        return self._shape(circles, color, gfx_fun=sdl2.sdlgfx.aacircleRGBA)

    def pixel(
        self,
        pixels: Sequence[tuple[int, int]],
        color: _Color,
    ) -> None:
        """Draws single pixels.

        Args:
            pixels: Sequence of (x, y) coordinate tuples.
            color: The color to draw with.
        """
        return self._shape(pixels, color, gfx_fun=sdl2.sdlgfx.pixelRGBA)

    def rounded_rectangle(
        self,
        rects: Sequence[tuple[int, int, int, int, int]],
        color: _Color,
    ) -> None:
        """Draws unfilled rectangles with rounded corners.

        Args:
            rects: Sequence of (x1, y1, x2, y2, radius) tuples where (x1, y1) is
                the top-left corner, (x2, y2) is the bottom-right corner, and
                radius is the corner arc radius.
            color: The color to draw with.
        """
        return self._shape(rects, color, gfx_fun=sdl2.sdlgfx.roundedRectangleRGBA)

    def rounded_box(
        self,
        rects: Sequence[tuple[int, int, int, int, int]],
        color: _Color,
    ) -> None:
        """Draws filled rectangles with rounded corners.

        Args:
            rects: Sequence of (x1, y1, x2, y2, radius) tuples where (x1, y1) is
                the top-left corner, (x2, y2) is the bottom-right corner, and
                radius is the corner arc radius.
            color: The color to draw with.
        """
        return self._shape(rects, color, gfx_fun=sdl2.sdlgfx.roundedBoxRGBA)

    def line(
        self,
        lines: Sequence[tuple[int, int, int, int]],
        color: _Color,
    ) -> None:
        """Draws lines.

        Args:
            lines: Sequence of (x1, y1, x2, y2) tuples defining line endpoints.
            color: The color to draw with.
        """
        return self._shape(lines, color, gfx_fun=sdl2.sdlgfx.lineRGBA)

    def aa_line(
        self,
        lines: Sequence[tuple[int, int, int, int]],
        color: _Color,
    ) -> None:
        """Draws anti-aliased lines.

        Args:
            lines: Sequence of (x1, y1, x2, y2) tuples defining line endpoints.
            color: The color to draw with.
        """
        return self._shape(lines, color, gfx_fun=sdl2.sdlgfx.aalineRGBA)

    def thick_line(
        self,
        lines: Sequence[tuple[int, int, int, int, int]],
        color: _Color,
    ) -> None:
        """Draws lines with a given thickness.

        Args:
            lines: Sequence of (x1, y1, x2, y2, width) tuples defining line
                endpoints and thickness in pixels (1-255).
            color: The color to draw with.
        """
        return self._shape(lines, color, gfx_fun=sdl2.sdlgfx.thickLineRGBA)

    def arc(
        self,
        arcs: Sequence[tuple[int, int, int, int, int]],
        color: _Color,
    ) -> None:
        """Draws arcs (partial circle outlines).

        Args:
            arcs: Sequence of (x, y, radius, start, end) tuples where x, y is the
                center, and start/end are angles in degrees (0 at bottom,
                increasing counter-clockwise).
            color: The color to draw with.
        """
        return self._shape(arcs, color, gfx_fun=sdl2.sdlgfx.arcRGBA)

    def ellipse(
        self,
        ellipses: Sequence[tuple[int, int, int, int]],
        color: _Color,
    ) -> None:
        """Draws unfilled ellipses.

        Args:
            ellipses: Sequence of (x, y, rx, ry) tuples where x, y is the center,
                rx is the horizontal radius, and ry is the vertical radius.
            color: The color to draw with.
        """
        return self._shape(ellipses, color, gfx_fun=sdl2.sdlgfx.ellipseRGBA)

    def aa_ellipse(
        self,
        ellipses: Sequence[tuple[int, int, int, int]],
        color: _Color,
    ) -> None:
        """Draws anti-aliased unfilled ellipses.

        Args:
            ellipses: Sequence of (x, y, rx, ry) tuples where x, y is the center,
                rx is the horizontal radius, and ry is the vertical radius.
            color: The color to draw with.
        """
        return self._shape(ellipses, color, gfx_fun=sdl2.sdlgfx.aaellipseRGBA)

    def filled_ellipse(
        self,
        ellipses: Sequence[tuple[int, int, int, int]],
        color: _Color,
    ) -> None:
        """Draws filled ellipses.

        Args:
            ellipses: Sequence of (x, y, rx, ry) tuples where x, y is the center,
                rx is the horizontal radius, and ry is the vertical radius.
            color: The color to draw with.
        """
        return self._shape(ellipses, color, gfx_fun=sdl2.sdlgfx.filledEllipseRGBA)

    def pie(
        self,
        pies: Sequence[tuple[int, int, int, int, int]],
        color: _Color,
    ) -> None:
        """Draws unfilled pie slices (circle segments).

        Args:
            pies: Sequence of (x, y, radius, start, end) tuples where x, y is the
                center, and start/end are angles in degrees (0 at bottom,
                increasing counter-clockwise).
            color: The color to draw with.
        """
        return self._shape(pies, color, gfx_fun=sdl2.sdlgfx.pieRGBA)

    def filled_pie(
        self,
        pies: Sequence[tuple[int, int, int, int, int]],
        color: _Color,
    ) -> None:
        """Draws filled pie slices (circle segments).

        Args:
            pies: Sequence of (x, y, radius, start, end) tuples where x, y is the
                center, and start/end are angles in degrees (0 at bottom,
                increasing counter-clockwise).
            color: The color to draw with.
        """
        return self._shape(pies, color, gfx_fun=sdl2.sdlgfx.filledPieRGBA)

    def trigon(
        self,
        trigons: Sequence[tuple[int, int, int, int, int, int]],
        color: _Color,
    ) -> None:
        """Draws unfilled triangles.

        Args:
            trigons: Sequence of (x1, y1, x2, y2, x3, y3) tuples defining the
                three vertices of each triangle.
            color: The color to draw with.
        """
        return self._shape(trigons, color, gfx_fun=sdl2.sdlgfx.trigonRGBA)

    def aa_trigon(
        self,
        trigons: Sequence[tuple[int, int, int, int, int, int]],
        color: _Color,
    ) -> None:
        """Draws anti-aliased unfilled triangles.

        Args:
            trigons: Sequence of (x1, y1, x2, y2, x3, y3) tuples defining the
                three vertices of each triangle.
            color: The color to draw with.
        """
        return self._shape(trigons, color, gfx_fun=sdl2.sdlgfx.aatrigonRGBA)

    def filled_trigon(
        self,
        trigons: Sequence[tuple[int, int, int, int, int, int]],
        color: _Color,
    ) -> None:
        """Draws filled triangles.

        Args:
            trigons: Sequence of (x1, y1, x2, y2, x3, y3) tuples defining the
                three vertices of each triangle.
            color: The color to draw with.
        """
        return self._shape(trigons, color, gfx_fun=sdl2.sdlgfx.filledTrigonRGBA)

    def _polygon(
        self,
        polygons: Sequence[Sequence[tuple[int, int]]],
        color: _Color,
        *,
        gfx_fun: typing.Callable[..., int],
    ) -> None:
        """Internal method to draw polygons.

        Args:
            polygons: Sequence of polygons, where each polygon is a sequence of
                (x, y) vertex tuples.
            color: The color to draw with.
            gfx_fun: The SDL2_gfx function to use for drawing.
        """
        clr = sdl2.ext.convert_to_color(color)
        for points in polygons:
            num = len(points)
            vx = (Sint16 * num)(*[int(p[0]) for p in points])
            vy = (Sint16 * num)(*[int(p[1]) for p in points])
            ret = gfx_fun(self.sdlrenderer, vx, vy, num, clr.r, clr.g, clr.b, clr.a)
            if ret:
                raise sdl2.ext.SDLError()

    def polygon(
        self,
        polygons: Sequence[Sequence[tuple[int, int]]],
        color: _Color,
    ) -> None:
        """Draws unfilled polygons.

        Args:
            polygons: Sequence of polygons, where each polygon is a sequence of
                (x, y) vertex tuples defining the polygon outline.
            color: The color to draw with.
        """
        return self._polygon(polygons, color, gfx_fun=sdl2.sdlgfx.polygonRGBA)

    def aa_polygon(
        self,
        polygons: Sequence[Sequence[tuple[int, int]]],
        color: _Color,
    ) -> None:
        """Draws anti-aliased unfilled polygons.

        Args:
            polygons: Sequence of polygons, where each polygon is a sequence of
                (x, y) vertex tuples defining the polygon outline.
            color: The color to draw with.
        """
        return self._polygon(polygons, color, gfx_fun=sdl2.sdlgfx.aapolygonRGBA)

    def filled_polygon(
        self,
        polygons: Sequence[Sequence[tuple[int, int]]],
        color: _Color,
    ) -> None:
        """Draws filled polygons.

        Args:
            polygons: Sequence of polygons, where each polygon is a sequence of
                (x, y) vertex tuples defining the polygon outline.
            color: The color to draw with.
        """
        return self._polygon(polygons, color, gfx_fun=sdl2.sdlgfx.filledPolygonRGBA)

    def bezier(
        self,
        beziers: Sequence[tuple[int, Sequence[tuple[int, int]]]],
        color: _Color,
    ) -> None:
        """Draws Bezier curves.

        The first and last vertices are the start and end points. Middle vertices
        are control points. For example, a cubic Bezier uses 4 vertices with 2
        control points.

        Args:
            beziers: Sequence of (steps, points) tuples where steps is the number
                of interpolation steps (minimum 2, higher = smoother), and points
                is a sequence of (x, y) vertex tuples (minimum 3 points).
            color: The color to draw with.
        """
        clr = sdl2.ext.convert_to_color(color)
        for steps, points in beziers:
            num = len(points)
            vx = (Sint16 * num)(*[int(p[0]) for p in points])
            vy = (Sint16 * num)(*[int(p[1]) for p in points])
            ret = sdl2.sdlgfx.bezierRGBA(
                self.sdlrenderer, vx, vy, num, steps, clr.r, clr.g, clr.b, clr.a
            )
            if ret:
                raise sdl2.ext.SDLError()

    def fill_color(self, color: _Color | None) -> None:
        """Fills the entire renderer with a color.

        Args:
            color: The color to fill with, or None to use the current color.
        """
        if color is not None:
            tmp = self.color
            self.color = sdl2.ext.convert_to_color(color)
        ret = sdl2.SDL_RenderFillRect(self.sdlrenderer, None)  # type: ignore[arg-type]
        if color is not None:
            self.color = tmp
        if ret == -1:
            raise sdl2.ext.SDLError()
