"""Integration tests for GfxRenderer SDL2_gfx methods."""

from collections.abc import Generator
from typing import Any

import pytest
import sdl2
import sdl2.ext
from gamepart.render import GfxRenderer

RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
BLUE = (0, 0, 255, 255)
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
YELLOW = (255, 255, 0, 255)
CYAN = (0, 255, 255, 255)
MAGENTA = (255, 0, 255, 255)
ORANGE = (255, 165, 0, 255)
GRAY = (128, 128, 128, 255)
PURPLE = (128, 0, 128, 255)


@pytest.fixture(scope="module")
def sdl_init() -> Generator[None, None, None]:
    """Initialize SDL for the test module."""
    sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
    yield
    sdl2.SDL_Quit()


@pytest.fixture
def renderer(sdl_init: None) -> Generator[GfxRenderer, None, None]:
    """Create a GfxRenderer with a hidden window for testing."""
    window = sdl2.ext.Window("Test", size=(100, 100), flags=sdl2.SDL_WINDOW_HIDDEN)
    renderer = GfxRenderer(window)
    yield renderer
    sdl2.SDL_DestroyRenderer(renderer.sdlrenderer)
    sdl2.SDL_DestroyWindow(window.window)


class TestPixel:
    """Tests for pixel drawing."""

    def test_draws_single_pixel(self, renderer: GfxRenderer) -> None:
        renderer.pixel([(50, 50)], RED)

    def test_draws_multiple_pixels(self, renderer: GfxRenderer) -> None:
        renderer.pixel([(10, 10), (20, 20), (30, 30)], (255, 0, 0))

    def test_draws_pixel_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.pixel([(50, 50)], (255, 0, 0, 128))


class TestHline:
    """Tests for horizontal line drawing."""

    def test_draws_horizontal_line(self, renderer: GfxRenderer) -> None:
        renderer.hline([(10, 90, 50)], BLUE)

    def test_draws_multiple_horizontal_lines(self, renderer: GfxRenderer) -> None:
        renderer.hline([(10, 90, 20), (10, 90, 40), (10, 90, 60)], GREEN)

    def test_draws_hline_with_tuple_color(self, renderer: GfxRenderer) -> None:
        renderer.hline([(0, 100, 50)], (0, 255, 0, 255))


class TestVline:
    """Tests for vertical line drawing."""

    def test_draws_vertical_line(self, renderer: GfxRenderer) -> None:
        renderer.vline([(50, 10, 90)], RED)

    def test_draws_multiple_vertical_lines(self, renderer: GfxRenderer) -> None:
        renderer.vline([(20, 10, 90), (40, 10, 90), (60, 10, 90)], BLUE)

    def test_draws_vline_with_tuple_color(self, renderer: GfxRenderer) -> None:
        renderer.vline([(50, 0, 100)], (255, 255, 0, 255))


class TestRectangle:
    """Tests for unfilled rectangle drawing."""

    def test_draws_rectangle(self, renderer: GfxRenderer) -> None:
        renderer.rectangle([(10, 10, 90, 90)], WHITE)

    def test_draws_multiple_rectangles(self, renderer: GfxRenderer) -> None:
        renderer.rectangle([(10, 10, 40, 40), (50, 50, 90, 90)], CYAN)

    def test_draws_rectangle_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.rectangle([(20, 20, 80, 80)], (255, 255, 255, 128))


class TestBox:
    """Tests for filled rectangle drawing."""

    def test_draws_filled_box(self, renderer: GfxRenderer) -> None:
        renderer.box([(10, 10, 90, 90)], MAGENTA)

    def test_draws_multiple_boxes(self, renderer: GfxRenderer) -> None:
        renderer.box([(10, 10, 40, 40), (50, 50, 90, 90)], YELLOW)

    def test_draws_box_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.box([(20, 20, 80, 80)], (128, 128, 128, 200))


