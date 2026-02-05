import sdl2

from gamepart.subsystem import SubSystemObject


class GUIObject(SubSystemObject):
    gui_system: "GUISystem"

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        parent: "GUIObject | None" = None,
    ) -> None:
        super().__init__()
        self.enabled: bool = True  # controls calls to event methods
        self.visible: bool = True  # controls calls to draw method
        self.focused: bool = False  # set by the system
        self.hovered: bool = False  # set by the system
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.parent: GUIObject | None = parent

    def draw(self) -> None:
        raise NotImplementedError()

    def init_gui_system(self, gui_system: "GUISystem") -> None:
        self.gui_system = gui_system

    def uninit_gui_system(self) -> None:
        del self.gui_system

    def event(self, event: sdl2.SDL_Event) -> bool:
        """Handle the event. Return True if event propagation should stop."""
        return False

    def event_inside(self, event: sdl2.SDL_Event) -> bool:
        """Handle the event that is inside the object.
        Return True if event propagation should stop."""
        return False

    def focus(self) -> None:
        pass

    def unfocus(self) -> None:
        pass

    def get_absolute_position(self) -> tuple[int, int]:
        if self.parent is None:
            return self.x, self.y
        parent_x, parent_y = self.parent.get_absolute_position()
        return parent_x + self.x, parent_y + self.y

    def contains_point(self, px: int, py: int) -> bool:
        x, y = self.get_absolute_position()
        return x <= px < x + self.width and y <= py < y + self.height


from .system import GUISystem  # noqa
