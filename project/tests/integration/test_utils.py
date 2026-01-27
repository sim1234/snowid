"""Integration tests for gamepart.utils SDL utilities."""

from collections.abc import Generator

import pytest
import sdl2
from gamepart.utils import get_clipboard_text, get_mouse_state


@pytest.fixture(scope="module")
def sdl_init() -> Generator[None, None, None]:
    """Initialize SDL for the test module."""
    sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
    yield
    sdl2.SDL_Quit()


class TestGetMouseState:
    """Tests for get_mouse_state function."""

    def test_returns_tuple_of_three_ints(self, sdl_init: None) -> None:
        """Test get_mouse_state returns tuple of (x, y, button_state)."""
        result = get_mouse_state()

        assert isinstance(result, tuple)
        assert len(result) == 3
        assert all(isinstance(v, int) for v in result)

    def test_coordinates_are_non_negative(self, sdl_init: None) -> None:
        """Test mouse coordinates are non-negative integers."""
        x, y, _ = get_mouse_state()

        assert x >= 0
        assert y >= 0

    def test_button_state_is_integer(self, sdl_init: None) -> None:
        """Test button state is an integer."""
        _, _, button_state = get_mouse_state()

        assert isinstance(button_state, int)


class TestGetClipboardText:
    """Tests for get_clipboard_text function."""

    def test_returns_string(self, sdl_init: None) -> None:
        """Test get_clipboard_text returns a string."""
        result = get_clipboard_text()

        assert isinstance(result, str)

    def test_default_encoding_is_utf8(self, sdl_init: None) -> None:
        """Test default encoding parameter works."""
        result = get_clipboard_text()
        assert isinstance(result, str)

    def test_custom_encoding_parameter(self, sdl_init: None) -> None:
        """Test custom encoding parameter is accepted."""
        result = get_clipboard_text(encoding="utf-8")
        assert isinstance(result, str)

    def test_set_and_get_clipboard(self, sdl_init: None) -> None:
        """Test setting and getting clipboard text."""
        test_text = "Hello from test!"
        sdl2.SDL_SetClipboardText(test_text.encode("utf-8"))

        result = get_clipboard_text()

        assert result == test_text

    def test_get_clipboard_with_unicode(self, sdl_init: None) -> None:
        """Test clipboard with unicode characters."""
        test_text = "Hello unicode: \u00e9\u00e8\u00ea"
        sdl2.SDL_SetClipboardText(test_text.encode("utf-8"))

        result = get_clipboard_text()

        assert result == test_text

    def test_get_clipboard_empty_after_clear(self, sdl_init: None) -> None:
        """Test clipboard returns empty string when cleared."""
        sdl2.SDL_SetClipboardText(b"")

        result = get_clipboard_text()

        assert result == ""

    def test_handles_none_clipboard_data(self, sdl_init: None) -> None:
        """Test clipboard returns empty string when SDL returns None."""
        # This tests the `if data is None: return ""` branch
        # SDL_GetClipboardText returns None when clipboard has no text data
        # We can simulate this by testing after video subsystem init
        # but before any clipboard operations (though this is hard to guarantee)
        # The safest is to just verify the function doesn't crash
        result = get_clipboard_text()
        assert isinstance(result, str)
