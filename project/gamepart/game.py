import collections
import gc
import logging
import sys
import time
import typing

import sdl2
import sdl2.ext

from .context import Context
from .render import GfxRenderer
from .time import FPSCounter, TimeFeeder
from .utils import get_mouse_state

logger = logging.getLogger(__name__)


class Game:
    """Main game wrapper"""

    context_class: type[Context] = Context

    def __init__(self) -> None:
        logger.debug("Starting")
        self.init()

        self.config: dict[str, typing.Any] = self.get_config()
        self.width: int = self.config["width"]
        self.height: int = self.config["height"]
        self.max_fps: float = self.config["max_fps"]
        self.show_fps: bool = self.config["show_fps"]
        self.caption: str = self.config["caption"]
        self.fullscreen: bool = self.config["fullscreen"]
        self.time_step: float = self.config["time_step"]
        self.time_speed: float = self.config["time_speed"]
        self.time_max_iter: int = self.config["time_max_iter"]

        self.window: sdl2.ext.Window | None = None
        self.renderer: GfxRenderer | None = None
        self.sprite_factory: sdl2.ext.SpriteFactory | None = None
        self.font_manager: sdl2.ext.FontManager | None = None
        self.frame_num: int = 0
        self.init_display()
        self.init_renderer()
        self.init_sprite_factory()
        self.init_font_manager()
        self.display_loading_screen()
        self.init_heavy()

        self.fps_counter: FPSCounter = FPSCounter()
        self.feeder: TimeFeeder = TimeFeeder(self.time_step, self.time_speed)
        self.key_state: dict[int, bool] = sdl2.SDL_GetKeyboardState(None)
        self.mouse_state: tuple[int, int, int] = get_mouse_state()
        self.running: bool = False
        self.scenes: dict[str, Scene] = {}
        self.scene_switch_queue: collections.deque[Scene] = collections.deque()
        self.active_scene: Scene = self.add_exit_scene()
        self.context: Context = self.get_initial_context()
        self.logger.debug("Initializing scenes")
        self.init_scenes()
        self.fps_counter.clear()
        self.time_time: float = time.monotonic()
        self.logger.info("All systems nominal")
        gc.collect()

    @property
    def logger(self) -> logging.Logger:
        return logger

    def init(self) -> None:
        sdl2.ext.init()

    def init_display(self) -> None:
        self.logger.debug("Initializing display")
        flags = None
        if self.fullscreen:
            flags = sdl2.SDL_WINDOW_FULLSCREEN
        self.window = sdl2.ext.Window(
            self.caption, size=(self.width, self.height), flags=flags
        )
        if self.window is not None:
            self.window.show()

    def init_renderer(self) -> None:
        self.logger.debug("Initializing renderer")
        self.renderer = GfxRenderer(self.window)
        self.renderer.blendmode = sdl2.SDL_BLENDMODE_BLEND
        self.renderer.clip = (0, 0, self.width, self.height)

    def init_sprite_factory(self) -> None:
        self.logger.debug("Initializing sprite factory")
        self.sprite_factory = sdl2.ext.SpriteFactory(renderer=self.renderer)

    def init_font_manager(self) -> None:
        self.logger.warning("No FontManager initialized!")

    def init_scenes(self) -> None:
        for scene in self.scenes.values():
            scene.init()
        self.active_scene.start(self.context)

    def display_loading_screen(self) -> None:
        if (
            self.font_manager is None
            or self.sprite_factory is None
            or self.renderer is None
        ):
            return
        text = self.font_manager.render("Loading", size=24)
        pos = (
            int(self.width / 2.0 - text.w / 2.0),
            int(self.height / 2 - text.h / 2.0),
            text.w,
            text.h,
        )
        text = self.sprite_factory.from_surface(text, True)
        self.renderer.copy(text, None, pos)
        self.renderer.present()

    def display_fps(self) -> None:
        fps = int(self.fps_counter.get_fps())
        logger.debug(f"FPS={fps}")
        if (
            self.font_manager is None
            or self.sprite_factory is None
            or self.renderer is None
        ):
            return
        text = self.font_manager.render(
            f"{fps}", size=8, color=(200, 200, 50), bg_color=(10, 10, 10)
        )
        pos = (0, 0, text.w, text.h)
        text = self.sprite_factory.from_surface(text, True)
        self.renderer.copy(text, None, pos)

    def frame(self) -> None:
        self.mouse_state = get_mouse_state()
        self.frame_num += 1
        if self.scene_switch_queue:
            self.switch_scene(self.scene_switch_queue.popleft())
        for event in sdl2.ext.get_events():
            logger.debug("Event %r %r", event.common.timestamp, event.type)
            self.active_scene.event(event)
        self.tick()
        self.active_scene.frame()
        self.fps_counter.frame()
        if self.show_fps:
            self.display_fps()
        self.fps_counter.target_fps(self.max_fps)
        if self.renderer is not None:
            self.renderer.present()

    def tick(self) -> None:
        new_time = time.monotonic()
        for delta in self.feeder.tick(new_time - self.time_time, self.time_max_iter):
            self.active_scene.tick(delta)
        self.time_time = new_time

    def add_scene(
        self, name: str, scene: type["Scene"], *args: typing.Any, **kwargs: typing.Any
    ) -> "Scene":
        logger.debug(f"Adding scene {scene.__name__}(name={name!r})")
        if name in self.scenes:
            raise ValueError(f"Scene with name {name!r} already exists")
        s = scene(self, name, *args, **kwargs)
        self.scenes[name] = s
        return s

    def queue_scene_switch(self, name: str) -> None:
        logger.debug(f"Queuing scene change to {name!r}")
        self.scene_switch_queue.append(self.scenes[name])

    def switch_scene(self, scene: "Scene") -> None:
        logger.info(f"Changing scene from {self.active_scene.name!r} to {scene.name!r}")
        self.context = self.active_scene.stop()
        logger.debug("Context: %r", self.context)
        self.context.last_scene = self.active_scene
        self.active_scene = scene
        self.active_scene.start(self.context)

    def stop(self) -> None:
        logger.debug("Stopping")
        for scene in self.scenes.values():
            scene.uninit()
        sdl2.ext.quit()

    def main_loop(self) -> None:
        self.running = True
        while self.running:
            self.frame()
        self.stop()
        self.logger.info("Bye")

    def wrapped_main_loop(self) -> None:
        try:
            self.main_loop()
            r = 0
        except:  # noqa: E722
            logger.exception("Error in game")
            sdl2.ext.quit()
            r = 1
        sys.exit(r)  # Exit with right code

    def get_config(self) -> dict:
        return {
            "width": 640,
            "height": 480,
            "caption": self.__class__.__name__,
            "max_fps": 128,
            "show_fps": False,
            "fullscreen": False,
            "time_step": 1 / 128,
            "time_speed": 1.0,
            "time_max_iter": 8,
        }

    def get_initial_context(self) -> Context:
        return self.context_class(last_scene=self.active_scene)

    def add_exit_scene(self) -> "Scene":
        return self.add_scene("exit", ExitScene)

    @property
    def world_time(self) -> float:
        return self.feeder.world_time

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.caption!r})"

    def init_heavy(self) -> None:
        """Initialize some heavy machinery"""


from .scene import Scene, ExitScene  # noqa
