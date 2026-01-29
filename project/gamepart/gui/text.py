from __future__ import annotations

from .image import Image
from .system import GUISystem


class Text(Image):
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
    ) -> None:
        super().__init__(x=x, y=y, width=width, height=height)
        self._text: str = text
        self.font: str = font
        self.font_size: int = font_size
        self.color: tuple[int, int, int, int] = color
        self.background_color: tuple[int, int, int, int] | None = background_color
        self.max_width: int | None = max_width

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        if value != self._text:
            self.sprite = None
        self._text = value

    def draw(self, manager: GUISystem) -> None:
        if self.sprite is None and self.text:
            surface = manager.font_manager.render(
                self.text,
                alias=self.font,
                size=self.font_size,
                color=self.color,
                width=self.max_width,
                bg_color=self.background_color,
            )
            sprite = manager.sprite_factory.from_surface(surface, free=True)
            self.sprite = sprite

        super().draw(manager)
