"""Tests for ConsoleService, BufferedConsole, and Console classes."""

import pytest
from gamepart.gui.console import BufferedConsole, Console, ConsoleService


class TestConsoleWrapLines:
    """Test Console.wrap_lines method."""

    @pytest.fixture
    def console(self) -> Console:
        return Console()

    def test_empty_string_unchanged(self, console: Console) -> None:
        assert console.wrap_lines("") == ""

    def test_short_line_unchanged(self, console: Console) -> None:
        console.wrap_width = 80
        assert console.wrap_lines("hello") == "hello"

    def test_line_at_exact_width_unchanged(self, console: Console) -> None:
        console.wrap_width = 5
        assert console.wrap_lines("12345") == "12345"

    def test_long_line_split(self, console: Console) -> None:
        console.wrap_width = 5
        assert console.wrap_lines("1234567890") == "12345\n67890"

    def test_long_line_split_with_remainder(self, console: Console) -> None:
        console.wrap_width = 4
        assert console.wrap_lines("1234567") == "1234\n567"

    def test_multiple_lines_each_wrapped(self, console: Console) -> None:
        console.wrap_width = 3
        result = console.wrap_lines("abc\ndefgh\nij")
        assert result == "abc\ndef\ngh\nij"

    def test_preserves_existing_newlines(self, console: Console) -> None:
        console.wrap_width = 80
        result = console.wrap_lines("line1\nline2\nline3")
        assert result == "line1\nline2\nline3"

    def test_explicit_wrap_width_none_uses_fallback(self, console: Console) -> None:
        console.wrap_width = None
        console.width = 640
        console.font_size = 12
        wrap_width = int(640 / 12 * 1.7)
        long_line = "x" * (wrap_width + 10)
        result = console.wrap_lines(long_line)
        lines = result.split("\n")
        assert len(lines) >= 2
        assert all(len(line) <= wrap_width for line in lines)

    def test_wrap_width_zero_single_char_lines(self, console: Console) -> None:
        console.wrap_width = 1
        assert console.wrap_lines("ab") == "a\nb"


class TestConsoleWithWrapIntegration:
    """Test that ConsoleService output works with Console.wrap_lines."""

    def test_submit_and_wrap_produces_no_line_over_width(self) -> None:
        console = Console()
        console.wrap_width = 40
        console.service.submit("x = 1")
        console.service.submit("print('hello world')")
        raw = console.service.get_history_output()
        wrapped = console.wrap_lines(raw)
        for line in wrapped.split("\n"):
            assert len(line) <= 40

    def test_long_output_wrapped(self) -> None:
        console = Console()
        console.wrap_width = 20
        console.service.submit("'a' * 50")
        raw = console.service.get_history_output()
        wrapped = console.wrap_lines(raw)
        lines = wrapped.split("\n")
        assert len(lines) >= 2
        for line in lines:
            assert len(line) <= 20


class TestBufferedConsole:
    """Test BufferedConsole class."""

    def test_initialization(self) -> None:
        """Test BufferedConsole initialization."""
        console = BufferedConsole()
        assert console.output_buffer.getvalue() == ""

    def test_write(self) -> None:
        """Test writing to output buffer."""
        console = BufferedConsole()
        console.write("hello")
        console.write(" world")
        assert console.output_buffer.getvalue() == "hello world"

    def test_push_line_simple(self) -> None:
        """Test pushing a simple line."""
        console = BufferedConsole()
        more = console.push_line("x = 1")
        assert more is False
        assert "x = 1\n" in console.output_buffer.getvalue()

    def test_push_line_with_prefix(self) -> None:
        """Test pushing a line with custom prefix."""
        console = BufferedConsole()
        console.push_line("x = 1", prefix="... ")
        output = console.output_buffer.getvalue()
        assert output.startswith("... x = 1\n")

    def test_push_line_multiline_statement(self) -> None:
        """Test pushing incomplete multiline statement."""
        console = BufferedConsole()
        more = console.push_line("def foo():")
        assert more is True

    def test_push_line_with_output(self) -> None:
        """Test pushing a line that produces output."""
        console = BufferedConsole()
        console.push_line("print('hello')")
        output = console.output_buffer.getvalue()
        assert "hello" in output


