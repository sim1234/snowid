from __future__ import annotations

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
    def get_texts(self) -> list[Text]:
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
            texts.append(text)
            py += text.height + self.line_spacing

        self._text_cache = {t.text: t for t in texts}
        return texts

    def draw(self) -> None:
        for text in self.get_texts():
            text.draw()

    def fit_to_text(self) -> None:
        texts = self.get_texts()
        line_height = self.get_line_height()
        self.width = max(text.width for text in texts) if texts else 0
        spacing = max(0, len(texts) - 1) * self.line_spacing
        self.height = len(texts) * line_height + spacing