class TestCircle:
    """Tests for unfilled circle drawing."""

    def test_draws_circle(self, renderer: GfxRenderer) -> None:
        renderer.circle([(50, 50, 30)], RED)

    def test_draws_multiple_circles(self, renderer: GfxRenderer) -> None:
        renderer.circle([(25, 25, 15), (75, 75, 15)], GREEN)

    def test_draws_circle_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.circle([(50, 50, 40)], (0, 0, 255, 180))


class TestFilledCircle:
    """Tests for filled circle drawing."""

    def test_draws_filled_circle(self, renderer: GfxRenderer) -> None:
        renderer.filled_circle([(50, 50, 30)], BLUE)

    def test_draws_multiple_filled_circles(self, renderer: GfxRenderer) -> None:
        renderer.filled_circle([(30, 30, 20), (70, 70, 20)], ORANGE)

    def test_draws_filled_circle_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.filled_circle([(50, 50, 35)], (255, 128, 0, 150))


class TestAACircle:
    """Tests for anti-aliased circle drawing."""

    def test_draws_aa_circle(self, renderer: GfxRenderer) -> None:
        renderer.aa_circle([(50, 50, 30)], WHITE)

    def test_draws_multiple_aa_circles(self, renderer: GfxRenderer) -> None:
        renderer.aa_circle([(25, 50, 15), (75, 50, 15)], GRAY)

    def test_draws_aa_circle_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.aa_circle([(50, 50, 40)], (200, 200, 200, 220))


class TestRoundedRectangle:
    """Tests for unfilled rounded rectangle drawing."""

    def test_draws_rounded_rectangle(self, renderer: GfxRenderer) -> None:
        renderer.rounded_rectangle([(10, 10, 90, 90, 10)], RED)

    def test_draws_multiple_rounded_rectangles(self, renderer: GfxRenderer) -> None:
        renderer.rounded_rectangle([(10, 10, 45, 45, 5), (55, 55, 90, 90, 8)], BLUE)

    def test_draws_rounded_rectangle_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.rounded_rectangle([(15, 15, 85, 85, 12)], (0, 255, 255, 100))


class TestRoundedBox:
    """Tests for filled rounded rectangle drawing."""

    def test_draws_rounded_box(self, renderer: GfxRenderer) -> None:
        renderer.rounded_box([(10, 10, 90, 90, 10)], GREEN)

    def test_draws_multiple_rounded_boxes(self, renderer: GfxRenderer) -> None:
        renderer.rounded_box([(10, 10, 45, 45, 5), (55, 55, 90, 90, 8)], PURPLE)

    def test_draws_rounded_box_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.rounded_box([(15, 15, 85, 85, 12)], (255, 0, 255, 150))


class TestLine:
    """Tests for line drawing."""

    def test_draws_line(self, renderer: GfxRenderer) -> None:
        renderer.line([(10, 10, 90, 90)], WHITE)

    def test_draws_multiple_lines(self, renderer: GfxRenderer) -> None:
        renderer.line([(10, 10, 90, 10), (10, 50, 90, 50), (10, 90, 90, 90)], RED)

    def test_draws_line_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.line([(0, 0, 100, 100)], (255, 255, 0, 200))


class TestAALine:
    """Tests for anti-aliased line drawing."""

    def test_draws_aa_line(self, renderer: GfxRenderer) -> None:
        renderer.aa_line([(10, 10, 90, 90)], CYAN)

    def test_draws_multiple_aa_lines(self, renderer: GfxRenderer) -> None:
        renderer.aa_line([(10, 90, 90, 10), (10, 50, 90, 50)], MAGENTA)

    def test_draws_aa_line_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.aa_line([(0, 50, 100, 50)], (128, 255, 128, 180))


class TestThickLine:
    """Tests for thick line drawing."""

    def test_draws_thick_line(self, renderer: GfxRenderer) -> None:
        renderer.thick_line([(10, 10, 90, 90, 5)], YELLOW)

    def test_draws_multiple_thick_lines(self, renderer: GfxRenderer) -> None:
        renderer.thick_line([(10, 30, 90, 30, 3), (10, 70, 90, 70, 7)], ORANGE)

    def test_draws_thick_line_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.thick_line([(20, 20, 80, 80, 10)], (0, 128, 255, 200))


