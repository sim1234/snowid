import sdl2
import sdl2.ext

from gamepart.subsystem import SystemManager
from .context import Context
from .event import EventDispatcher, KeyEventDispatcher, MouseEventDispatcher
from .render import GfxRenderer


class Scene:
    """Scene base"""

    def __init__(self, game: "Game", name: str, *args, **kwargs):
        self.game: "Game" = game
        self.name: str = name
        self.args = args
        self.kwargs = kwargs
        self.is_first_frame = True
        self.context: Context = Context(None)

    def init(self):
        """Configure Scene"""

    def start(self, context: Context):
        """Start displaying Scene"""
        self.context = context

    def tick(self, delta: float):
        """Move forward in time"""

    def event(self, event: sdl2.SDL_Event):
        """Handle event"""

    def frame(self):
        """Generate frame"""

    def stop(self) -> Context:
        """Stop displaying Scene"""
        return self.context

    def uninit(self):
        """Uninitialize Scene"""
        self.context: Context = Context(None)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.game!r}, {self.name!r})"


class ExitScene(Scene):
    """Scene quitting the game"""

    def frame(self):
        self.game.running = False


class SimpleScene(Scene):
    """Scene with some utility functions"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system: SystemManager = None
        self.event: EventDispatcher = None
        self.key_event: KeyEventDispatcher = None
        self.mouse_event: MouseEventDispatcher = None

    def init(self):
        super().init()
        self.system = SystemManager()
        self.event = EventDispatcher()
        self.key_event = KeyEventDispatcher()
        self.mouse_event = MouseEventDispatcher()
        self.event.on(sdl2.SDL_QUIT, self.on_exit)
        self.event.on(sdl2.SDL_KEYDOWN, self.key_event)
        self.event.on(sdl2.SDL_KEYUP, self.key_event)
        self.event.on(sdl2.SDL_MOUSEBUTTONDOWN, self.mouse_event)
        self.event.on(sdl2.SDL_MOUSEBUTTONUP, self.mouse_event)

    def start(self, context: Context):
        self.is_first_frame = True
        return super().start(context)

    def frame(self):
        self.system.remove_queued_all()
        if self.is_first_frame:
            self.first_frame(self.game.renderer)
            self.is_first_frame = False
        return self.every_frame(self.game.renderer)

    def uninit(self):
        self.event.clear()
        self.key_event.clear()
        self.mouse_event.clear()
        self.system.clear_all()
        self.system.clear()
        super().uninit()

    def on_exit(self, _: sdl2.SDL_Event):
        """Handle exit event"""
        self.exit()

    def exit(self):
        """Exit the game"""
        return self.game.queue_scene_switch("exit")

    def first_frame(self, renderer: GfxRenderer):
        """Generate first frame"""

    def every_frame(self, renderer: GfxRenderer):
        """Generate frame"""


from .game import Game  # noqa
