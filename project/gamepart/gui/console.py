from .system import GUISystem
from .guiobject import GUIObject


class Console(GUIObject):
    def __init__(self):
        super().__init__()

    def draw(self, manager: "GUISystem"):
        text = manager.font_manager.render(
            "TEST", size=8, color=(200, 200, 50), bg_color=(10, 10, 10)
        )
        pos = (0, 0, text.w, text.h)
        text = manager.sprite_factory.from_surface(text, True)
        manager.renderer.copy(text, None, pos)