class TestArc:
    """Tests for arc drawing."""

    def test_draws_arc(self, renderer: GfxRenderer) -> None:
        renderer.arc([(50, 50, 30, 0, 180)], RED)

    def test_draws_multiple_arcs(self, renderer: GfxRenderer) -> None:
        renderer.arc([(50, 50, 30, 0, 90), (50, 50, 30, 180, 270)], BLUE)

    def test_draws_arc_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.arc([(50, 50, 40, 45, 315)], (255, 128, 0, 200))


class TestEllipse:
    """Tests for unfilled ellipse drawing."""

    def test_draws_ellipse(self, renderer: GfxRenderer) -> None:
        renderer.ellipse([(50, 50, 40, 20)], GREEN)

    def test_draws_multiple_ellipses(self, renderer: GfxRenderer) -> None:
        renderer.ellipse([(30, 50, 20, 30), (70, 50, 20, 30)], PURPLE)

    def test_draws_ellipse_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.ellipse([(50, 50, 35, 25)], (100, 200, 255, 180))


class TestAAEllipse:
    """Tests for anti-aliased ellipse drawing."""

    def test_draws_aa_ellipse(self, renderer: GfxRenderer) -> None:
        renderer.aa_ellipse([(50, 50, 40, 20)], WHITE)

    def test_draws_multiple_aa_ellipses(self, renderer: GfxRenderer) -> None:
        renderer.aa_ellipse([(30, 50, 15, 25), (70, 50, 15, 25)], GRAY)

    def test_draws_aa_ellipse_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.aa_ellipse([(50, 50, 30, 20)], (200, 100, 200, 220))


class TestFilledEllipse:
    """Tests for filled ellipse drawing."""

    def test_draws_filled_ellipse(self, renderer: GfxRenderer) -> None:
        renderer.filled_ellipse([(50, 50, 40, 20)], ORANGE)

    def test_draws_multiple_filled_ellipses(self, renderer: GfxRenderer) -> None:
        renderer.filled_ellipse([(30, 50, 15, 25), (70, 50, 15, 25)], CYAN)

    def test_draws_filled_ellipse_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.filled_ellipse([(50, 50, 35, 22)], (255, 200, 100, 150))


class TestPie:
    """Tests for unfilled pie slice drawing."""

    def test_draws_pie(self, renderer: GfxRenderer) -> None:
        renderer.pie([(50, 50, 30, 0, 90)], RED)

    def test_draws_multiple_pies(self, renderer: GfxRenderer) -> None:
        renderer.pie([(50, 50, 30, 0, 120), (50, 50, 30, 180, 300)], BLUE)

    def test_draws_pie_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.pie([(50, 50, 35, 45, 270)], (128, 255, 128, 180))


class TestFilledPie:
    """Tests for filled pie slice drawing."""

    def test_draws_filled_pie(self, renderer: GfxRenderer) -> None:
        renderer.filled_pie([(50, 50, 30, 0, 90)], YELLOW)

    def test_draws_multiple_filled_pies(self, renderer: GfxRenderer) -> None:
        renderer.filled_pie([(50, 50, 30, 0, 120), (50, 50, 30, 180, 300)], MAGENTA)

    def test_draws_filled_pie_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.filled_pie([(50, 50, 35, 30, 330)], (255, 100, 100, 200))


class TestTrigon:
    """Tests for unfilled triangle drawing."""

    def test_draws_trigon(self, renderer: GfxRenderer) -> None:
        renderer.trigon([(50, 10, 10, 90, 90, 90)], WHITE)

    def test_draws_multiple_trigons(self, renderer: GfxRenderer) -> None:
        renderer.trigon([(30, 20, 10, 50, 50, 50), (70, 20, 50, 50, 90, 50)], CYAN)

    def test_draws_trigon_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.trigon([(50, 15, 15, 85, 85, 85)], (200, 200, 255, 180))


