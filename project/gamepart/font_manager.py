import ctypes
from functools import lru_cache

from sdl2 import sdlttf
from sdl2.ext import FontManager


class AdvancedFontManager(FontManager):
    def _ensure_font_size(self, alias: str, size: int) -> None:
        if alias not in self.fonts:
            raise KeyError(f"Font {alias!r} not loaded in FontManager")
        if size not in self.fonts[alias]:
            self._change_font_size(alias, size)  # type: ignore[attr-defined]

    @lru_cache(maxsize=100)
    def get_text_size(self, font: str, size: int, text: str) -> tuple[int, int]:
        if not text:
            return 0, 0
        self._ensure_font_size(font, size)
        face = self.fonts[font][size]
        w = ctypes.c_int(0)
        h = ctypes.c_int(0)
        sdlttf.TTF_SizeUTF8(
            face, text.encode("utf-8"), ctypes.byref(w), ctypes.byref(h)
        )
        return w.value, h.value

    @lru_cache(maxsize=100)
    def get_line_height(self, font: str, size: int) -> int:
        self._ensure_font_size(font, size)
        return sdlttf.TTF_FontLineSkip(self.fonts[font][size])
