"""Tests for Button component."""

from gamepart.gui.button import ButtonMixin
from gamepart.gui.text import Text


class Button(ButtonMixin, Text):
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
