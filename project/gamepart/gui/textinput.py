from __future__ import annotations

import time
from collections.abc import Callable

import sdl2

from gamepart.event import KeyboardEventDispatcher
from gamepart.utils import cached_depends_on, get_clipboard_text

from .guiobject import GUIObject
from .text import Text


class TextController:
    text: str
    cursor_index: int

    def enter_text(self, new_text: str) -> None:
        before = self.text[: self.cursor_index]
        after = self.text[self.cursor_index :]
        self.text = f"{before}{new_text}{after}"
        self.cursor_index += len(new_text)

    def press_backspace(self, amount: int = 1) -> None:
        before = self.text[: self.cursor_index][:-amount]
        after = self.text[self.cursor_index :]
        self.text = f"{before}{after}"
        self.cursor_index = max(self.cursor_index - amount, 0)

    def press_delete(self, amount: int = 1) -> None:
        before = self.text[: self.cursor_index]
        after = self.text[self.cursor_index :][amount:]
        self.text = f"{before}{after}"

    def press_left(self, amount: int = 1) -> None:
        self.cursor_index = max(self.cursor_index - amount, 0)

    def press_right(self, amount: int = 1) -> None:
        self.cursor_index = min(self.cursor_index + amount, len(self.text))

    def press_ctrl_left(self) -> None:
        idx = self.text.rfind(" ", 0, max(self.cursor_index - 1, 0))
        if idx == -1:
            idx = 0
        self.cursor_index = idx

    def press_ctrl_right(self) -> None:
        idx = self.text.find(" ", self.cursor_index + 1)
        if idx == -1:
            idx = len(self.text)
        self.cursor_index = idx

    def press_home(self) -> None:
        self.cursor_index = 0

    def press_end(self) -> None:
        self.cursor_index = len(self.text)


class TextInput(TextController, Text):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        parent: GUIObject | None = None,
        text: str = "",
        font: str = "console",
        font_size: int = 12,
        color: tuple[int, int, int, int] = (0, 0, 0, 255),
        background_color: tuple[int, int, int, int] | None = None,
        max_width: int | None = None,
        cursor_index: int = 0,
        cursor_text: str = "|",
        cursor_frequency: float = 1.0,
        enable_paste: bool = True,
        on_submit: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            text=text,
            font=font,
            font_size=font_size,
            color=color,
            background_color=background_color,
            max_width=max_width,
        )
        self.cursor_index: int = cursor_index
        self.cursor_text: str = cursor_text
        self.cursor_frequency: float = cursor_frequency
        self.enable_paste: bool = enable_paste
        self.on_submit: Callable[[str], None] | None = on_submit
        self.keyboard_event_dispatcher = KeyboardEventDispatcher()
        self.setup_event_handlers()

    def setup_event_handlers(self) -> None:
        self.keyboard_event_dispatcher.on_down(sdl2.SDLK_BACKSPACE, self.on_backspace)
        self.keyboard_event_dispatcher.on_down(sdl2.SDLK_DELETE, self.on_delete)
        self.keyboard_event_dispatcher.on_down(sdl2.SDLK_END, self.on_end)
        self.keyboard_event_dispatcher.on_down(sdl2.SDLK_HOME, self.on_home)
        self.keyboard_event_dispatcher.on_down(sdl2.SDLK_KP_ENTER, self.on_enter)
        self.keyboard_event_dispatcher.on_down(sdl2.SDLK_RETURN, self.on_enter)
        self.keyboard_event_dispatcher.on_down(sdl2.SDLK_RETURN2, self.on_enter)
        self.keyboard_event_dispatcher.on_down(sdl2.SDLK_LEFT, self.on_left)
        self.keyboard_event_dispatcher.on_down(sdl2.SDLK_RIGHT, self.on_right)
        self.keyboard_event_dispatcher.on_down(sdl2.SDLK_v, self.on_v)

    def focus(self) -> None:
        abs_x, abs_y = self.get_absolute_position()
        sdl2.SDL_StartTextInput()
        sdl2.SDL_SetTextInputRect(sdl2.SDL_Rect(abs_x, abs_y, self.width, self.height))

    def unfocus(self) -> None:
        sdl2.SDL_StopTextInput()

    @cached_depends_on("font", "font_size", "color")
    def get_cursor(self) -> Text:
        text = Text(
            text="|",
            font=self.font,
            font_size=self.font_size,
            color=self.color,
            parent=self,
        )
        text.init_gui_system(self.gui_system)
        return text

    def draw(self) -> None:
        super().draw()

        if not self.focused or time.time() % self.cursor_frequency > 0.5:
            return

        before_text = self.text[: self.cursor_index]
        before_width, _ = self.gui_system.font_manager.get_text_size(
            self.font, self.font_size, before_text
        )

        cursor = self.get_cursor()
        cursor_sprite = cursor.get_rendered_text(self.gui_system)
        assert cursor_sprite is not None
        cursor.x = before_width - cursor_sprite.size[0] // 2
        cursor.draw()

    def event(self, event: sdl2.SDL_Event) -> bool:
        if not self.focused:
            return False
        if event.type == sdl2.SDL_TEXTINPUT:
            self.enter_text(bytes(event.text.text).decode())
            return True
        elif event.type in (sdl2.SDL_KEYDOWN, sdl2.SDL_KEYUP):
            return self.keyboard_event_dispatcher(event)
        return False

    def on_backspace(self, event: sdl2.SDL_Event) -> bool:
        self.press_backspace()
        return True

    def on_delete(self, event: sdl2.SDL_Event) -> bool:
        self.press_delete()
        return True

    def on_end(self, event: sdl2.SDL_Event) -> bool:
        self.press_end()
        return True

    def on_home(self, event: sdl2.SDL_Event) -> bool:
        self.press_home()
        return True

    def on_v(self, event: sdl2.SDL_Event) -> bool:
        if event.key.keysym.mod & sdl2.KMOD_CTRL:
            self.enter_text(get_clipboard_text())
            return True
        return False

    def on_left(self, event: sdl2.SDL_Event) -> bool:
        if event.key.keysym.mod & sdl2.KMOD_CTRL:
            self.press_ctrl_left()
        else:
            self.press_left()
        return True

    def on_right(self, event: sdl2.SDL_Event) -> bool:
        if event.key.keysym.mod & sdl2.KMOD_CTRL:
            self.press_ctrl_right()
        else:
            self.press_right()
        return True

    def on_enter(self, event: sdl2.SDL_Event) -> bool:
        if self.on_submit:
            self.on_submit(self.text)
        return True

    def clear(self) -> None:
        self.text = ""
        self.cursor_index = 0
