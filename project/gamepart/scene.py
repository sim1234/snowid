import typing

import sdl2
import sdl2.ext

from gamepart.subsystem import SystemManager

from .context import Context
from .event import EventDispatcher, KeyboardEventDispatcher, MouseButtonEventDispatcher
from .render import GfxRenderer


class Scene:
    """Scene base"""

    def __init__(
        self, game: "Game", name: str, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        self.game: Game = game
        self.name: str = name
        self.args = args
        self.kwargs = kwargs
        self.is_first_frame = True
        self.context: Context = Context(None)

    def init(self) -> None:
        """Configure Scene"""

    def start(self, context: Context) -> None:
        """Start displaying Scene"""
        self.context = context

    def tick(self, delta: float) -> None:
        """Move forward in time"""

    def event(self, event: sdl2.SDL_Event) -> None:
        """Handle event"""

    def frame(self) -> None:
        """Generate frame"""

    def stop(self) -> Context:
        """Stop displaying Scene"""
        return self.context

    def uninit(self) -> None:
        """Uninitialize Scene"""
        self.context = Context(None)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.game!r}, {self.name!r})"


class ExitScene(Scene):
    """Scene quitting the game"""

    def frame(self) -> None:
        self.game.running = False


class SimpleScene(Scene):
    """Scene with some utility functions"""

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.system: SystemManager
        self.event_dispatcher: EventDispatcher
        self.keyboard_event: KeyboardEventDispatcher
        self.mouse_button_event: MouseButtonEventDispatcher
        self.is_first_frame: bool

    def init(self) -> None:
        super().init()
        self.system = SystemManager()
        self.event_dispatcher = EventDispatcher()
        self.keyboard_event = KeyboardEventDispatcher()
        self.mouse_button_event = MouseButtonEventDispatcher()
        self.mouse_button_event.attach_to(self.event_dispatcher)
        self.keyboard_event.attach_to(self.event_dispatcher)
        self.event_dispatcher.on(sdl2.SDL_QUIT, lambda _: self.exit())

    def event(self, event: sdl2.SDL_Event) -> None:
        """Handle event via dispatcher"""
        self.event_dispatcher(event)

    def start(self, context: Context) -> None:
        self.is_first_frame = True
        super().start(context)

    def frame(self) -> None:
        self.system.remove_queued_all()
        if self.is_first_frame:
            self.first_frame(self.game.renderer)
            self.is_first_frame = False
        self.every_frame(self.game.renderer)

    def uninit(self) -> None:
        self.event_dispatcher.clear()
        self.keyboard_event.clear()
        self.mouse_button_event.clear()
        self.system.clear_all()
        self.system.clear()
        super().uninit()

    def exit(self) -> None:
        """Exit the game"""
        self.game.queue_scene_switch("exit")

    def first_frame(self, renderer: GfxRenderer) -> None:
        """Generate first frame"""

    def every_frame(self, renderer: GfxRenderer) -> None:
        """Generate frame"""


from .game import Game  # noqa