class TestAATrigon:
    """Tests for anti-aliased triangle drawing."""

    def test_draws_aa_trigon(self, renderer: GfxRenderer) -> None:
        renderer.aa_trigon([(50, 10, 10, 90, 90, 90)], GREEN)

    def test_draws_multiple_aa_trigons(self, renderer: GfxRenderer) -> None:
        renderer.aa_trigon([(30, 20, 10, 50, 50, 50), (70, 20, 50, 50, 90, 50)], RED)

    def test_draws_aa_trigon_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.aa_trigon([(50, 15, 15, 85, 85, 85)], (100, 255, 100, 200))


class TestFilledTrigon:
    """Tests for filled triangle drawing."""

    def test_draws_filled_trigon(self, renderer: GfxRenderer) -> None:
        renderer.filled_trigon([(50, 10, 10, 90, 90, 90)], BLUE)

    def test_draws_multiple_filled_trigons(self, renderer: GfxRenderer) -> None:
        renderer.filled_trigon(
            [(30, 20, 10, 50, 50, 50), (70, 20, 50, 50, 90, 50)], PURPLE
        )

    def test_draws_filled_trigon_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.filled_trigon([(50, 15, 15, 85, 85, 85)], (128, 0, 255, 180))


class TestPolygon:
    """Tests for unfilled polygon drawing."""

    def test_draws_polygon(self, renderer: GfxRenderer) -> None:
        renderer.polygon([[(10, 50), (50, 10), (90, 50), (50, 90)]], RED)

    def test_draws_multiple_polygons(self, renderer: GfxRenderer) -> None:
        renderer.polygon(
            [[(10, 10), (40, 10), (40, 40), (10, 40)], [(60, 60), (90, 60), (90, 90)]],
            GREEN,
        )

    def test_draws_polygon_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.polygon([[(20, 50), (50, 20), (80, 50), (50, 80)]], (255, 200, 0, 200))


class TestAAPolygon:
    """Tests for anti-aliased polygon drawing."""

    def test_draws_aa_polygon(self, renderer: GfxRenderer) -> None:
        renderer.aa_polygon([[(10, 50), (50, 10), (90, 50), (50, 90)]], CYAN)

    def test_draws_multiple_aa_polygons(self, renderer: GfxRenderer) -> None:
        renderer.aa_polygon(
            [[(10, 10), (40, 10), (40, 40)], [(60, 60), (90, 60), (75, 90)]],
            MAGENTA,
        )

    def test_draws_aa_polygon_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.aa_polygon(
            [[(20, 50), (50, 20), (80, 50), (50, 80)]], (100, 255, 255, 180)
        )


class TestFilledPolygon:
    """Tests for filled polygon drawing."""

    def test_draws_filled_polygon(self, renderer: GfxRenderer) -> None:
        renderer.filled_polygon([[(10, 50), (50, 10), (90, 50), (50, 90)]], YELLOW)

    def test_draws_multiple_filled_polygons(self, renderer: GfxRenderer) -> None:
        renderer.filled_polygon(
            [[(10, 10), (40, 10), (40, 40), (10, 40)], [(60, 60), (90, 60), (75, 90)]],
            ORANGE,
        )

    def test_draws_filled_polygon_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.filled_polygon(
            [[(20, 50), (50, 20), (80, 50), (50, 80)]], (255, 128, 64, 200)
        )


