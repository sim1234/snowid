import sdl2
import sdl2.ext

from gamepart.physics import World
from gamepart.physics.vector import Vector
from gamepart.render import GfxRenderer
from gamepart.viewport import ViewPort, FlippedViewPort

from ..base import MyBaseScene, MyContext
from .line import BoundLine
from .ball import Ball, TexturedBall
from .player import Player, PlayerController


class BallScene(MyBaseScene):
    bg_color = sdl2.ext.Color(255, 255, 255)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.world: World = None
        self.viewport: ViewPort = None
        self.last_click = (0, 0)
        self.player: Player = None
        self.player_ctrl: PlayerController = None

    def init(self):
        super().init()
        self.world = World()
        self.world.space.gravity = (0, -1000)
        self.system.add(self.world)
        self.viewport = FlippedViewPort(
            self.game.renderer, self.game.width, self.game.height
        )
        self.viewport.change_zoom(0.5)
        self.system.add(self.viewport)

        self.key_event.on_up(sdl2.SDLK_F2, self.switch_to_test)
        self.key_event.on_down(sdl2.SDLK_w, self.player_jump)
        self.mouse_event.on_down(sdl2.SDL_BUTTON_LEFT, self.start_drag)
        self.mouse_event.on_up(sdl2.SDL_BUTTON_LEFT, self.end_drag)
        self.mouse_event.on_up(sdl2.SDL_BUTTON_RIGHT, self.delete_ball)
        self.event.on(sdl2.SDL_MOUSEWHEEL, self.change_zoom)

        self.player = Player(position=(200, 300))
        self.player_ctrl = PlayerController(self.player)
        self.key_event.on_down(sdl2.SDLK_e, self.player_ctrl.setter("shoot", True))

    def start(self, context: MyContext):
        self.system.clear_all()
        super().start(context)
        tex = self.game.sprite_factory.from_image("resources/cube.png")
        self.system.add_all(
            Ball(30, 20, (100, 100), (100, 100)),
            Ball(40, 30, (200, 200), (100, 100)),
            TexturedBall(40, 30, (300, 300), (0, 0), texture=tex, scale=0.75),
            self.player,
        )
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

    def player_jump(self, event: sdl2.SDL_Event):
        if not event.key.repeat:
            self.player_ctrl.input.jump = True

    def tick(self, delta: float):
        self.player_ctrl.input.left = bool(self.game.key_state[sdl2.SDL_SCANCODE_A])
        self.player_ctrl.input.right = bool(self.game.key_state[sdl2.SDL_SCANCODE_D])
        self.player_ctrl.input.shoot = bool(self.game.key_state[sdl2.SDL_SCANCODE_E])
        self.player_ctrl.control(self.game.world_time, delta)
        self.world.tick(delta)

    def every_frame(self, renderer: GfxRenderer):
        renderer.clear(self.bg_color)
        self.viewport.draw()
        super().every_frame(renderer)