class TestConsoleService:
    """Test ConsoleService class."""

    @pytest.fixture
    def console_service(self) -> ConsoleService:
        """Create a ConsoleService for testing."""
        shell = BufferedConsole()
        return ConsoleService(shell)

    def test_initialization(self, console_service: ConsoleService) -> None:
        """Test ConsoleService initialization."""
        assert console_service.prompt1 == ">>> "
        assert console_service.prompt2 == "... "
        assert console_service.prompt == ">>> "
        assert console_service.input_buffer == ""
        assert console_service.history == []
        assert console_service.history_index is None

    def test_get_history_output_empty(self, console_service: ConsoleService) -> None:
        """Test get_history_output with empty output."""
        output = console_service.get_history_output()
        assert output == ""

    def test_get_history_output_with_content(
        self, console_service: ConsoleService
    ) -> None:
        """Test get_history_output after submitting commands."""
        console_service.submit("x = 1")
        output = console_service.get_history_output()
        assert ">>> x = 1" in output

    def test_submit(self, console_service: ConsoleService) -> None:
        """Test submit command."""
        console_service.submit("x = 1")
        assert console_service.history == ["x = 1"]

    def test_submit_empty(self, console_service: ConsoleService) -> None:
        """Test submit with empty input."""
        console_service.submit("")
        assert console_service.history == []

    def test_submit_multiline(self, console_service: ConsoleService) -> None:
        """Test submit starts multiline mode."""
        console_service.submit("def foo():")
        assert console_service.prompt == "... "

    def test_submit_completes_multiline(self, console_service: ConsoleService) -> None:
        """Test completing multiline statement."""
        console_service.submit("def foo():")
        assert console_service.prompt == "... "
        console_service.submit("    pass")
        console_service.submit("")
        assert console_service.prompt == ">>> "

    def test_history_navigation_up(self, console_service: ConsoleService) -> None:
        """Test up arrow navigates history."""
        console_service.submit("first")
        console_service.submit("second")

        result = console_service.press_up("current")
        assert result == "second"
        assert console_service.history_index == 1

        result = console_service.press_up("current")
        assert result == "first"
        assert console_service.history_index == 0

    def test_history_navigation_up_at_start(
        self, console_service: ConsoleService
    ) -> None:
        """Test up arrow at start of history."""
        console_service.submit("first")

        result = console_service.press_up("current")
        assert result == "first"
        result = console_service.press_up("current")
        assert result == "first"
        assert console_service.history_index == 0

    def test_history_navigation_down(self, console_service: ConsoleService) -> None:
        """Test down arrow navigates history."""
        console_service.submit("first")
        console_service.submit("second")

        console_service.press_up("current")
        console_service.press_up("current")
        assert console_service.history_index == 0

        result = console_service.press_down()
        assert result == "second"
        assert console_service.history_index == 1

    def test_history_navigation_down_restores_current(
        self, console_service: ConsoleService
    ) -> None:
        """Test down arrow restores current input."""
        console_service.submit("first")

        console_service.press_up("current")
        assert console_service.input_buffer == "current"

        result = console_service.press_down()
        assert result == "current"
        assert console_service.history_index is None

    def test_history_navigation_up_empty(self, console_service: ConsoleService) -> None:
        """Test up arrow with no history."""
        result = console_service.press_up("current")
        assert result is None
        assert console_service.history_index is None

    def test_history_navigation_down_not_in_history(
        self, console_service: ConsoleService
    ) -> None:
        """Test down arrow when not in history mode."""
        result = console_service.press_down()
        assert result is None
        assert console_service.history_index is None

    def test_exit_history(self, console_service: ConsoleService) -> None:
        """Test exit_history resets history_index."""
        console_service.submit("first")
        console_service.press_up("current")
        assert console_service.history_index == 0

        console_service.exit_history()
        assert console_service.history_index is None

    def test_submit_adds_to_history(self, console_service: ConsoleService) -> None:
        """Test that submit adds non-empty commands to history."""
        console_service.submit("x = 1")
        console_service.submit("y = 2")

        assert len(console_service.history) == 2
        assert console_service.history == ["x = 1", "y = 2"]

    def test_multiline_history(self, console_service: ConsoleService) -> None:
        """Test history with multiline statements."""
        console_service.submit("def foo():")
        console_service.submit("    return 1")
        console_service.submit("")

        # Empty line not added to history, only 2 entries
        assert len(console_service.history) == 2
        assert console_service.history == ["def foo():", "    return 1"]
        assert console_service.prompt == ">>> "
