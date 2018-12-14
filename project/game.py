import time
import math
import os

import sdl2
import sdl2.ext

from gamepart import Game, SimpleScene
from gamepart.context import Context


class TestScene(SimpleScene):
    def init(self):
        super(TestScene, self).init()
        self.key_event.on_up(sdl2.SDLK_COMMA, self.decrease_fps)
        self.key_event.on_up(sdl2.SDLK_PERIOD, self.increase_fps)
        self.key_event.on_up(sdl2.SDLK_SPACE, self.switch_to_balls)
        time.sleep(1)

    def every_frame(self, renderer: sdl2.ext.Renderer):
        # if random.random() > 0.9999:
        #     self.game.queue_scene_switch('my')
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


class BallScene(SimpleScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.balls = []  # x, y, vx, vy, r

    def init(self):
        super(BallScene, self).init()
        self.key_event.on_up(sdl2.SDLK_SPACE, self.switch_to_test)

    def start(self, context: Context):
        super(BallScene, self).start(context)
        self.balls.clear()
        self.balls.append([50, 50, 200, 400, 25])
        self.balls.append([250, 200, 150, 200, 50])

    def switch_to_test(self, _=None):
        self.game.queue_scene_switch("test")

    def tick(self, delta: float):
        for ball in self.balls:
            x, y, vx, vy, r = ball
            if x + vx * delta + r >= self.game.width and vx > 0:
                vx = -abs(vx)
            elif x + vx * delta - r <= 0 and vx < 0:
                vx = abs(vx)
            if y + vy * delta + r >= self.game.height and vy > 0:
                vy = -abs(vy)
            elif y + vy * delta - r <= 0 and vy < 0:
                vy = abs(vy)
            vy -= 1000 * delta
            x += vx * delta
            y += vy * delta
            ball[:] = [x, y, vx, vy, r]

    def every_frame(self, renderer: sdl2.ext.Renderer):
        self.game.renderer.clear((255, 255, 255))
        # circles = [(x, y, r) for x, y, vx, vy, r in self.balls]
        # self.game.renderer.circle(circles, (0, 255, 0))

        import sdl2.sdlgfx

        for x, y, vx, vy, r in self.balls:
            self.game.renderer.circle((x, y, r), (0, 255, 0, 127))
            # sdl2.sdlgfx.filledCircleRGBA(
            #     self.game.renderer.sdlrenderer,
            #     int(x),
            #     int(self.game.height - y),
            #     r,
            #     0,
            #     255,
            #     0,
            #     255,
            # )


class MyGame(Game):
    def init_font_manager(self):
        directory = os.path.dirname(os.path.abspath(__file__))
        self.font_manager = sdl2.ext.FontManager(
            os.path.join(directory, "resources", "PixelFJVerdana12pt.ttf")
        )

    def init_scenes(self):
        self.add_scene("test", TestScene)
        self.add_scene("balls", BallScene)
        super(MyGame, self).init_scenes()
        self.queue_scene_switch("test")

    def get_config(self):
        config = super(MyGame, self).get_config()
        config["max_fps"] = 120
        # config["fullscreen"] = True
        return config
