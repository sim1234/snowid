import typing
from typing import Any

import sdl2
import sdl2.ext

from gamepart.font_manager import AdvancedFontManager
from gamepart.render import GfxRenderer
from gamepart.subsystem import SubSystem


class GUISystem(SubSystem["GUIObject"]):
    def __init__(
        self,
        renderer: GfxRenderer,
        font_manager: AdvancedFontManager,
        sprite_factory: sdl2.ext.SpriteFactory,
        width: int,
        height: int,
    ):
        super().__init__()
        self.renderer = renderer
        self.font_manager = font_manager
        self.sprite_factory = sprite_factory
        self.width = width
        self.height = height
        self.focused_object: GUIObject | None = None
        self.mouse_position: tuple[int, int] = (0, 0)

    @staticmethod
    def accepts(obj: typing.Any) -> bool:
        return isinstance(obj, GUIObject)

    def add(self, *objects: "GUIObject") -> typing.Iterable["GUIObject"]:
        super().add(*objects)
        for obj in objects:
            obj.init_gui_system(self)
        return objects

    def remove(self, *objects: "GUIObject") -> typing.Iterable["GUIObject"]:
        for obj in objects:
            obj.uninit_gui_system()
        return super().remove(*objects)

    def draw(self) -> None:
        for obj in self.objects:
            if obj.visible:
                obj.draw()

    def event(self, event: sdl2.SDL_Event) -> Any:
        x, y = self._update_mouse_position(event)
        result = None
        handled_by = None
        for obj in self.objects:
            if obj.enabled and handled_by is None:
                if result := obj.event(event):
                    handled_by = obj.event
            hovered = obj.contains_point(x, y)
            obj.hovered = obj.visible and hovered
            if obj.hovered and obj.enabled and handled_by is None:
                if result := obj.event_inside(event):
                    handled_by = obj.event_inside
        return False if handled_by is None else (handled_by, result)

    def change_focus(self, obj: typing.Optional["GUIObject"]) -> None:
        if self.focused_object:
            self.focused_object.unfocus()
            self.focused_object.focused = False
        self.focused_object = obj
        if self.focused_object:
            self.focused_object.focus()
            self.focused_object.focused = True

    def _update_mouse_position(self, event: sdl2.SDL_Event) -> tuple[int, int]:
        if event.type in (sdl2.SDL_MOUSEBUTTONDOWN, sdl2.SDL_MOUSEBUTTONUP):
            self.mouse_position = event.button.x, event.button.y
        if event.type == sdl2.SDL_MOUSEMOTION:
            self.mouse_position = event.motion.x, event.motion.y
        return self.mouse_position


from .guiobject import GUIObject  # noqa
