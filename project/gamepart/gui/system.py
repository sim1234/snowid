import sdl2.ext

from ..subsystem import SubSystem
from ..render import GfxRenderer


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


from .guiobject import GUIObject  # noqa
