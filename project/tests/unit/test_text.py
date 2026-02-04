"""Tests for Text component."""

from gamepart.gui.text import Text


class TestText:
    def test_initialization_empty(self) -> None:
        text = Text()
        assert text.text == ""
        assert text.font == "console"
        assert text.font_size == 12
        assert text.color == (0, 0, 0, 255)
        assert text.x == 0
        assert text.y == 0

    def test_initialization_with_text(self) -> None:
        text = Text(text="Hello World")
        assert text.text == "Hello World"

    def test_initialization_with_position(self) -> None:
        text = Text(x=100, y=50, text="Test")
        assert text.x == 100
        assert text.y == 50

    def test_font_properties(self) -> None:
        text = Text(
            text="Test",
            font="console",
            font_size=16,
            color=(200, 100, 50, 255),
        )
        assert text.font == "console"
        assert text.font_size == 16
        assert text.color == (200, 100, 50, 255)

    def test_text_property_updates_text(self) -> None:
        text = Text(text="Initial")
        assert text.text == "Initial"

        text.text = "Changed"
        assert text.text == "Changed"

    def test_background_color(self) -> None:
        text = Text(text="Test", background_color=(0, 0, 0, 128))
        assert text.background_color == (0, 0, 0, 128)

    def test_max_width(self) -> None:
        text = Text(text="Long text", max_width=200)
        assert text.max_width == 200
