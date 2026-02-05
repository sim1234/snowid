from __future__ import annotations

import sdl2
import sdl2.ext

from .guiobject import GUIObject


class Image(GUIObject):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        parent: GUIObject | None = None,
        sprite: sdl2.ext.Sprite | None = None,
        stretch: bool = False,
    ) -> None:
        super().__init__(x=x, y=y, width=width, height=height, parent=parent)
        self.sprite: sdl2.ext.Sprite | None = sprite
        self.stretch: bool = stretch

    def draw(self) -> None:
        if self.sprite is None:
            return
        x, y = self.get_absolute_position()
        src_w, src_h = self.sprite.size
        dst_w = self.width if self.width > 0 and self.stretch else src_w
        dst_h = self.height if self.height > 0 and self.stretch else src_h
        self.gui_system.renderer.copy(
            self.sprite,
            (0, 0, src_w, src_h),
            (x, y, dst_w, dst_h),
        )
