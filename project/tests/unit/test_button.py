"""Tests for Button component."""

from typing import cast

import sdl2
from gamepart.gui.button import OnClickMixin, OnHoverMixin, PrettyButton
from gamepart.gui.system import GUISystem
from gamepart.gui.text import Text


class Button(OnClickMixin, OnHoverMixin, Text):
    pass


class TestButton:
    def test_initialization_empty(self) -> None:
        button = Button()
        assert button.text == ""
        assert button.on_click is None
        assert button.font == "console"
        assert button.font_size == 12
        assert button.color == (0, 0, 0, 255)
        assert button.background_color is None
        assert button.hovered is False

    def test_initialization_with_text(self) -> None:
        button = Button(text="Click Me")
        assert button.text == "Click Me"

    def test_initialization_with_callback(self) -> None:
        called = False

        def callback() -> None:
            nonlocal called
            called = True

        button = Button("Test", on_click=callback)
        assert button.on_click is not None
        button.on_click()
        assert called

    def test_position_and_size(self) -> None:
        button = Button()
        button.x = 100
        button.y = 50
        button.width = 200
        button.height = 40

        assert button.x == 100
        assert button.y == 50
        assert button.width == 200
        assert button.height == 40

    def test_contains_point(self) -> None:
        button = Button()
        button.x = 100
        button.y = 50
        button.width = 200
        button.height = 40

        assert button.contains_point(150, 70) is True
        assert button.contains_point(100, 50) is True
        assert button.contains_point(299, 89) is True
        assert button.contains_point(99, 50) is False
        assert button.contains_point(300, 50) is False
        assert button.contains_point(150, 49) is False
        assert button.contains_point(150, 90) is False

    def test_contains_point_with_parent(self) -> None:
        from gamepart.gui.panel import Panel

        panel = Panel()
        panel.x = 100
        panel.y = 50

        button = Button()
        button.x = 10
        button.y = 10
        button.width = 50
        button.height = 30
        panel.add_child(button)

        # Button absolute position is (110, 60)
        assert button.contains_point(120, 70) is True
        assert button.contains_point(109, 60) is False


class TestPrettyButton:
    def test_initialization_stores_text_and_colors(self) -> None:
        label = Text(x=0, y=0, text="Ok", font="sans", font_size=16)
        btn = PrettyButton(
            text=label,
            hover_color=(255, 255, 255, 255),
            hover_background_color=(80, 80, 80, 255),
        )
        assert btn.text is label
        assert btn.base_color == label.color
        assert btn.base_background_color == label.background_color
        assert btn.hover_color == (255, 255, 255, 255)
        assert btn.hover_background_color == (80, 80, 80, 255)
        assert label in btn.children
        assert btn.background_color == btn.base_background_color

    def test_initialization_clears_text_background_color(self) -> None:
        label = Text(
            x=0,
            y=0,
            text="Ok",
            font="sans",
            font_size=16,
            background_color=(40, 40, 40, 255),
        )
        btn = PrettyButton(text=label)
        assert label.background_color is None
        assert btn.background_color == (40, 40, 40, 255)

    def test_on_click_callback(self) -> None:
        label = Text(x=0, y=0, text="Click", font="sans", font_size=16)
        called = False

        def callback() -> None:
            nonlocal called
            called = True

        btn = PrettyButton(text=label, on_click=callback)
        btn.width = 50
        btn.height = 30
        assert btn.on_click is not None
        btn.on_click()
        assert called

    def test_hover_sets_colors(self) -> None:
        label = Text(
            x=0,
            y=0,
            text="Hover",
            font="sans",
            font_size=16,
            color=(0, 0, 0, 255),
            background_color=None,
        )
        btn = PrettyButton(
            text=label,
            hover_color=(255, 255, 255, 255),
            hover_background_color=(80, 80, 80, 255),
        )
        btn.base_background_color = (40, 40, 40, 255)
        btn.background_color = (40, 40, 40, 255)

        class FakeEvent:
            pass

        event = cast(sdl2.SDL_Event, FakeEvent())
        btn._on_hover(event)
        assert btn.text.color == (255, 255, 255, 255)
        assert btn.background_color == (80, 80, 80, 255)

        btn._on_unhover(event)
        assert btn.text.color == (0, 0, 0, 255)
        assert btn.background_color == (40, 40, 40, 255)

    def test_contains_point(self) -> None:
        label = Text(x=0, y=0, text="Hit", font="sans", font_size=16)
        btn = PrettyButton(text=label)
        btn.x = 10
        btn.y = 20
        btn.width = 100
        btn.height = 40

        assert btn.contains_point(60, 40) is True
        assert btn.contains_point(10, 20) is True
        assert btn.contains_point(109, 59) is True
        assert btn.contains_point(9, 20) is False
        assert btn.contains_point(110, 20) is False
        assert btn.contains_point(60, 19) is False
        assert btn.contains_point(60, 60) is False

    def test_fit_to_text_padding(self) -> None:
        class StubText(Text):
            def fit_to_text(self) -> None:
                pass

        label = StubText(x=0, y=0, text="X", font="sans", font_size=16)
        label.width = 10
        label.height = 16
        label.gui_system = cast(GUISystem, object())

        btn = PrettyButton(text=label)
        btn.fit_to_text(padding=(5, 10, 15, 20))

        assert label.x == 20
        assert label.y == 5
        assert btn.width == 10 + 10 + 20
        assert btn.height == 5 + 16 + 15
