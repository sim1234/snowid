import code
import math
import io
import sys

import sdl2

from .system import GUISystem
from .guiobject import GUIObject


class BufferedConsole(code.InteractiveConsole):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_buffer = io.StringIO()

    def write(self, data: str):
        self.output_buffer.write(data)

    def push_line(self, line: str):
        self.output_buffer.write(line)
        self.output_buffer.write("\n")
        so, se = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = self.output_buffer
        self.push(line)
        sys.stdout, sys.stderr = so, se


class Console(GUIObject):
    def __init__(self):
        super().__init__()
        self.shell = BufferedConsole()
        # self.font = None
        # self.font_size = 8
        self.font = "console"
        self.font_size = 12
        self.position = (0, 0)
        self.width = 640
        self.height = 200
        self.color = (200, 200, 200, 200)
        self.bg_color = (20, 0, 20, 200)
        self._max_width = self.width
        self._max_height = self.height * 2
        self.input_buffer = b""
        sdl2.SDL_StartTextInput()

    def _filter_output(self, data: str):
        max_lines = math.floor(self._max_height / (self.font_size + 1))
        max_chars = math.floor(self._max_width / (self.font_size + 1))
        return "\n".join([row[:max_chars] for row in data.split("\n")[-max_lines:]])

    def draw(self, manager: "GUISystem"):
        d = self.input_buffer.decode("utf8")
        buffer = "Test " + "a" * 100 + "\n" + self.shell.output_buffer.getvalue() + d
        buffer = self._filter_output(buffer)
        manager.renderer.fill(
            [(self.position[0], self.position[1], self.width, self.height)],
            self.bg_color,
        )
        if buffer:
            text = manager.font_manager.render(
                buffer,
                alias=self.font,
                size=self.font_size,
                color=self.color,
                # bg_color=(100, 0, 0, 255),
                width=int(self._max_width),
            )
            tw, th = min(self.width, text.w), min(self.height, text.h)
            sx, sy = 0, text.h - th
            tx = self.position[0]
            ty = self.position[1] + self.height - th
            print((text.w, text.h), (sx, sy, tw, th), (tx, ty, tw, th))
            text = manager.sprite_factory.from_surface(text, True)
            manager.renderer.copy(text, (sx, sy, tw, th), (tx, ty, tw, th))

    def event(self, event: sdl2.SDL_Event):
        if event.type == sdl2.SDL_TEXTINPUT:
            self.input_buffer += event.text.text
        if event.type == sdl2.SDL_KEYUP:
            if event.key.keysym.sym in (sdl2.SDLK_BACKSPACE, sdl2.SDLK_KP_BACKSPACE):
                self.input_buffer = self.input_buffer[:-1]
            elif event.key.keysym.sym in (
                sdl2.SDLK_KP_ENTER,
                sdl2.SDLK_RETURN,
                sdl2.SDLK_RETURN2,
            ):
                print(self.input_buffer)
                self.shell.push_line(self.input_buffer.decode("utf8"))
                self.input_buffer = b""
