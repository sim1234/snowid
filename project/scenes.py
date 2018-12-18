import time
import math
import os

import sdl2
import sdl2.ext
import pymunk

from gamepart import Game, SimpleScene
from gamepart.context import Context
from gamepart.physics import World, Circle
from gamepart.physics.vector import Vector


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
        self.world: World = None
        self.last_click = (0, 0)

    def init(self):
        super(BallScene, self).init()
        self.world = World()
        self.world.space.gravity = (0, -1000)
        static_lines = [
            pymunk.Segment(
                self.world.space.static_body, (0, 0), (0, self.game.height), 0.0
            ),
            pymunk.Segment(
                self.world.space.static_body,
                (0, self.game.height),
                (self.game.width, self.game.height),
                0.0,
            ),
            pymunk.Segment(
                self.world.space.static_body,
                (self.game.width, self.game.height),
                (self.game.width, 0),
                0.0,
            ),
            pymunk.Segment(
                self.world.space.static_body, (self.game.width, 0), (0, 0), 0.0
            ),
        ]
        for line in static_lines:
            line.elasticity = 1.0
            line.friction = 1.0
        self.world.space.add(static_lines)

        self.key_event.on_up(sdl2.SDLK_SPACE, self.switch_to_test)
        self.mouse_event.on_down(sdl2.SDL_BUTTON_LEFT, self.start_drag)
        self.mouse_event.on_up(sdl2.SDL_BUTTON_LEFT, self.end_drag)
        self.mouse_event.on_up(sdl2.SDL_BUTTON_RIGHT, self.delete_ball)

    def start(self, context: Context):
        super(BallScene, self).start(context)
        self.world.clear()
        self.world.add(Circle(30, 20, (100, 100), (100, 100)))
        self.world.add(Circle(40, 30, (200, 200), (100, 100)))

    def start_drag(self, event: sdl2.SDL_Event):
        self.last_click = (event.button.x, self.game.height - event.button.y)

    def end_drag(self, event: sdl2.SDL_Event):
        p = Vector.to(self.last_click)
        v = Vector.to((event.button.x, self.game.height - event.button.y)) - p
        self.world.add(Circle(position=p, velocity=v * 4, radius=30, mass=20))

    def delete_ball(self, event: sdl2.SDL_Event):
        pos = Vector.to((event.button.x, self.game.height - event.button.y))
        rem = None
        for c in self.world.get_objects(Circle):
            if (pos - c.position).r <= c.radius:
                rem = c
        if rem:
            self.world.remove(rem)

    def switch_to_test(self, _=None):
        self.game.queue_scene_switch("test")

    def tick(self, delta: float):
        self.world.tick(delta)

    def every_frame(self, renderer: sdl2.ext.Renderer):
        self.game.renderer.clear((255, 255, 255))
        circles = [
            (c.position.x, self.game.height - c.position.y, c.radius)
            for c in self.world.get_objects(Circle)
        ]
        self.game.renderer.filled_circle(circles, (0, 255, 0))


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
