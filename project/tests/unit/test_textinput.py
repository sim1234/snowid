"""Tests for TextInput component."""

import pytest
from gamepart.gui.textinput import TextInput


class TestTextInput:
    def test_initialization(self) -> None:
        text_input = TextInput()
        assert text_input.stored_text == ""
        assert text_input.cursor_index == 0
        assert text_input.font == "console"
        assert text_input.font_size == 12
        assert text_input.color == (255, 255, 255, 255)
        assert text_input.background_color is None
        assert text_input.focused is False
        assert text_input.on_submit is None


class TestTextInputEditing:
    @pytest.fixture
    def text_input(self) -> TextInput:
        return TextInput()

    def test_enter_text(self, text_input: TextInput) -> None:
        text_input.enter_text("hello")
        assert text_input.stored_text == "hello"
        assert text_input.cursor_index == 5

    def test_enter_text_multiple(self, text_input: TextInput) -> None:
        text_input.enter_text("hello")
        text_input.enter_text(" world")
        assert text_input.stored_text == "hello world"
        assert text_input.cursor_index == 11

    def test_enter_text_at_position(self, text_input: TextInput) -> None:
        text_input.enter_text("helloworld")
        text_input.cursor_index = 5
        text_input.enter_text(" ")
        assert text_input.stored_text == "hello world"
        assert text_input.cursor_index == 6


class TestTextInputBackspace:
    @pytest.fixture
    def text_input(self) -> TextInput:
        ti = TextInput()
        ti.enter_text("hello")
        return ti

    def test_press_backspace(self, text_input: TextInput) -> None:
        text_input.press_backspace()
        assert text_input.stored_text == "hell"
        assert text_input.cursor_index == 4

    def test_press_backspace_multiple(self, text_input: TextInput) -> None:
        text_input.press_backspace(3)
        assert text_input.stored_text == "he"
        assert text_input.cursor_index == 2

    def test_press_backspace_at_start(self, text_input: TextInput) -> None:
        text_input.cursor_index = 0
        text_input.press_backspace()
        assert text_input.stored_text == "hello"
        assert text_input.cursor_index == 0

    def test_press_backspace_in_middle(self, text_input: TextInput) -> None:
        text_input.cursor_index = 3
        text_input.press_backspace()
        assert text_input.stored_text == "helo"
        assert text_input.cursor_index == 2


class TestTextInputDelete:
    @pytest.fixture
    def text_input(self) -> TextInput:
        ti = TextInput()
        ti.enter_text("hello")
        return ti

    def test_press_delete(self, text_input: TextInput) -> None:
        text_input.cursor_index = 0
        text_input.press_delete()
        assert text_input.stored_text == "ello"
        assert text_input.cursor_index == 0

    def test_press_delete_multiple(self, text_input: TextInput) -> None:
        text_input.cursor_index = 0
        text_input.press_delete(3)
        assert text_input.stored_text == "lo"
        assert text_input.cursor_index == 0

    def test_press_delete_at_end(self, text_input: TextInput) -> None:
        text_input.press_delete()
        assert text_input.stored_text == "hello"
        assert text_input.cursor_index == 5

    def test_press_delete_in_middle(self, text_input: TextInput) -> None:
        text_input.cursor_index = 2
        text_input.press_delete()
        assert text_input.stored_text == "helo"
        assert text_input.cursor_index == 2


class TestTextInputNavigation:
    @pytest.fixture
    def text_input(self) -> TextInput:
        ti = TextInput()
        ti.enter_text("hello")
        return ti

    def test_press_left(self, text_input: TextInput) -> None:
        text_input.press_left()
        assert text_input.cursor_index == 4

    def test_press_left_multiple(self, text_input: TextInput) -> None:
        text_input.press_left(3)
        assert text_input.cursor_index == 2

    def test_press_left_at_start(self, text_input: TextInput) -> None:
        text_input.cursor_index = 0
        text_input.press_left()
        assert text_input.cursor_index == 0

    def test_press_right(self, text_input: TextInput) -> None:
        text_input.cursor_index = 0
        text_input.press_right()
        assert text_input.cursor_index == 1

    def test_press_right_multiple(self, text_input: TextInput) -> None:
        text_input.cursor_index = 0
        text_input.press_right(3)
        assert text_input.cursor_index == 3

    def test_press_right_at_end(self, text_input: TextInput) -> None:
        text_input.press_right()
        assert text_input.cursor_index == 5

    def test_press_home(self, text_input: TextInput) -> None:
        text_input.press_home()
        assert text_input.cursor_index == 0

    def test_press_end(self, text_input: TextInput) -> None:
        text_input.cursor_index = 0
        text_input.press_end()
        assert text_input.cursor_index == 5


class TestTextInputSubmit:
    def test_press_enter_calls_on_submit(self) -> None:
        text_input = TextInput()
        text_input.enter_text("test input")
        submitted_value = None

        def on_submit(value: str) -> None:
            nonlocal submitted_value
            submitted_value = value

        text_input.on_submit = on_submit
        text_input.press_enter()

        assert submitted_value == "test input"

    def test_press_enter_without_callback(self) -> None:
        text_input = TextInput()
        text_input.enter_text("test")
        text_input.press_enter()  # Should not raise
