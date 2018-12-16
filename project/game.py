import time
import math
import os

import sdl2
import sdl2.ext

from gamepart import Game, SimpleScene
from gamepart.context import Context
from gamepart.physics import (
    World,
    Vector,
    CircleObject,
    PointObject,
    LineObject,
    RectangleObject,
)


class Ball(CircleObject):
    pass


class Pixel(PointObject):
    pass


class Line(LineObject):
    pass


class Rect(RectangleObject):
    pass


class TestScene(SimpleScene):
    def init(self):
        super(TestScene, self).init()
        self.key_event.on_up(sdl2.SDLK_COMMA, self.decrease_fps)
        self.key_event.on_up(sdl2.SDLK_PERIOD, self.increase_fps)
        self.key_event.on_up(sdl2.SDLK_SPACE, self.switch_to_balls)
        # time.sleep(1)

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
        # self.balls = []  # x, y, vx, vy, r
        self.world = World(time_step=1 / 1024, speed=1.0)
        self.last_click = (0, 0)

    def init(self):
        super(BallScene, self).init()
        self.key_event.on_up(sdl2.SDLK_SPACE, self.switch_to_test)
        self.mouse_event.on_down(sdl2.SDL_BUTTON_LEFT, self.start_drag)
        self.mouse_event.on_up(sdl2.SDL_BUTTON_LEFT, self.end_drag)
        self.mouse_event.on_up(sdl2.SDL_BUTTON_RIGHT, self.delete_ball)

    def start(self, context: Context):
        super(BallScene, self).start(context)
        self.world.clear()
        self.world.add(
            # Ball(position=(50, 100), velocity=(200, 0), radius=25),
            # Ball(position=(400, 100), velocity=(-200, 0.000000001), radius=50, mass=4, restitution=0.9),
            Pixel(velocity=(50, 50)),
            Line(position=(300, 300), width=300),
        )

    def start_drag(self, event: sdl2.SDL_Event):
        self.last_click = (event.button.x, self.game.height - event.button.y)
        print(self.last_click)

    def end_drag(self, event: sdl2.SDL_Event):
        p = Vector.to(self.last_click)
        v = Vector.to((event.button.x, self.game.height - event.button.y)) - p
        self.world.add(Ball(position=p, velocity=v * 4, radius=30, mass=2))

    def delete_ball(self, event: sdl2.SDL_Event):
        pos = Vector.to((event.button.x, self.game.height - event.button.y))
        rem = None
        for ball in self.world.objects:
            if (ball.position - pos).r <= getattr(ball, "radius", 1):
                rem = ball
        if rem:
            self.world.objects.remove(rem)

    def switch_to_test(self, _=None):
        self.game.queue_scene_switch("test")

    def tick(self, delta: float):
        for ball in self.world.objects:
            x, y = ball.position
            vx, vy = ball.velocity
            r = getattr(ball, "radius", 1)
            if x + vx * delta + r >= self.game.width and vx > 0:
                vx = -abs(vx)
            elif x + vx * delta - r <= 0 and vx < 0:
                vx = abs(vx)
            if y + vy * delta + r >= self.game.height and vy > 0:
                vy = -abs(vy)
            elif y + vy * delta - r <= 0 and vy < 0:
                vy = abs(vy)
            # vy -= 1000 * delta
            ball.velocity.update(vx, vy)
            # x += vx * delta
            # y += vy * delta
            # ball[:] = [x, y, vx, vy, r]
        self.world.tick(delta)

    def every_frame(self, renderer: sdl2.ext.Renderer):
        self.game.renderer.clear((255, 255, 255))
        # circles = [(x, self.game.height - y, r) for x, y, vx, vy, r in self.balls]
        circles = [
            (b.position.x, self.game.height - b.position.y, b.radius)
            for b in self.world.get_objects(Ball)
        ]
        self.game.renderer.filled_circle(circles, (0, 255, 0))

        pixels = [
            (p.position.x, self.game.height - p.position.y, 3)
            for p in self.world.get_objects(Pixel)
        ]
        self.game.renderer.filled_circle(pixels, (255, 0, 0))
        # self.game.renderer.pixel(pixels, (255, 0, 0))

        lines = [
            (
                l.end_points[0].x,
                self.game.height - l.end_points[0].y,
                l.end_points[1].x,
                self.game.height - l.end_points[1].y,
            )
            for l in self.world.get_objects(Line)
        ]
        self.game.renderer.line(lines, (0, 0, 255))

        # print("E =", self.world.get_energy())


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
        self.queue_scene_switch("balls")

    def get_config(self):
        config = super(MyGame, self).get_config()
        config["max_fps"] = 120
        # config["fullscreen"] = True
        return config