class TestTexturedPolygon:
    """Tests for textured polygon drawing."""

    @pytest.fixture
    def texture_surface(self) -> Generator[Any, None, None]:
        """Create a simple test surface for texture testing."""
        surface_ptr = sdl2.SDL_CreateRGBSurface(
            0,
            32,
            32,
            32,
            0x00FF0000,
            0x0000FF00,
            0x000000FF,
            0xFF000000,
        )
        if surface_ptr:
            surface = surface_ptr.contents
            color = sdl2.SDL_MapRGBA(surface.format, 255, 128, 64, 255)
            sdl2.SDL_FillRect(surface_ptr, None, color)  # type: ignore[arg-type]
        yield surface_ptr
        if surface_ptr:
            sdl2.SDL_FreeSurface(surface_ptr)

    def test_draws_textured_polygon(
        self, renderer: GfxRenderer, texture_surface: Any
    ) -> None:
        points = [(10, 50), (50, 10), (90, 50), (50, 90)]
        renderer.textured_polygon([(points, texture_surface, 0, 0)])

    def test_draws_textured_polygon_with_offset(
        self, renderer: GfxRenderer, texture_surface: Any
    ) -> None:
        points = [(20, 20), (80, 20), (80, 80), (20, 80)]
        renderer.textured_polygon([(points, texture_surface, 10, 10)])

    def test_draws_multiple_textured_polygons(
        self, renderer: GfxRenderer, texture_surface: Any
    ) -> None:
        poly1 = [(10, 10), (40, 10), (40, 40), (10, 40)]
        poly2 = [(60, 60), (90, 60), (90, 90), (60, 90)]
        renderer.textured_polygon(
            [
                (poly1, texture_surface, 0, 0),
                (poly2, texture_surface, 60, 60),
            ]
        )


class TestBezier:
    """Tests for Bezier curve drawing."""

    def test_draws_bezier(self, renderer: GfxRenderer) -> None:
        renderer.bezier([(10, [(10, 50), (30, 10), (70, 90), (90, 50)])], WHITE)

    def test_draws_multiple_beziers(self, renderer: GfxRenderer) -> None:
        renderer.bezier(
            [
                (20, [(10, 30), (50, 10), (90, 30)]),
                (20, [(10, 70), (50, 90), (90, 70)]),
            ],
            GRAY,
        )

    def test_draws_bezier_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.bezier(
            [(15, [(10, 50), (25, 10), (50, 90), (75, 10), (90, 50)])],
            (200, 200, 200, 180),
        )


class TestCharacter:
    """Tests for single character drawing."""

    def test_draws_character(self, renderer: GfxRenderer) -> None:
        renderer.character([(50, 50, "A")], WHITE)

    def test_draws_multiple_characters(self, renderer: GfxRenderer) -> None:
        renderer.character([(10, 50, "H"), (20, 50, "i"), (30, 50, "!")], GREEN)

    def test_draws_character_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.character([(50, 50, "X")], (255, 255, 0, 200))


class TestString:
    """Tests for string drawing."""

    def test_draws_string(self, renderer: GfxRenderer) -> None:
        renderer.string([(10, 50, "Hello")], WHITE)

    def test_draws_multiple_strings(self, renderer: GfxRenderer) -> None:
        renderer.string([(10, 30, "Line 1"), (10, 50, "Line 2")], CYAN)

    def test_draws_string_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.string([(10, 50, "Test123")], (128, 255, 128, 200))


class TestFillColor:
    """Tests for fill color functionality."""

    def test_fills_with_color(self, renderer: GfxRenderer) -> None:
        renderer.fill_color(BLACK)

    def test_fills_with_tuple_color(self, renderer: GfxRenderer) -> None:
        renderer.fill_color((64, 64, 64))

    def test_fills_with_alpha(self, renderer: GfxRenderer) -> None:
        renderer.fill_color((128, 128, 128, 255))

    def test_fills_with_none_uses_current_color(self, renderer: GfxRenderer) -> None:
        renderer.color = sdl2.ext.Color(100, 100, 100, 255)
        renderer.fill_color(None)


class TestClip:
    """Tests for clip rectangle property."""

    def test_get_clip_returns_tuple(self, renderer: GfxRenderer) -> None:
        clip = renderer.clip
        assert isinstance(clip, tuple)
        assert len(clip) == 4

    def test_set_and_get_clip(self, renderer: GfxRenderer) -> None:
        renderer.clip = (10, 20, 50, 60)
        clip = renderer.clip
        assert clip == (10, 20, 50, 60)

    def test_clip_restricts_drawing_area(self, renderer: GfxRenderer) -> None:
        renderer.clip = (25, 25, 50, 50)
        renderer.box([(0, 0, 100, 100)], RED)
        clip = renderer.clip
        assert clip == (25, 25, 50, 50)
