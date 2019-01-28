import sdl2

from ..subsystem import SubSystemObject


class GUIObject(SubSystemObject):
    def draw(self, manager: "GUISystem"):
        raise NotImplementedError()

    def event(self, event: sdl2.SDL_Event):
        raise NotImplementedError()


from .system import GUISystem  # noqa
