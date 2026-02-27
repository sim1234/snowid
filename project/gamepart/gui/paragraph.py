from __future__ import annotations

from typing import Literal

import sdl2

from gamepart.utils import cached_depends_on

from .guiobject import GUIObject
from .text import Text


class Paragraph(Text):
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
        line_spacing: int = 2,
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            parent=parent,
            text=text,
            font=font,
            font_size=font_size,
            color=color,
            background_color=background_color,
            max_width=max_width,
        )
        self.line_spacing: int = line_spacing
        self._text_cache: dict[str, Text] = {}

    @cached_depends_on(
        "text",
        "font",
        "font_size",
        "color",
        "max_width",
        "background_color",
        "line_spacing",
    )
    def get_texts(self) -> list[tuple[int, Text]]:
        texts = []
        py = 0
        for line in self.text.split("\n"):
            if (text := self._text_cache.get(line)) is None:
                text = Text(text=line, parent=self)
                text.init_gui_system(self.gui_system)
            text.y = py
            text.font = self.font
            text.font_size = self.font_size
            text.color = self.color
            text.background_color = self.background_color
            text.max_width = self.max_width
            text.fit_to_text()
            texts.append((py, text))
            py += text.height + self.line_spacing

        self._text_cache = {text.text: text for _, text in texts}
        return texts

    def draw(self) -> None:
        for py, text in self.get_texts():
            text.y = py
            text.draw()

    def fit_to_text(self) -> None:
        texts = self.get_texts()
        line_height = self.get_line_height()
        self.width = max(text.width for _, text in texts) if texts else 0
        spacing = max(0, len(texts) - 1) * self.line_spacing
        self.height = len(texts) * line_height + spacing


class ScrollableParagraph(Paragraph):
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
        line_spacing: int = 2,
        scroll_speed: int = 20,
        smooth_scroll_factor: float = 0.2,
        valign: Literal["top", "bottom"] = "top",
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            parent=parent,
            text=text,
            font=font,
            font_size=font_size,
            color=color,
            background_color=background_color,
            max_width=max_width,
            line_spacing=line_spacing,
        )
        self.scroll_speed: int = scroll_speed
        self.smooth_scroll_factor: float = smooth_scroll_factor
        self.valign: Literal["top", "bottom"] = valign
        self._scroll_offset: float = 0.0
        self._target_scroll_offset: float = 0.0

    @property
    def scroll_offset(self) -> float:
        return self._scroll_offset

    @scroll_offset.setter
    def scroll_offset(self, value: float) -> None:
        self._scroll_offset = self._clamp_scroll_offset(value)

    @property
    def target_scroll_offset(self) -> float:
        return self._target_scroll_offset

    @target_scroll_offset.setter
    def target_scroll_offset(self, value: float) -> None:
        self._target_scroll_offset = self._clamp_scroll_offset(value)

    def _clamp_scroll_offset(self, value: float) -> float:
        max_scroll = self._get_content_height() - self.height
        return max(0.0, min(value, max(0.0, max_scroll)))

    def _get_content_height(self) -> int:
        res = 0
        for py, last_text in self.get_texts():
            res = py + last_text.height
        return res

    def event_inside(self, event: sdl2.SDL_Event) -> bool:
        if event.type == sdl2.SDL_MOUSEWHEEL:
            scroll_amount = -event.wheel.y * self.scroll_speed
            self.target_scroll_offset = self._target_scroll_offset + scroll_amount
            return True
        return super().event_inside(event)

    def _get_valign_offset(self) -> int:
        if self.valign == "bottom":
            content_height = self._get_content_height()
            if content_height < self.height:
                return self.height - content_height
        return 0

    def update_scroll(self) -> None:
        if abs(self._target_scroll_offset - self._scroll_offset) > 0.5:
            diff = self._target_scroll_offset - self._scroll_offset
            self._scroll_offset += diff * self.smooth_scroll_factor
            self._scroll_offset = self._clamp_scroll_offset(self._scroll_offset)
        else:
            self._scroll_offset = self._target_scroll_offset

    def draw(self) -> None:
        self.update_scroll()
        abs_x, abs_y = self.get_absolute_position()
        clip_rect = (abs_x, abs_y, self.width, self.height)
        scroll_int = int(self._scroll_offset)
        valign_offset = self._get_valign_offset()

        with self.gui_system.renderer.keep_clip():
            self.gui_system.renderer.clip = clip_rect

            for py, text in self.get_texts():
                text_top = py - scroll_int + valign_offset
                text_bottom = text_top + text.height

                if text_bottom < 0 or text_top > self.height:
                    continue

                text.y = text_top
                text.draw()
