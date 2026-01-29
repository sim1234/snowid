from __future__ import annotations

import time
from collections.abc import Callable

import sdl2

from gamepart.utils import get_clipboard_text

from .system import GUISystem
from .text import Text


class TextInput(Text):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        text: str = "",
        font: str = "console",
        font_size: int = 12,
        color: tuple[int, int, int, int] = (0, 0, 0, 255),
        background_color: tuple[int, int, int, int] | None = None,
        max_width: int | None = None,
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
        self.cursor_index: int = 0
        self.stored_text: str = text
        self.on_submit: Callable[[str], None] | None = on_submit
        self.enable_paste: bool = enable_paste

    def focus(self) -> None:
        abs_x, abs_y = self.get_absolute_position()
        sdl2.SDL_StartTextInput()
        sdl2.SDL_SetTextInputRect(sdl2.SDL_Rect(abs_x, abs_y, self.width, self.height))

    def unfocus(self) -> None:
        sdl2.SDL_StopTextInput()

    def enter_text(self, new_text: str) -> None:
        before = self.stored_text[: self.cursor_index]
        after = self.stored_text[self.cursor_index :]
        self.stored_text = f"{before}{new_text}{after}"
        self.cursor_index += len(new_text)

    def press_backspace(self, amount: int = 1) -> None:
        before = self.stored_text[: self.cursor_index][:-amount]
        after = self.stored_text[self.cursor_index :]
        self.stored_text = f"{before}{after}"
        self.cursor_index = max(self.cursor_index - amount, 0)

    def press_delete(self, amount: int = 1) -> None:
        before = self.stored_text[: self.cursor_index]
        after = self.stored_text[self.cursor_index :][amount:]
        self.stored_text = f"{before}{after}"

    def press_left(self, amount: int = 1) -> None:
        self.cursor_index = max(self.cursor_index - amount, 0)

    def press_right(self, amount: int = 1) -> None:
        self.cursor_index = min(self.cursor_index + amount, len(self.stored_text))

    def press_home(self) -> None:
        self.cursor_index = 0

    def press_end(self) -> None:
        self.cursor_index = len(self.stored_text)

    def press_enter(self) -> None:
        if self.on_submit:
            self.on_submit(self.stored_text)

    def draw(self, manager: GUISystem) -> None:
        extra = " "
        if self.focused and time.time() % 1 <= 0.5:
            extra = "|"
        before = self.stored_text[: self.cursor_index]
        after = self.stored_text[self.cursor_index :]
        self.text = f"{before}{extra}{after}"
        super().draw(manager)

    def event(self, event: sdl2.SDL_Event) -> bool:
        if not self.focused:
            return False

        if event.type == sdl2.SDL_TEXTINPUT:
            text_bytes = bytes(event.text.text)
            self.enter_text(text_bytes.decode("utf8"))
            return True

        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym in (sdl2.SDLK_BACKSPACE, sdl2.SDLK_KP_BACKSPACE):
                self.press_backspace()
                return True
            elif event.key.keysym.sym == sdl2.SDLK_DELETE:
                self.press_delete()
                return True
            elif event.key.keysym.sym == sdl2.SDLK_LEFT:
                self.press_left()
                return True
            elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                self.press_right()
                return True
            elif event.key.keysym.sym == sdl2.SDLK_END:
                self.press_end()
                return True
            elif event.key.keysym.sym == sdl2.SDLK_HOME:
                self.press_home()
                return True
            elif (
                self.enable_paste
                and event.key.keysym.sym == sdl2.SDLK_v
                and event.key.keysym.mod & sdl2.KMOD_CTRL
            ):
                self.enter_text(get_clipboard_text())
                return True
            elif event.key.keysym.sym in (
                sdl2.SDLK_KP_ENTER,
                sdl2.SDLK_RETURN,
                sdl2.SDLK_RETURN2,
            ):
                self.press_enter()
                return True

        return False
