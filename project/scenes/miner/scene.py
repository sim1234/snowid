import typing

import sdl2
import sdl2.ext
from context import MyContext
from gamepart.context import Context
from gamepart.gui.text import Text
from gamepart.render import GfxRenderer
from gamepart.viewport import CulledFlippedViewPort, ViewPort

from scenes.base import MyBaseScene

from .chunk import ResourceChunkManager
from .miner_entity import Miner
from .patch import ResourceType
from .ui import create_resource_panel

PANEL_WIDTH = 180
OVERLAY_PANEL_X = 10
OVERLAY_PANEL_Y = 10
MINER_COST_IRON = 10
MINER_COST_COPPER = 10
MINER_COST_COAL = 10
MINER_REFUND_IRON = 10
MINER_REFUND_COPPER = 10
MINER_REFUND_COAL = 10
STARTING_IRON = 50
STARTING_COPPER = 50
STARTING_COAL = 50
PRODUCTION_INTERVAL = 1.0
EDGE_PAN_MARGIN = 50
EDGE_PAN_SPEED = 400.0
ZOOM_MIN = 1 / 16
ZOOM_MAX = 16.0


def _point_in_panel(panel: typing.Any, px: int, py: int) -> bool:
    return panel.contains_point(px, py)


class MinerScene(MyBaseScene):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.viewport: ViewPort
        self.chunk_manager: ResourceChunkManager
        self.miners: list[Miner]
        self._iron: int = STARTING_IRON
        self._copper: int = STARTING_COPPER
        self._coal: int = STARTING_COAL
        self._timer_acc: float = 0.0
        self._panel: typing.Any = None
        self._iron_text: typing.Any = None
        self._iron_per_sec_text: typing.Any = None
        self._copper_text: typing.Any = None
        self._copper_per_sec_text: typing.Any = None
        self._coal_text: typing.Any = None
        self._coal_per_sec_text: typing.Any = None
        self._patch_tooltip: typing.Any = None

    @property
    def iron(self) -> int:
        return self._iron

    @iron.setter
    def iron(self, value: int) -> None:
        self._iron = max(0, value)

    @property
    def copper(self) -> int:
        return self._copper

    @copper.setter
    def copper(self, value: int) -> None:
        self._copper = max(0, value)

    @property
    def coal(self) -> int:
        return self._coal

    @coal.setter
    def coal(self, value: int) -> None:
        self._coal = max(0, value)

    def init(self) -> None:
        super().init()
        self.viewport = CulledFlippedViewPort(
            self.game.renderer,
            self.game.width,
            self.game.height,
            zoom=0.8,
            x=0.0,
            y=0.0,
            cull_margin=100.0,
        )
        self.system.add(self.viewport)
        self.miners = []

    def start(self, context: Context) -> None:
        super().start(context)
        assert isinstance(context, MyContext)
        (
            self._panel,
            self._iron_text,
            self._iron_per_sec_text,
            self._copper_text,
            self._copper_per_sec_text,
            self._coal_text,
            self._coal_per_sec_text,
        ) = create_resource_panel(self.gui, PANEL_WIDTH)
        self._panel.x = OVERLAY_PANEL_X
        self._panel.y = OVERLAY_PANEL_Y
        self._patch_tooltip = Text(
            x=0,
            y=0,
            width=120,
            height=22,
            text="",
            font="sans",
            font_size=14,
            color=(240, 240, 240, 255),
            background_color=(40, 40, 45, 230),
        )
        self.gui.add(self._patch_tooltip)
        self._patch_tooltip.visible = False
        self.chunk_manager = ResourceChunkManager(self.system)
        self.chunk_manager.update((0.0, 0.0), rings=2)
        self.mouse_button_event.on_down(sdl2.SDL_BUTTON_LEFT, self._on_left_click)
        self.mouse_button_event.on_up(sdl2.SDL_BUTTON_RIGHT, self._on_right_click)
        self.event_dispatcher.on(sdl2.SDL_MOUSEWHEEL, self._change_zoom)
        self.keyboard_event.on_up(
            sdl2.SDLK_ESCAPE,
            lambda e: self.game.queue_scene_switch("main_menu"),
        )

    def stop(self) -> MyContext:
        self.system.clear_all()
        return super().stop()

    def _screen_to_world(self, screen_x: int, screen_y: int) -> tuple[float, float]:
        return self.viewport.to_world((float(screen_x), float(screen_y)))

    def _change_zoom(self, event: sdl2.SDL_Event) -> None:
        mx, my = self.game.mouse_state[0], self.game.mouse_state[1]
        pos = self.viewport.to_world((float(mx), float(my)))
        if event.wheel.y > 0:
            if self.viewport.zoom <= ZOOM_MAX:
                self.viewport.change_zoom(1.25, pos)
        elif event.wheel.y < 0:
            if self.viewport.zoom >= ZOOM_MIN:
                self.viewport.change_zoom(0.75, pos)

    def _update_camera(self, delta: float) -> None:
        dx = 0.0
        dy = 0.0
        mx, my = self.game.mouse_state[0], self.game.mouse_state[1]
        in_world = 0 <= mx < self.game.width and 0 <= my < self.game.height
        if in_world:
            if mx < EDGE_PAN_MARGIN:
                dx -= 1.0
            elif mx >= self.game.width - EDGE_PAN_MARGIN:
                dx += 1.0
            if my < EDGE_PAN_MARGIN:
                dy += 1.0
            elif my >= self.game.height - EDGE_PAN_MARGIN:
                dy -= 1.0
        sc_left = sdl2.SDL_GetScancodeFromKey(sdl2.SDLK_LEFT)
        sc_right = sdl2.SDL_GetScancodeFromKey(sdl2.SDLK_RIGHT)
        sc_up = sdl2.SDL_GetScancodeFromKey(sdl2.SDLK_UP)
        sc_down = sdl2.SDL_GetScancodeFromKey(sdl2.SDLK_DOWN)
        if self.game.key_state[sc_left]:
            dx -= 1.0
        if self.game.key_state[sc_right]:
            dx += 1.0
        if self.game.key_state[sc_up]:
            dy += 1.0
        if self.game.key_state[sc_down]:
            dy -= 1.0
        if dx != 0 or dy != 0:
            move = EDGE_PAN_SPEED * delta
            self.viewport.x += dx * move
            self.viewport.y += dy * move

    def _on_left_click(self, event: sdl2.SDL_Event) -> None:
        if _point_in_panel(self._panel, event.button.x, event.button.y):
            return
        wx, wy = self._screen_to_world(event.button.x, event.button.y)
        patch = self.chunk_manager.get_patch_at((wx, wy))
        if patch is None:
            return
        if any(m.patch is patch for m in self.miners):
            return
        if (
            self.iron < MINER_COST_IRON
            or self.copper < MINER_COST_COPPER
            or self.coal < MINER_COST_COAL
        ):
            return
        self.iron -= MINER_COST_IRON
        self.copper -= MINER_COST_COPPER
        self.coal -= MINER_COST_COAL
        miner = Miner(patch)
        self.miners.append(miner)
        self.system.add_all(miner)

    def _on_right_click(self, event: sdl2.SDL_Event) -> None:
        if _point_in_panel(self._panel, event.button.x, event.button.y):
            return
        wx, wy = self._screen_to_world(event.button.x, event.button.y)
        for i, miner in enumerate(self.miners):
            if miner.contains_point((wx, wy)):
                self.miners.pop(i)
                self.system.remove_all(miner)
                self.iron += MINER_REFUND_IRON
                self.copper += MINER_REFUND_COPPER
                self.coal += MINER_REFUND_COAL
                return

    def tick(self, delta: float) -> None:
        self._timer_acc += delta
        while self._timer_acc >= PRODUCTION_INTERVAL:
            self._timer_acc -= PRODUCTION_INTERVAL
            self._run_miner_production()
        self._update_camera(delta)
        self.chunk_manager.update(self.viewport.center, rings=2)

    def _run_miner_production(self) -> None:
        to_remove: list[Miner] = []
        for miner in self.miners:
            if miner.patch.richness <= 0:
                to_remove.append(miner)
                continue
            resource: ResourceType = miner.patch.resource_type
            if resource == "iron":
                self.iron += 1
            elif resource == "copper":
                self.copper += 1
            else:
                self.coal += 1
            miner.patch.deplete(1)
            if miner.patch.richness <= 0:
                to_remove.append(miner)
        for miner in to_remove:
            self.miners.remove(miner)
            self.system.remove_all(miner)

    def every_frame(self, renderer: GfxRenderer) -> None:
        renderer.clear((30, 30, 35, 255))
        self.viewport.draw()
        self._iron_text.text = f"Iron: {self.iron}"
        iron_per_sec = sum(
            1
            for m in self.miners
            if m.patch.resource_type == "iron" and m.patch.richness > 0
        )
        self._iron_per_sec_text.text = f"Iron/s: {iron_per_sec}"
        self._copper_text.text = f"Copper: {self.copper}"
        copper_per_sec = sum(
            1
            for m in self.miners
            if m.patch.resource_type == "copper" and m.patch.richness > 0
        )
        self._copper_per_sec_text.text = f"Copper/s: {copper_per_sec}"
        self._coal_text.text = f"Coal: {self.coal}"
        coal_per_sec = sum(
            1
            for m in self.miners
            if m.patch.resource_type == "coal" and m.patch.richness > 0
        )
        self._coal_per_sec_text.text = f"Coal/s: {coal_per_sec}"
        mx, my = self.game.mouse_state[0], self.game.mouse_state[1]
        if not _point_in_panel(self._panel, mx, my):
            world_pos = self._screen_to_world(mx, my)
            patch = self.chunk_manager.get_patch_at(world_pos)
            if patch is not None:
                self._patch_tooltip.text = f"Richness: {patch.richness}"
                offset = 14
                tx = mx + offset
                ty = my + offset
                if tx + self._patch_tooltip.width > self.game.width:
                    tx = mx - self._patch_tooltip.width - offset
                if ty + self._patch_tooltip.height > self.game.height:
                    ty = my - self._patch_tooltip.height - offset
                if tx < 0:
                    tx = 0
                if ty < 0:
                    ty = 0
                self._patch_tooltip.x = tx
                self._patch_tooltip.y = ty
                self._patch_tooltip.visible = True
            else:
                self._patch_tooltip.visible = False
        else:
            self._patch_tooltip.visible = False
        self.gui.draw()
