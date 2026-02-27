import code
import io
import sys
import typing

import sdl2

from gamepart.event import KeyboardEventDispatcher
from gamepart.utils import cached_depends_on

from .guiobject import GUIObject
from .paragraph import ScrollableParagraph
from .text import Text
from .textinput import TextInput


class BufferedConsole(code.InteractiveConsole):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.output_buffer = io.StringIO()

    def write(self, data: str) -> None:
        self.output_buffer.write(data)

    def push_line(self, line: str, prefix: str = "") -> bool:
        self.output_buffer.write(prefix)
        self.output_buffer.write(line)
        self.output_buffer.write("\n")
        so, se = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = self.output_buffer
        more = self.push(line)
        sys.stdout, sys.stderr = so, se
        return more


class ConsoleService:
    def __init__(self, shell: BufferedConsole):
        self.shell: BufferedConsole = shell

        self.prompt1: str = ">>> "
        self.prompt2: str = "... "
        self.prompt: str = self.prompt1
        self.input_buffer: str = ""
        self.history: list[str] = []
        self.history_index: int | None = None

    def get_history_output(self) -> str:
        return self.shell.output_buffer.getvalue().rstrip("\n")

    def exit_history(self) -> None:
        self.history_index = None

    def press_up(self, current_input: str) -> str | None:
        if self.history:
            if self.history_index is None:
                self.history_index = len(self.history)
                self.input_buffer = current_input
            self.history_index = max(self.history_index - 1, 0)
            return self.history[self.history_index]
        return None

    def press_down(self) -> str | None:
        if self.history_index is not None:
            self.history_index = min(self.history_index + 1, len(self.history))
            if self.history_index == len(self.history):
                result = self.input_buffer
                self.history_index = None
                return result
            else:
                return self.history[self.history_index]
        return None

    def submit(self, data: str) -> None:
        self.exit_history()
        if data:
            self.history.append(data)
        if self.shell.push_line(data, self.prompt):
            self.prompt = self.prompt2
        else:
            self.prompt = self.prompt1


class Console(GUIObject):
    def __init__(self, shell_locals: dict[str, typing.Any] | None = None) -> None:
        super().__init__()
        locals_ = {"__name__": "__console__", "__doc__": None, "self": self}
        if shell_locals:
            locals_.update(shell_locals)
        self.shell = BufferedConsole(locals=locals_)
        self.service = ConsoleService(self.shell)

        self.font = "console"
        self.font_size: int = 12
        self.line_spacing: int = 2
        self.width: int = 640
        self.height: int = 200
        self.wrap_width: int | None = None
        self.color: tuple[int, int, int, int] = (200, 200, 200, 200)
        self.bg_color: tuple[int, int, int, int] = (20, 0, 20, 200)

        self.keyboard_dispatcher = KeyboardEventDispatcher()
        self.keyboard_dispatcher.on_down(sdl2.SDLK_UP, self.on_up)
        self.keyboard_dispatcher.on_down(sdl2.SDLK_DOWN, self.on_down)

    def wrap_lines(self, text: str) -> str:
        wrap_width = self.wrap_width or int(self.width / self.font_size * 1.7)
        lines = []
        for line in text.split("\n"):
            if len(line) <= wrap_width:
                lines.append(line)
            else:
                while len(line) > wrap_width:
                    lines.append(line[:wrap_width])
                    line = line[wrap_width:]
                if line:
                    lines.append(line)
        return "\n".join(lines)

    @cached_depends_on("font", "font_size", "color", "height", "line_spacing")
    def get_prompt_text(self) -> Text:
        text = Text(
            text=self.service.prompt,
            font=self.font,
            font_size=self.font_size,
            color=self.color,
        )
        text.init_gui_system(self.gui_system)
        text.fit_to_text()
        text.y = self.height - text.height - self.line_spacing
        return text

    @cached_depends_on("font", "font_size", "color", "height", "line_spacing")
    def get_input_field(self) -> TextInput:
        text_input = TextInput(
            text=self.service.input_buffer,
            font=self.font,
            font_size=self.font_size,
            color=self.color,
            on_submit=self.on_input_submit,
        )
        text_input.init_gui_system(self.gui_system)
        text = self.get_prompt_text()
        text_input.x, text_input.y = text.width + self.line_spacing, text.y
        text_input.focused = self.focused
        return text_input

    @cached_depends_on("font", "font_size", "color", "line_spacing", "height")
    def get_history_paragraph(self) -> ScrollableParagraph:
        input_height = self.get_prompt_text().height + self.line_spacing
        paragraph = ScrollableParagraph(
            text=self.wrap_lines(self.service.get_history_output()),
            font=self.font,
            font_size=self.font_size,
            color=self.color,
            line_spacing=self.line_spacing,
            width=self.width,
            height=self.height - input_height - self.line_spacing,
            valign="bottom",
        )
        paragraph.init_gui_system(self.gui_system)
        return paragraph

    def scroll_history_to_bottom(self) -> None:
        paragraph = self.get_history_paragraph()
        paragraph.text = self.wrap_lines(self.service.get_history_output())
        paragraph.target_scroll_offset = float("inf")

    def focus(self) -> None:
        input_field = self.get_input_field()
        input_field.focused = True
        input_field.focus()

    def unfocus(self) -> None:
        input_field = self.get_input_field()
        input_field.focused = False
        input_field.unfocus()

    def on_input_submit(self, text: str) -> None:
        self.service.submit(text)
        input_field = self.get_input_field()
        input_field.clear()
        self.scroll_history_to_bottom()

    def on_up(self, event: sdl2.SDL_Event) -> bool:
        input_field = self.get_input_field()
        new_text = self.service.press_up(input_field.text)
        if new_text is not None:
            input_field.text = new_text
            input_field.cursor_index = len(new_text)
        return True

    def on_down(self, event: sdl2.SDL_Event) -> bool:
        input_field = self.get_input_field()
        new_text = self.service.press_down()
        if new_text is not None:
            input_field.text = new_text
            input_field.cursor_index = len(new_text)
        return True

    def draw(self) -> None:
        x, y = self.get_absolute_position()

        self.gui_system.renderer.fill(
            [(x, y, self.width, self.height)],
            self.bg_color,
        )
        input_field = self.get_input_field()
        prompt_text = self.get_prompt_text()
        history_paragraph = self.get_history_paragraph()

        history_paragraph.text = self.wrap_lines(self.service.get_history_output())
        prompt_text.text = self.service.prompt
        prompt_text.fit_to_text()
        input_field.x = prompt_text.width

        history_paragraph.draw()
        prompt_text.draw()
        input_field.draw()

    def event(self, event: sdl2.SDL_Event) -> bool:
        if event.type in (sdl2.SDL_KEYDOWN, sdl2.SDL_KEYUP):
            if result := self.keyboard_dispatcher(event):
                return result
        return self.get_input_field().event(event)

    def event_inside(self, event: sdl2.SDL_Event) -> bool:
        if event.type == sdl2.SDL_MOUSEWHEEL:
            return self.get_history_paragraph().event_inside(event)
        return super().event_inside(event)

        # TODO: multiline input
        # TODO: break long lines
        # TODO: stop propagation of all events
        # TODO: use game time
        # TODO: save & load history?
        # TODO: IPython?
        # TODO: selectable text & copy
        # TODO: KeyboadInterrupt
        # TODO: history search
        # TODO: autocomplete
