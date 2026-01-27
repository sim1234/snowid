import typing

import sdl2.ext

from gamepart.render import GfxRenderer
from gamepart.subsystem import SubSystem


class GUISystem(SubSystem["GUIObject"]):
    def __init__(
        self,
        renderer: GfxRenderer,
        font_manager: sdl2.ext.FontManager,
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

    @staticmethod
    def accepts(obj: typing.Any) -> bool:
        return isinstance(obj, GUIObject)

    def draw(self) -> None:
        for obj in self.objects:
            if obj.visible:
                obj.draw(self)

    def event(self, event: sdl2.SDL_Event) -> None:
        for obj in self.objects:
            if obj.enabled:
                obj.event(event)

    def change_focus(self, obj: typing.Optional["GUIObject"]) -> None:
        if self.focused_object:
            self.focused_object.unfocus()
        self.focused_object = obj
        if self.focused_object:
            self.focused_object.focus()


from .guiobject import GUIObject  # noqa
