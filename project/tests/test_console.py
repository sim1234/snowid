"""Tests for ConsoleService and BufferedConsole classes."""

import pytest

from gamepart.gui.console import BufferedConsole, ConsoleService


class TestBufferedConsole:
    """Test BufferedConsole class."""

    def test_initialization(self):
        """Test BufferedConsole initialization."""
        console = BufferedConsole()
        assert console.output_buffer.getvalue() == ""

    def test_write(self):
        """Test writing to output buffer."""
        console = BufferedConsole()
        console.write("hello")
        console.write(" world")
        assert console.output_buffer.getvalue() == "hello world"

    def test_push_line_simple(self):
        """Test pushing a simple line."""
        console = BufferedConsole()
        more = console.push_line("x = 1")
        assert more is False
        assert "x = 1\n" in console.output_buffer.getvalue()

    def test_push_line_with_prefix(self):
        """Test pushing a line with custom prefix."""
        console = BufferedConsole()
        console.push_line("x = 1", prefix="... ")
        output = console.output_buffer.getvalue()
        assert output.startswith("... x = 1\n")

    def test_push_line_multiline_statement(self):
        """Test pushing incomplete multiline statement."""
        console = BufferedConsole()
        more = console.push_line("def foo():")
        assert more is True

    def test_push_line_with_output(self):
        """Test pushing a line that produces output."""
        console = BufferedConsole()
        console.push_line("print('hello')")
        output = console.output_buffer.getvalue()
        assert "hello" in output


