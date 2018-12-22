import sdl2
import sdl2.ext

from gamepart import SimpleScene
from gamepart.context import Context
from gamepart.physics import pymunk, World, PhysicalCircle
from gamepart.physics.vector import Vector
from gamepart.viewport import ViewPort, Circle


class Ball(Circle, PhysicalCircle):
    @property
    def color(self):
        return 0, 255, 0

    @property
    def position(self):
        return self.body.position

    @property
    def angle(self):
        return self.body.angle

    @property
    def radius(self):
        return self.shape.radius


class BallScene(SimpleScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.world: World = None
        self.viewport: ViewPort = None
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

        self.viewport = ViewPort(self.game.renderer, self.game.width, self.game.height)

        self.key_event.on_up(sdl2.SDLK_SPACE, self.switch_to_test)
        self.mouse_event.on_down(sdl2.SDL_BUTTON_LEFT, self.start_drag)
        self.mouse_event.on_up(sdl2.SDL_BUTTON_LEFT, self.end_drag)
        self.mouse_event.on_up(sdl2.SDL_BUTTON_RIGHT, self.delete_ball)

    def start(self, context: Context):
        super(BallScene, self).start(context)
        self.world.clear()
        self.viewport.clear()
        b = Ball(30, 20, (100, 100), (100, 100))
        self.world.add(b)
        self.viewport.add(b)
        b = Ball(40, 30, (200, 200), (100, 100))
        self.world.add(b)
        self.viewport.add(b)

    def start_drag(self, event: sdl2.SDL_Event):
        self.last_click = (event.button.x, self.game.height - event.button.y)

    def end_drag(self, event: sdl2.SDL_Event):
        p = Vector.to(self.last_click)
        v = Vector.to((event.button.x, self.game.height - event.button.y)) - p
        b = Ball(position=p, velocity=v * 4, radius=30, mass=20)
        self.world.add(b)
        self.viewport.add(b)

    def delete_ball(self, event: sdl2.SDL_Event):
        pos = Vector.to((event.button.x, self.game.height - event.button.y))
        rem = None
        for c in self.world.get_objects(Ball):
            if (pos - c.position).r <= c.radius:
                rem = c
        if rem:
            self.viewport.remove(*self.world.remove(rem))

    def switch_to_test(self, _=None):
        self.game.queue_scene_switch("test")

    def tick(self, delta: float):
        self.world.tick(delta)

    def every_frame(self, renderer: sdl2.ext.Renderer):
        self.game.renderer.clear((255, 255, 255))
        self.viewport.draw()
