import typing

import sdl2
import sdl2.ext

from gamepart.subsystem import SystemManager

from .context import Context
from .event import EventDispatcher, KeyEventDispatcher, MouseEventDispatcher
from .render import GfxRenderer


class Scene:
    """Scene base"""

    def __init__(self, game: "Game", name: str, *args, **kwargs):
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

    def frame(self):
        self.game.running = False


class SimpleScene(Scene):
    """Scene with some utility functions"""

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.system: SystemManager | None = None
        self._event_dispatcher: EventDispatcher | None = (
            None  # Internal event dispatcher
        )
        self.key_event: KeyEventDispatcher | None = None
        self.mouse_event: MouseEventDispatcher | None = None

    def event(self, event: sdl2.SDL_Event) -> None:  # type: ignore[override]
        """Handle event via dispatcher"""
        if self._event_dispatcher is not None:
            self._event_dispatcher(event)

    def init(self) -> None:
        super().init()
        self.system = SystemManager()
        self._event_dispatcher = EventDispatcher()
        self.key_event = KeyEventDispatcher()
        self.mouse_event = MouseEventDispatcher()
        if self._event_dispatcher is not None:
            self._event_dispatcher.on(sdl2.SDL_QUIT, self.on_exit)
            self._event_dispatcher.on(sdl2.SDL_KEYDOWN, self.key_event)
            self._event_dispatcher.on(sdl2.SDL_KEYUP, self.key_event)
            self._event_dispatcher.on(sdl2.SDL_MOUSEBUTTONDOWN, self.mouse_event)
            self._event_dispatcher.on(sdl2.SDL_MOUSEBUTTONUP, self.mouse_event)

    def start(self, context: Context) -> None:
        self.is_first_frame = True
        super().start(context)

    def frame(self) -> None:
        if self.system is None or self.game.renderer is None:
            return
        self.system.remove_queued_all()
        if self.is_first_frame:
            self.first_frame(self.game.renderer)
            self.is_first_frame = False
        self.every_frame(self.game.renderer)

    def uninit(self) -> None:
        if self._event_dispatcher is not None:
            self._event_dispatcher.clear()
        if self.key_event is not None:
            self.key_event.clear()
        if self.mouse_event is not None:
            self.mouse_event.clear()
        if self.system is not None:
            self.system.clear_all()
            self.system.clear()
        super().uninit()

    def on_exit(self, _: sdl2.SDL_Event) -> None:
        """Handle exit event"""
        self.exit()

    def exit(self) -> None:
        """Exit the game"""
        self.game.queue_scene_switch("exit")

    def first_frame(self, renderer: GfxRenderer) -> None:
        """Generate first frame"""

    def every_frame(self, renderer: GfxRenderer) -> None:
        """Generate frame"""


from .game import Game  # noqa