class TestConsoleService:
    """Test ConsoleService class."""

    @pytest.fixture
    def console_service(self):
        """Create a ConsoleService for testing."""
        shell = BufferedConsole()
        return ConsoleService(shell)

    def test_initialization(self, console_service: ConsoleService):
        """Test ConsoleService initialization."""
        assert console_service.prompt1 == ">>> "
        assert console_service.prompt2 == "... "
        assert console_service.prompt == ">>> "
        assert console_service.input_buffer == ""
        assert console_service.input_buffer2 == ""
        assert console_service.input_index == 0
        assert console_service.history == []
        assert console_service.history_index is None

    def test_get_all_buffer_empty(self, console_service: ConsoleService):
        """Test get_all_buffer with empty input."""
        buffer = console_service.get_all_buffer()
        assert buffer == ">>> "

    def test_get_buffer_start_empty(self, console_service: ConsoleService):
        """Test get_buffer_start with empty input."""
        buffer = console_service.get_buffer_start()
        assert buffer == ">>> "

    def test_get_buffer_end_empty(self, console_service: ConsoleService):
        """Test get_buffer_end with empty input."""
        buffer = console_service.get_buffer_end()
        assert buffer == ""

    def test_enter_text(self, console_service: ConsoleService):
        """Test entering text."""
        console_service.enter_text("hello")
        assert console_service.input_buffer == "hello"
        assert console_service.input_index == 5

    def test_enter_text_multiple(self, console_service: ConsoleService):
        """Test entering multiple text segments."""
        console_service.enter_text("hello")
        console_service.enter_text(" world")
        assert console_service.input_buffer == "hello world"
        assert console_service.input_index == 11

    def test_enter_text_at_position(self, console_service: ConsoleService):
        """Test entering text at a specific position."""
        console_service.enter_text("helloworld")
        console_service.input_index = 5
        console_service.enter_text(" ")
        assert console_service.input_buffer == "hello world"
        assert console_service.input_index == 6

    def test_get_buffer_with_text(self, console_service: ConsoleService):
        """Test buffer methods with text."""
        console_service.enter_text("hello")
        console_service.input_index = 3
        assert console_service.get_buffer_start() == ">>> hel"
        assert console_service.get_buffer_end() == "lo"
        assert console_service.get_all_buffer() == ">>> hello"

    def test_press_backspace(self, console_service: ConsoleService):
        """Test backspace."""
        console_service.enter_text("hello")
        console_service.press_backspace()
        assert console_service.input_buffer == "hell"
        assert console_service.input_index == 4

    def test_press_backspace_multiple(self, console_service: ConsoleService):
        """Test backspace with amount."""
        console_service.enter_text("hello")
        console_service.press_backspace(3)
        assert console_service.input_buffer == "he"
        assert console_service.input_index == 2

    def test_press_backspace_at_start(self, console_service: ConsoleService):
        """Test backspace at start of buffer."""
        console_service.enter_text("hello")
        console_service.input_index = 0
        console_service.press_backspace()
        assert console_service.input_buffer == "hello"
        assert console_service.input_index == 0

    def test_press_backspace_in_middle(self, console_service: ConsoleService):
        """Test backspace in middle of buffer."""
        console_service.enter_text("hello")
        console_service.input_index = 3
        console_service.press_backspace()
        assert console_service.input_buffer == "helo"
        assert console_service.input_index == 2

    def test_press_delete(self, console_service: ConsoleService):
        """Test delete."""
        console_service.enter_text("hello")
        console_service.input_index = 0
        console_service.press_delete()
        assert console_service.input_buffer == "ello"
        assert console_service.input_index == 0

    def test_press_delete_multiple(self, console_service: ConsoleService):
        """Test delete with amount."""
        console_service.enter_text("hello")
        console_service.input_index = 0
        console_service.press_delete(3)
        assert console_service.input_buffer == "lo"
        assert console_service.input_index == 0

    def test_press_delete_at_end(self, console_service: ConsoleService):
        """Test delete at end of buffer."""
        console_service.enter_text("hello")
        console_service.press_delete()
        assert console_service.input_buffer == "hello"
        assert console_service.input_index == 5

    def test_press_delete_in_middle(self, console_service: ConsoleService):
        """Test delete in middle of buffer."""
        console_service.enter_text("hello")
        console_service.input_index = 2
        console_service.press_delete()
        assert console_service.input_buffer == "helo"
        assert console_service.input_index == 2

    def test_press_left(self, console_service: ConsoleService):
        """Test left arrow key."""
        console_service.enter_text("hello")
        console_service.press_left()
        assert console_service.input_index == 4

    def test_press_left_multiple(self, console_service: ConsoleService):
        """Test left arrow key with amount."""
        console_service.enter_text("hello")
        console_service.press_left(3)
        assert console_service.input_index == 2

    def test_press_left_at_start(self, console_service: ConsoleService):
        """Test left arrow key at start."""
        console_service.enter_text("hello")
        console_service.input_index = 0
        console_service.press_left()
        assert console_service.input_index == 0

    def test_press_right(self, console_service: ConsoleService):
        """Test right arrow key."""
        console_service.enter_text("hello")
        console_service.input_index = 0
        console_service.press_right()
        assert console_service.input_index == 1

    def test_press_right_multiple(self, console_service: ConsoleService):
        """Test right arrow key with amount."""
        console_service.enter_text("hello")
        console_service.input_index = 0
        console_service.press_right(3)
        assert console_service.input_index == 3

    def test_press_right_at_end(self, console_service: ConsoleService):
        """Test right arrow key at end."""
        console_service.enter_text("hello")
        console_service.press_right()
        assert console_service.input_index == 5

    def test_press_home(self, console_service: ConsoleService):
        """Test home key."""
        console_service.enter_text("hello")
        console_service.press_home()
        assert console_service.input_index == 0

    def test_press_end(self, console_service: ConsoleService):
        """Test end key."""
        console_service.enter_text("hello")
        console_service.input_index = 0
        console_service.press_end()
        assert console_service.input_index == 5

    def test_press_enter(self, console_service: ConsoleService):
        """Test enter key."""
        console_service.enter_text("x = 1")
        console_service.press_enter()
        assert console_service.input_buffer == ""
        assert console_service.input_index == 0
        assert console_service.history == ["x = 1"]

    def test_press_enter_empty(self, console_service: ConsoleService):
        """Test enter key with empty input."""
        console_service.press_enter()
        assert console_service.input_buffer == ""
        assert console_service.history == []

    def test_press_enter_multiline(self, console_service: ConsoleService):
        """Test enter key starts multiline mode."""
        console_service.enter_text("def foo():")
        console_service.press_enter()
        assert console_service.prompt == "... "

    def test_press_enter_completes_multiline(self, console_service: ConsoleService):
        """Test completing multiline statement."""
        console_service.enter_text("def foo():")
        console_service.press_enter()
        assert console_service.prompt == "... "
        console_service.enter_text("    pass")
        console_service.press_enter()
        console_service.press_enter()
        assert console_service.prompt == ">>> "

    def test_history_navigation_up(self, console_service: ConsoleService):
        """Test up arrow navigates history."""
        console_service.enter_text("first")
        console_service.press_enter()
        console_service.enter_text("second")
        console_service.press_enter()

        console_service.press_up()
        assert console_service.input_buffer == "second"
        assert console_service.history_index == 1

        console_service.press_up()
        assert console_service.input_buffer == "first"
        assert console_service.history_index == 0

    def test_history_navigation_up_at_start(self, console_service: ConsoleService):
        """Test up arrow at start of history."""
        console_service.enter_text("first")
        console_service.press_enter()

        console_service.press_up()
        assert console_service.input_buffer == "first"
        console_service.press_up()
        assert console_service.input_buffer == "first"
        assert console_service.history_index == 0

    def test_history_navigation_down(self, console_service: ConsoleService):
        """Test down arrow navigates history."""
        console_service.enter_text("first")
        console_service.press_enter()
        console_service.enter_text("second")
        console_service.press_enter()

        console_service.press_up()
        console_service.press_up()
        assert console_service.input_buffer == "first"

        console_service.press_down()
        assert console_service.input_buffer == "second"
        assert console_service.history_index == 1

    def test_history_navigation_down_restores_current(
        self, console_service: ConsoleService
    ):
        """Test down arrow restores current input."""
        console_service.enter_text("first")
        console_service.press_enter()

        console_service.enter_text("current")
        console_service.press_up()
        assert console_service.input_buffer == "first"

        console_service.press_down()
        assert console_service.input_buffer == "current"
        assert console_service.history_index is None

    def test_history_navigation_up_empty(self, console_service: ConsoleService):
        """Test up arrow with no history."""
        console_service.press_up()
        assert console_service.input_buffer == ""
        assert console_service.history_index is None

    def test_history_navigation_down_not_in_history(
        self, console_service: ConsoleService
    ):
        """Test down arrow when not in history mode."""
        console_service.enter_text("test")
        console_service.press_down()
        assert console_service.input_buffer == "test"
        assert console_service.history_index is None

    def test_exit_history(self, console_service: ConsoleService):
        """Test exit_history resets history_index."""
        console_service.enter_text("first")
        console_service.press_enter()
        console_service.press_up()
        assert console_service.history_index == 0

        console_service.exit_history()
        assert console_service.history_index is None

    def test_enter_text_exits_history(self, console_service: ConsoleService):
        """Test entering text exits history mode."""
        console_service.enter_text("first")
        console_service.press_enter()
        console_service.press_up()
        assert console_service.history_index == 0

        console_service.enter_text("x")
        assert console_service.history_index is None

    def test_press_enter_uses_history_selection(self, console_service: ConsoleService):
        """Test enter key uses selected history item."""
        console_service.enter_text("x = 1")
        console_service.press_enter()
        console_service.enter_text("y = 2")
        console_service.press_enter()

        console_service.press_up()
        console_service.press_up()
        console_service.press_enter()

        assert "x = 1" in console_service.history
        assert console_service.history[-1] == "x = 1"

    def test_cursor_movement_sequence(self, console_service: ConsoleService):
        """Test a sequence of cursor movements."""
        console_service.enter_text("hello world")
        console_service.press_home()
        assert console_service.input_index == 0

        console_service.press_right(6)
        assert console_service.input_index == 6

        console_service.press_backspace()
        assert console_service.input_buffer == "helloworld"

        console_service.enter_text(" ")
        assert console_service.input_buffer == "hello world"

    def test_editing_sequence(self, console_service: ConsoleService):
        """Test a sequence of edit operations."""
        console_service.enter_text("def foo():")
        console_service.press_enter()
        console_service.enter_text("    return 1")
        console_service.press_enter()
        console_service.press_enter()

        # Empty line not added to history, only 2 entries
        assert len(console_service.history) == 2
        assert console_service.history == ["def foo():", "    return 1"]
        assert console_service.prompt == ">>> "
