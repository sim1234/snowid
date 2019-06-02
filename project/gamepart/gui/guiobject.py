import sdl2

from ..subsystem import SubSystemObject


class GUIObject(SubSystemObject):
    def __init__(self):
        super().__init__()
        self.enabled: bool = True
        self.visible: bool = True

    def draw(self, manager: "GUISystem"):
        raise NotImplementedError()

    def event(self, event: sdl2.SDL_Event):
        raise NotImplementedError()

    def focus(self):
        pass

    def unfocus(self):
        pass


from .system import GUISystem  # noqa
