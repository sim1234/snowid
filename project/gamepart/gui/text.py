from __future__ import annotations

import sdl2.ext

from gamepart.utils import cached_depends_on

from .guiobject import GUIObject
from .image import Image
from .system import GUISystem


class Text(Image):
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
    ) -> None:
        super().__init__(x=x, y=y, width=width, height=height, parent=parent)
        self.text: str = text
        self.font: str = font
        self.font_size: int = font_size
        self.color: tuple[int, int, int, int] = color
        self.background_color: tuple[int, int, int, int] | None = background_color
        self.max_width: int | None = max_width

    @cached_depends_on(
        "text", "font", "font_size", "color", "max_width", "background_color"
    )
    def get_rendered_text(self, manager: GUISystem) -> sdl2.ext.Sprite | None:
        if self.text:
            surface = manager.font_manager.render(
                self.text,
                alias=self.font,
                size=self.font_size,
                color=self.color,
                width=self.max_width,
                bg_color=self.background_color,
            )
            return manager.sprite_factory.from_surface(surface, free=True)
        return None

    def draw(self, manager: GUISystem) -> None:
        self.sprite = self.get_rendered_text(manager)
        super().draw(manager)
