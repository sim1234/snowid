import sdl2

from gamepart.subsystem import SubSystemObject


class GUIObject(SubSystemObject):
    def __init__(self) -> None:
        super().__init__()
        self.enabled: bool = True
        self.visible: bool = True

    def draw(self, manager: "GUISystem") -> None:
        raise NotImplementedError()

    def event(self, event: sdl2.SDL_Event) -> None:
        raise NotImplementedError()

    def focus(self) -> None:
        pass

    def unfocus(self) -> None:
        pass


from .system import GUISystem  # noqa
