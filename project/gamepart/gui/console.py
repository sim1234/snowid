import code
import io
import sys
import time
import typing

import sdl2

from .system import GUISystem
from .guiobject import GUIObject


class BufferedConsole(code.InteractiveConsole):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_buffer = io.StringIO()

    def write(self, data: str):
        self.output_buffer.write(data)

    def push_line(self, line: str, prefix: str = ""):
        self.output_buffer.write(prefix)
        self.output_buffer.write(line)
        self.output_buffer.write("\n")
        so, se = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = self.output_buffer
        more = self.push(line)
        sys.stdout, sys.stderr = so, se
        return more


class Console(GUIObject):
    def __init__(self, shell_locals: dict = None):
        super().__init__()
        locals_ = {"__name__": "__console__", "__doc__": None, "self": self}
        if shell_locals:
            locals_.update(shell_locals)
        self.shell = BufferedConsole(locals=locals_)
        self.font = "console"
        self.font_size: int = 12
        self.line_spacing: int = 2
        self.position = [0, 0]
        self.width: int = 640
        self.height: int = 200
        self.scroll = [0, 0]
        self.color = (200, 200, 200, 200)
        self.bg_color = (20, 0, 20, 200)

        self.prompt1: str = ">>> "
        self.prompt2: str = "... "
        self.prompt: str = self.prompt1
        self.input_buffer: str = ""
        self.input_buffer2: str = ""
        self.input_index: int = 0
        self.history: typing.List[str] = []
        self.history_index: typing.Optional[int] = None

    def focus(self):
        sdl2.SDL_StartTextInput()
        sdl2.SDL_SetTextInputRect(
            sdl2.SDL_Rect(
                self.position[0],
                self.position[1] + self.height - self.font_size,
                self.width,
                self.font_size,
            )
        )

    def unfocus(self):
        sdl2.SDL_StopTextInput()

    def draw(self, manager: "GUISystem"):
        # TODO: multiline input
        # TODO: break long lines
        # TODO: split into components
        # TODO: clipboard
        # TODO: stop propagation of all events
        # TODO: scrolls
        # TODO: add game to locals
        # TODO: use game time
        # TODO: save & load history?
        # TODO: IPython?

        line_height = self.font_size + self.line_spacing
        buffer = self.shell.output_buffer.getvalue() + self.prompt
        buffer += self.input_buffer[: self.input_index]
        old_clip = manager.renderer.clip
        manager.renderer.clip = (
            self.position[0],
            self.position[1],
            self.width,
            self.height,
        )
        manager.renderer.fill(
            [(self.position[0], self.position[1], self.width, self.height)],
            self.bg_color,
        )

        self.scroll[1] = (
            self.height - (buffer.count("\n") + 1) * line_height - self.line_spacing
        )
        py = 0
        for row in buffer.split("\n"):
            spy = py + self.scroll[1]
            if row and spy <= self.height and spy + line_height >= 0:
                text = manager.font_manager.render(
                    row, alias=self.font, size=self.font_size, color=self.color
                )
                tw = text.w
                th = text.h
                tx = self.position[0] + self.scroll[0]
                ty = self.position[1] + self.scroll[1] + py
                text = manager.sprite_factory.from_surface(text, True)
                manager.renderer.copy(text, (0, 0, tw, th), (tx, ty, tw, th))
            py += line_height

        ttx = tx + tw
        if time.time() % 1 <= 0.5:
            text = manager.font_manager.render(
                "|", alias=self.font, size=self.font_size, color=self.color
            )
            ttw = text.w
            tth = text.h
            text = manager.sprite_factory.from_surface(text, True)
            manager.renderer.copy(
                text, (0, 0, ttw, tth), (ttx - int(ttw / 2), ty, ttw, tth)
            )

        rest = self.input_buffer[self.input_index :]
        if rest and self.history_index is None:
            text = manager.font_manager.render(
                rest, alias=self.font, size=self.font_size, color=self.color
            )
            tw = text.w
            th = text.h
            text = manager.sprite_factory.from_surface(text, True)
            manager.renderer.copy(text, (0, 0, tw, th), (ttx, ty, tw, th))

        manager.renderer.clip = old_clip

    def event(self, event: sdl2.SDL_Event):
        if event.type == sdl2.SDL_TEXTINPUT:
            self.input_buffer = "{}{}{}".format(
                self.input_buffer[: self.input_index],
                event.text.text.decode("utf8"),
                self.input_buffer[self.input_index :],
            )
            self.input_index += 1
            self.history_index = None
        if event.type == sdl2.SDL_KEYUP:
            if event.key.keysym.sym in (sdl2.SDLK_BACKSPACE, sdl2.SDLK_KP_BACKSPACE):
                self.input_buffer = "{}{}".format(
                    self.input_buffer[: self.input_index][:-1],
                    self.input_buffer[self.input_index :],
                )
                self.input_index = max(self.input_index - 1, 0)
                self.history_index = None
            if event.key.keysym.sym == sdl2.SDLK_DELETE:
                self.input_buffer = "{}{}".format(
                    self.input_buffer[: self.input_index],
                    self.input_buffer[self.input_index :][1:],
                )
                self.input_index = max(self.input_index, 0)
                self.history_index = None
            elif event.key.keysym.sym == sdl2.SDLK_LEFT:
                self.input_index = max(self.input_index - 1, 0)
                self.history_index = None
            elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                self.input_index = min(self.input_index + 1, len(self.input_buffer))
                self.history_index = None
            elif event.key.keysym.sym == sdl2.SDLK_END:
                self.input_index = len(self.input_buffer)
                self.history_index = None
            elif event.key.keysym.sym == sdl2.SDLK_HOME:
                self.input_index = 0
                self.history_index = None
            elif event.key.keysym.sym == sdl2.SDLK_UP:
                if self.history:
                    if self.history_index is None:
                        self.history_index = len(self.history)
                        self.input_buffer2 = self.input_buffer
                    self.history_index = max(self.history_index - 1, 0)
                    self.input_buffer = self.history[self.history_index]
                    self.input_index = len(self.input_buffer)
            elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                if self.history_index is not None:
                    self.history_index = min(self.history_index + 1, len(self.history))
                    if self.history_index == len(self.history):
                        self.input_buffer = self.input_buffer2
                        self.input_index = len(self.input_buffer)
                        self.history_index = None
                    else:
                        self.input_buffer = self.history[self.history_index]
                        self.input_index = len(self.input_buffer)
            elif event.key.keysym.sym in (
                sdl2.SDLK_KP_ENTER,
                sdl2.SDLK_RETURN,
                sdl2.SDLK_RETURN2,
            ):
                data = self.input_buffer
                if self.history_index is not None:
                    data = self.history[self.history_index]
                if data:
                    self.history.append(data)
                if self.shell.push_line(data, self.prompt):
                    self.prompt = self.prompt2
                else:
                    self.prompt = self.prompt1
                self.input_buffer = ""
                self.input_index = 0
                self.history_index = None
