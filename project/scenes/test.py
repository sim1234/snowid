import time
import math

import sdl2

from gamepart import SimpleScene
from gamepart.render import GfxRenderer


class TestScene(SimpleScene):
    def init(self):
        super().init()
        self.key_event.on_up(sdl2.SDLK_COMMA, self.decrease_fps)
        self.key_event.on_up(sdl2.SDLK_PERIOD, self.increase_fps)
        self.key_event.on_up(sdl2.SDLK_SPACE, self.switch_to_balls)
        # time.sleep(1)

    def every_frame(self, renderer: GfxRenderer):
        # if random.random() > 0.9999:
        #     self.game.queue_scene_switch('test')
        # d = random.randint(1, 10)**6 / 10**6 / 50.0
        # time.sleep(d)
        self.game.renderer.clear((0, 0, 0))
        x = int((math.sin(time.perf_counter()) + 1) * 150) + 50
        y = int((math.cos(time.perf_counter()) + 1) * 150) + 50
        self.game.renderer.fill((x, y, 50, 50), (0, 255, 0))

    def decrease_fps(self, _=None):
        self.game.max_fps /= 2
        self.game.fps_counter.clear()

    def increase_fps(self, _=None):
        self.game.max_fps *= 2
        self.game.fps_counter.clear()

    def switch_to_balls(self, _=None):
        self.game.queue_scene_switch("balls")
