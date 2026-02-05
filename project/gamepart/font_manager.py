import ctypes
from functools import lru_cache

from sdl2 import sdlttf
from sdl2.ext import FontManager


class AdvancedFontManager(FontManager):
    @lru_cache(maxsize=100)
    def get_text_size(self, font: str, size: int, text: str) -> tuple[int, int]:
        if not text:
            return 0, 0
        font = self.fonts[font][size]
        w = ctypes.c_int(0)
        h = ctypes.c_int(0)
        sdlttf.TTF_SizeUTF8(
            font, text.encode("utf-8"), ctypes.byref(w), ctypes.byref(h)
        )
        return w.value, h.value

    @lru_cache(maxsize=100)
    def get_line_height(self, font: str, size: int) -> int:
        return sdlttf.TTF_FontLineSkip(self.fonts[font][size])
