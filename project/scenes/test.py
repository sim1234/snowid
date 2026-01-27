import math
import time
import typing

import sdl2.ext
from gamepart.render import GfxRenderer

from .base import MyBaseScene


class TestScene(MyBaseScene):
    def init(self) -> None:
        super().init()
        self.key_event.on_up(sdl2.SDLK_COMMA, self.decrease_fps)
        self.key_event.on_up(sdl2.SDLK_PERIOD, self.increase_fps)
        self.key_event.on_up(sdl2.SDLK_F2, self.switch_to_balls)

    def every_frame(self, renderer: GfxRenderer) -> None:
        self.game.renderer.clear((0, 0, 0, 255))
        # if random.random() > 0.9999:
        #     self.game.queue_scene_switch('test')
        # d = random.randint(1, 10)**6 / 10**6 / 50.0
        # time.sleep(d)
        x = int((math.sin(time.perf_counter()) + 1) * 150) + 50
        y = int((math.cos(time.perf_counter()) + 1) * 150) + 50
        self.game.renderer.fill((x, y, 50, 50), (0, 255, 0, 255))
        super().every_frame(renderer)

    def decrease_fps(self, _: typing.Any = None) -> None:
        self.game.max_fps /= 2
        self.game.fps_counter.clear()

    def increase_fps(self, _: typing.Any = None) -> None:
        self.game.max_fps *= 2
        self.game.fps_counter.clear()

    def switch_to_balls(self, _: typing.Any = None) -> None:
        self.game.queue_scene_switch("balls")
