import os
import typing

import sdl2
import sdl2.ext
from gamepart.context import Context
from gamepart.physics import PhysicalObject, World, pymunk
from gamepart.physics.vector import Vector
from gamepart.render import GfxRenderer
from gamepart.viewport import FlippedViewPort, ViewPort

from scenes.base import MyBaseScene

from .ball import Ball, TexturedBall
from .chunk import TerrainChunkManager
from .player import Player, PlayerController

FALL_LIMIT_Y = -10000.0
RESPAWN_Y = 500.0


class BallScene(MyBaseScene):
    bg_color = sdl2.ext.Color(255, 255, 255)

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.world: World
        self.viewport: ViewPort
        self.player: Player
        self.player_ctrl: PlayerController
        self.terrain_chunk_manager: TerrainChunkManager
        self.last_click: tuple[float, float] = (0, 0)

    def init(self) -> None:
        super().init()
        self.world = World()
        self.world.space.gravity = (0, -1000)
        self.system.add(self.world)
        self.viewport = FlippedViewPort(
            self.game.renderer, self.game.width, self.game.height
        )
        self.viewport.change_zoom(0.5)
        self.system.add(self.viewport)

        self.keyboard_event.on_up(sdl2.SDLK_F2, self.switch_to_test)
        self.keyboard_event.on_down(sdl2.SDLK_w, self.player_jump)
        self.mouse_button_event.on_down(sdl2.SDL_BUTTON_LEFT, self.start_drag)
        self.mouse_button_event.on_up(sdl2.SDL_BUTTON_LEFT, self.end_drag)
        self.mouse_button_event.on_up(sdl2.SDL_BUTTON_RIGHT, self.delete_ball)
        self.event_dispatcher.on(sdl2.SDL_MOUSEWHEEL, self.change_zoom)

        self.player = Player(position=(200, 300))
        self.player_ctrl = PlayerController(self.player)
        if self.keyboard_event is not None and self.player_ctrl is not None:
            self.keyboard_event.on_down(
                sdl2.SDLK_e, self.player_ctrl.setter("shoot", True)
            )

    def start(self, context: Context) -> None:
        self.system.clear_all()
        super().start(context)
        if self.game.sprite_factory is None:
            return
        resources_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            "resources",
        )
        tex = self.game.sprite_factory.from_image(
            os.path.join(resources_path, "cube.png")
        )
        self.system.add_all(
            Ball(30, 20, (100, 100), (100, 100)),
            Ball(40, 30, (200, 200), (100, 100)),
            TexturedBall(40, 30, (300, 300), (0, 0), texture=tex, scale=0.75),
            self.player,
        )

        self.chunk_manager = TerrainChunkManager(
            self.system,
            self.world.space.static_body,
        )
        self.chunk_manager.update(self.player.position)

    def change_zoom(self, event: sdl2.SDL_Event) -> None:
        pos = self.viewport.to_world(self.game.mouse_state[0:2])
        if event.wheel.y > 0:
            if self.viewport.zoom <= 16:
                self.viewport.change_zoom(1.25, pos)
        elif event.wheel.y < 0:
            if self.viewport.zoom >= 1 / 16:
                self.viewport.change_zoom(0.75, pos)

    def start_drag(self, event: sdl2.SDL_Event) -> None:
        self.last_click = self.viewport.to_world((event.button.x, event.button.y))

    def end_drag(self, event: sdl2.SDL_Event) -> None:
        if self.viewport is None or self.world is None or self.system is None:
            return
        click = self.viewport.to_world((event.button.x, event.button.y))
        p = Vector(*self.last_click)
        v = (Vector(*click) - p) * 4
        self.system.add_all(
            Ball(position=p.to_tuple(), velocity=v.to_tuple(), radius=30, mass=20)
        )

    def delete_ball(self, event: sdl2.SDL_Event) -> None:
        pos = Vector.to(self.viewport.to_world((event.button.x, event.button.y)))
        rem = None
        for c in self.world.get_objects(Ball):
            if (pos - c.position).r <= c.radius:
                rem = c
                break
        if rem is not None:
            self.system.remove_all(rem)

    def switch_to_test(self, _: typing.Any = None) -> None:
        self.game.queue_scene_switch("test")

    def player_jump(self, event: sdl2.SDL_Event) -> None:
        if not event.key.repeat:
            self.player_ctrl.input.jump = True

    def tick(self, delta: float) -> None:
        self.player_ctrl.input.left = bool(self.game.key_state[sdl2.SDL_SCANCODE_A])
        self.player_ctrl.input.right = bool(self.game.key_state[sdl2.SDL_SCANCODE_D])
        self.player_ctrl.input.shoot = bool(self.game.key_state[sdl2.SDL_SCANCODE_E])
        self.player_ctrl.control(self.game.world_time, delta)
        self.world.tick(delta)
        self.chunk_manager.update(self.player.position)
        self._update_fallen_objects()
        self._update_camera(delta)

    def every_frame(self, renderer: GfxRenderer) -> None:
        renderer.clear(self.bg_color)
        self.viewport.draw()
        super().every_frame(renderer)

    def _update_fallen_objects(self) -> None:
        for obj in self.world.get_objects(PhysicalObject):
            if obj.body is None or obj.body.body_type == pymunk.Body.STATIC:
                continue
            current_x, current_y = obj.position
            if current_y < FALL_LIMIT_Y:
                if isinstance(obj, Ball):
                    self.system.remove_all(obj)
                else:
                    obj.position = (
                        current_x,
                        self.chunk_manager.get_terrain_height(current_x) + 100,
                    )
                    obj.body.velocity = (0, 0)

    def _update_camera(self, delta: float) -> None:
        self.viewport.follow_target(
            self.player.position,
            delta,
        )
