import typing

import sdl2
import sdl2.ext

from gamepart import SimpleScene
from gamepart.context import Context
from gamepart.physics import pymunk, World, PhysicalCircle, SimplePhysicalObject
from gamepart.physics.vector import Vector
from gamepart.viewport import ViewPort, FlippedViewPort, Circle, Line


class Ball(Circle, PhysicalCircle):  # type: ignore
    color = (0, 255, 0)

    @property
    def angle(self):
        return self.body.angle


class BoundLine(Line, SimplePhysicalObject[pymunk.Segment]):  # type: ignore
    color = (255, 0, 0)

    def __init__(
        self, static_body: pymunk.Body, p1x: float, p1y: float, p2x: float, p2y: float
    ):
        shape = pymunk.Segment(static_body, (p1x, p1y), (p2x, p2y), 0.0)
        shape.elasticity = 1.0
        shape.friction = 1.0
        super().__init__(None, shape)

    @property
    def end_points(self):
        return self.shape.a, self.shape.b

    @classmethod
    def make_box(
        cls,
        static_body: pymunk.Body,
        width: float,
        height: float,
        start_x: float = 0.0,
        start_y: float = 0.0,
    ) -> typing.Generator["BoundLine", None, None]:
        end_x = start_x + width
        end_y = start_y + height
        yield cls(static_body, start_x, start_y, end_x, start_y)
        yield cls(static_body, end_x, start_y, end_x, end_y)
        yield cls(static_body, end_x, end_y, start_x, end_y)
        yield cls(static_body, start_x, end_y, start_x, start_y)


class BallScene(SimpleScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.world: World = None
        self.viewport: ViewPort = None
        self.last_click = (0, 0)

    def init(self):
        super().init()
        self.world = World(1 / 2 ** 8, 1.0)
        self.world.space.gravity = (0, -1000)
        self.system.add(self.world)
        self.viewport = FlippedViewPort(
            self.game.renderer, self.game.width, self.game.height
        )
        self.viewport.change_zoom(0.5)
        self.system.add(self.viewport)

        self.key_event.on_up(sdl2.SDLK_SPACE, self.switch_to_test)
        self.mouse_event.on_down(sdl2.SDL_BUTTON_LEFT, self.start_drag)
        self.mouse_event.on_up(sdl2.SDL_BUTTON_LEFT, self.end_drag)
        self.mouse_event.on_up(sdl2.SDL_BUTTON_RIGHT, self.delete_ball)
        self.event.on(sdl2.SDL_MOUSEWHEEL, self.change_zoom)

    def start(self, context: Context):
        super(BallScene, self).start(context)
        self.system.clear_all()
        self.system.add_all(Ball(30, 20, (100, 100), (100, 100)))
        self.system.add_all(Ball(40, 30, (200, 200), (100, 100)))
        self.system.add_all(
            *BoundLine.make_box(
                self.world.space.static_body,
                self.game.width - 3,
                self.game.height - 2,
                1,
                2,
            )
        )

    def change_zoom(self, event: sdl2.SDL_Event):
        pos = self.viewport.to_world(self.game.mouse_state[0:2])
        if event.wheel.y > 0:
            if self.viewport.zoom <= 16:
                self.viewport.change_zoom(1.25, pos)
        elif event.wheel.y < 0:
            if self.viewport.zoom >= 1 / 16:
                self.viewport.change_zoom(0.75, pos)

    def start_drag(self, event: sdl2.SDL_Event):
        self.last_click = self.viewport.to_world((event.button.x, event.button.y))

    def end_drag(self, event: sdl2.SDL_Event):
        click = self.viewport.to_world((event.button.x, event.button.y))
        p = Vector.to(self.last_click)
        v = Vector.to(click) - p
        self.system.add_all(Ball(position=p, velocity=v * 4, radius=30, mass=20))

    def delete_ball(self, event: sdl2.SDL_Event):
        pos = Vector.to(self.viewport.to_world((event.button.x, event.button.y)))
        rem = None
        for c in self.world.get_objects(Ball):
            if (pos - c.position).r <= c.radius:
                rem = c
        if rem:
            self.system.remove_all(rem)

    def switch_to_test(self, _=None):
        self.game.queue_scene_switch("test")

    def tick(self, delta: float):
        self.world.tick(delta)

    def every_frame(self, renderer: sdl2.ext.Renderer):
        renderer.clear((255, 255, 255))
        self.viewport.draw()
