"""Tests for Image component."""

from gamepart.gui.image import Image


class TestImage:
    def test_initialization_empty(self) -> None:
        image = Image()
        assert image.sprite is None
        assert image.x == 0
        assert image.y == 0
        assert image.width == 0
        assert image.height == 0

    def test_initialization_with_position(self) -> None:
        image = Image(x=100, y=50)
        assert image.x == 100
        assert image.y == 50

    def test_initialization_with_size(self) -> None:
        image = Image(width=64, height=32)
        assert image.width == 64
        assert image.height == 32

    def test_all_constructor_params(self) -> None:
        image = Image(x=10, y=20, width=100, height=50)
        assert image.x == 10
        assert image.y == 20
        assert image.width == 100
        assert image.height == 50
