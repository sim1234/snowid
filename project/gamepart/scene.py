import sdl2
import sdl2.ext

from .context import Context
from .event import EventDispatcher, KeyEventDispatcher, MouseEventDispatcher


class Scene:
    """Scene base"""

    def __init__(self, game: "Game", name: str, *args, **kwargs):
        self.game: "Game" = game
        self.name: str = name
        self.args = args
        self.kwargs = kwargs
        self.is_first_frame = True
        self.context: Context = None

    def init(self):
        """Configure Scene"""

    def start(self, context: Context):
        """Start displaying Scene"""
        self.context = context

    def frame(self):
        """Generate frame"""

    def tick(self, delta: float):
        """Move forward in time"""

    def stop(self) -> Context:
        """Stop displaying Scene"""
        return self.context

    def event(self, event: sdl2.SDL_Event):
        """Handle event"""

    def __repr__(self):
        return f"{self.__class__.__name__}({self.game!r}, {self.name!r})"


class ExitScene(Scene):
    """Scene quitting the game"""

    def frame(self):
        self.game.running = False


class SimpleScene(Scene):
    """Scene with some utility functions"""

    def __init__(self, *args, **kwargs):
        super(SimpleScene, self).__init__(*args, **kwargs)
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
        return super(SimpleScene, self).start(context)

    def frame(self):
        if self.is_first_frame:
            self.first_frame(self.game.renderer)
            self.is_first_frame = False
        if self.game.ticks_delta:
            self.tick(self.game.ticks_delta)
        return self.every_frame(self.game.renderer)

    def on_exit(self, event: sdl2.SDL_Event):
        """Handle exit event"""
        self.exit()

    def exit(self):
        """Exit the game"""
        return self.game.queue_scene_switch("exit")

    def first_frame(self, renderer: sdl2.ext.Renderer):
        """Generate first frame"""

    def every_frame(self, renderer: sdl2.ext.Renderer):
        """Generate frame"""


from .game import Game  # noqa
