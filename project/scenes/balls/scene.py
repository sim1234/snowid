import os
import typing

import sdl2
import sdl2.ext
from gamepart.context import Context
from gamepart.noise import PerlinNoise
from gamepart.physics import World
from gamepart.physics.vector import Vector
from gamepart.render import GfxRenderer
from gamepart.viewport import FlippedViewPort, ViewPort

from ..base import MyBaseScene
from .ball import Ball, TexturedBall
from .chunk import TerrainChunkManager
from .player import Player, PlayerController


class BallScene(MyBaseScene):
    bg_color = sdl2.ext.Color(255, 255, 255)

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.world: World | None = None
        self.viewport: ViewPort | None = None
        self.last_click: tuple[float, float] = (0, 0)
        self.player: Player | None = None
        self.player_ctrl: PlayerController | None = None
        self.terrain_chunk_manager: TerrainChunkManager | None = None

    def init(self) -> None:
        super().init()
        if self.system is None:
            return
        self.world = World()
        self.world.space.gravity = (0, -1000)
        self.system.add(self.world)
        if self.game.renderer is None:
            return
        self.viewport = FlippedViewPort(
            self.game.renderer, self.game.width, self.game.height
        )
        self.viewport.change_zoom(0.5)
        self.system.add(self.viewport)

        self.noise = PerlinNoise(seed=42, octaves=4, persistence=0.5, scale=1000.0)

        if self.key_event is not None:
            self.key_event.on_up(sdl2.SDLK_F2, self.switch_to_test)
            self.key_event.on_down(sdl2.SDLK_w, self.player_jump)
        if self.mouse_event is not None:
            self.mouse_event.on_down(sdl2.SDL_BUTTON_LEFT, self.start_drag)
            self.mouse_event.on_up(sdl2.SDL_BUTTON_LEFT, self.end_drag)
            self.mouse_event.on_up(sdl2.SDL_BUTTON_RIGHT, self.delete_ball)
        if hasattr(self, "_event_dispatcher") and self._event_dispatcher is not None:
            self._event_dispatcher.on(sdl2.SDL_MOUSEWHEEL, self.change_zoom)

        self.player = Player(position=(200, 300))
        self.player_ctrl = PlayerController(self.player)
        if self.key_event is not None and self.player_ctrl is not None:
            self.key_event.on_down(sdl2.SDLK_e, self.player_ctrl.setter("shoot", True))

    def start(self, context: Context) -> None:
        if self.system is None or self.world is None:
            return
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
        if self.player is not None:
            self.system.add_all(
                Ball(30, 20, (100, 100), (100, 100)),
                Ball(40, 30, (200, 200), (100, 100)),
                TexturedBall(40, 30, (300, 300), (0, 0), texture=tex, scale=0.75),
                self.player,
            )

            self.chunk_manager = TerrainChunkManager(
                self.system,
                self.world.space.static_body,
                self.noise,
            )
            self.chunk_manager.update(self.player.position)

    def change_zoom(self, event: sdl2.SDL_Event) -> None:
        if self.viewport is None:
            return
        pos = self.viewport.to_world(self.game.mouse_state[0:2])
        if event.wheel.y > 0:
            if self.viewport.zoom <= 16:
                self.viewport.change_zoom(1.25, pos)
        elif event.wheel.y < 0:
            if self.viewport.zoom >= 1 / 16:
                self.viewport.change_zoom(0.75, pos)

    def start_drag(self, event: sdl2.SDL_Event) -> None:
        if self.viewport is None:
            return
        self.last_click = self.viewport.to_world((event.button.x, event.button.y))

    def end_drag(self, event: sdl2.SDL_Event) -> None:
        if self.viewport is None or self.world is None or self.system is None:
            return
        click = self.viewport.to_world((event.button.x, event.button.y))
        p = Vector.to(self.last_click)
        v = Vector.to(click) - p
        p_tuple: tuple[float, float] = (p.x, p.y)
        v_tuple: tuple[float, float] = ((v * 4).x, (v * 4).y)
        self.system.add_all(
            Ball(position=p_tuple, velocity=v_tuple, radius=30, mass=20)
        )

    def delete_ball(self, event: sdl2.SDL_Event) -> None:
        if self.viewport is None or self.world is None or self.system is None:
            return
        pos = Vector.to(self.viewport.to_world((event.button.x, event.button.y)))
        rem = None
        for c in self.world.get_objects(Ball):
            if (pos - c.position).r <= c.radius:
                rem = c
        if rem:
            self.system.remove_all(rem)

    def switch_to_test(self, _: typing.Any = None) -> None:
        self.game.queue_scene_switch("test")

    def player_jump(self, event: sdl2.SDL_Event) -> None:
        if self.player_ctrl is None:
            return
        if not event.key.repeat:
            self.player_ctrl.input.jump = True

    def tick(self, delta: float) -> None:
        if self.player_ctrl is None or self.world is None or self.player is None:
            return
        self.player_ctrl.input.left = bool(self.game.key_state[sdl2.SDL_SCANCODE_A])
        self.player_ctrl.input.right = bool(self.game.key_state[sdl2.SDL_SCANCODE_D])
        self.player_ctrl.input.shoot = bool(self.game.key_state[sdl2.SDL_SCANCODE_E])
        self.player_ctrl.control(self.game.world_time, delta)
        self.world.tick(delta)
        if self.chunk_manager is not None:
            self.chunk_manager.update(self.player.position)
        self._update_camera(delta)

    def _update_camera(self, delta: float) -> None:
        if self.viewport is None or self.player is None:
            return
        self.viewport.follow_target(
            self.player.position,
            delta,
        )

    def every_frame(self, renderer: GfxRenderer) -> None:
        if self.viewport is None:
            return
        renderer.clear(self.bg_color)
        self.viewport.draw()
        super().every_frame(renderer)
