from __future__ import annotations

import array
import ctypes
import math
import queue
import threading

import sdl2
import sdl2.ext
from context import MyContext
from gamepart.context import Context
from gamepart.gui import Panel, Paragraph
from gamepart.gui.button import PrettyButton
from gamepart.gui.console import Console
from gamepart.gui.text import Text
from gamepart.gui.textinput import TextInput
from gamepart.noise import PerlinNoise
from gamepart.render import GfxRenderer

from scenes.base import MyBaseScene

from .generation import (
    NoiseRenderRequest,
    NoiseTileQueueItem,
    NoiseViewParameters,
    render_noise_argb32_streaming,
)

_SIDEBAR_W = 280
_PAN_STEP_WORLD = 32.0
_KEY_ZOOM_FACTOR = 2.0
_MAX_ZOOM = 1_048_576.0
_MIN_ZOOM = 1 / _MAX_ZOOM
_INITIAL_ZOOM = 1.0
_WHEEL_ZOOM_FACTOR = math.sqrt(2.0)
_INNER_MARGIN = 8
_ROW_GAP = 6
_LABEL_GAP = 8
_FIELD_ROW_H = 24
_SIDEBAR_BLOCKS_PAD = (_INNER_MARGIN, _INNER_MARGIN, _INNER_MARGIN, _INNER_MARGIN)
_ROW_LBL_VAL_PAD = (4, 8, 4, 8)
_ROW_SECTION_PAD = (6, 6, 6, 6)
_BUSY_INDICATOR_RADIUS = 10
_BUSY_INDICATOR_MARGIN = 14
_BUSY_INDICATOR_COLOR = (255, 230, 0, 255)
_NOISE_TILE_QUEUE_MAX = 512
_OPAQUE_BLACK_ARGB = (255 << 24) | 0


def _parse_float(text: str, default: float) -> float:
    text = text.strip()
    if not text:
        return default
    try:
        return float(text)
    except ValueError:
        return default


def _parse_int(text: str, default: int) -> int:
    text = text.strip()
    if not text:
        return default
    try:
        return int(text, base=10)
    except ValueError:
        return default


def _clamp_octaves(value: int) -> int:
    return max(1, min(32, value))


class NoiseDebugScene(MyBaseScene):
    def init(self) -> None:
        super().init()
        self._center_x = 0.0
        self._center_y = 0.0
        self._zoom = _INITIAL_ZOOM
        self._dragging = False
        self._noise_sprite: sdl2.ext.TextureSprite | None = None
        self._noise: PerlinNoise | None = None
        self._noise_display_params: NoiseViewParameters | None = None
        self._viewport_w = 0
        self._viewport_h = 0

        self._stop_worker_event = threading.Event()
        self._recalculate_event = threading.Event()
        self._worker_thread: threading.Thread | None = None
        self._noise_result_lock = threading.Lock()
        self._noise_worker_computing = False
        self._noise_tile_queue: queue.Queue[NoiseTileQueueItem] = queue.Queue(
            maxsize=_NOISE_TILE_QUEUE_MAX
        )
        self._noise_composite: array.array | None = None
        self._noise_composite_w = 0
        self._noise_composite_h = 0
        self._noise_composite_params: NoiseViewParameters | None = None
        self._noise_bake_center_x = 0.0
        self._noise_bake_center_y = 0.0
        self._noise_bake_zoom = 0.0
        self._noise_bake_tw = 0
        self._noise_bake_th = 0

        self._inp_seed: TextInput | None = None
        self._inp_octaves: TextInput | None = None
        self._inp_persistence: TextInput | None = None
        self._inp_lacunarity: TextInput | None = None
        self._inp_scale: TextInput | None = None
        self._inp_threshold_low: TextInput | None = None
        self._inp_threshold_high: TextInput | None = None
        self._inp_zoom: TextInput | None = None
        self._txt_center_val: Text | None = None
        self._para_bounds: Paragraph | None = None
        self._row_bounds: Panel | None = None
        self._lbl_bounds: Text | None = None
        self._tooltip_par: Paragraph | None = None
        self._sidebar: Panel | None = None

    def start(self, context: Context) -> None:
        super().start(context)
        self._viewport_w = max(1, self.game.width - _SIDEBAR_W)
        self._viewport_h = max(1, self.game.height)
        self.event_dispatcher.on(sdl2.SDL_MOUSEMOTION, self._on_mouse_motion)
        self.event_dispatcher.on(sdl2.SDL_MOUSEWHEEL, self._on_mouse_wheel)
        self.mouse_button_event.on_down(sdl2.SDL_BUTTON_LEFT, self._on_left_down)
        self.mouse_button_event.on_up(sdl2.SDL_BUTTON_LEFT, self._on_left_up)
        self.keyboard_event.on_up(
            sdl2.SDLK_ESCAPE, lambda e: self.game.queue_scene_switch("main_menu")
        )
        self.keyboard_event.on_down(sdl2.SDLK_LEFT, self._kbd_pan_left)
        self.keyboard_event.on_down(sdl2.SDLK_RIGHT, self._kbd_pan_right)
        self.keyboard_event.on_down(sdl2.SDLK_UP, self._kbd_pan_up)
        self.keyboard_event.on_down(sdl2.SDLK_DOWN, self._kbd_pan_down)
        self.keyboard_event.on_down(sdl2.SDLK_h, self._kbd_reset_origin)
        self.keyboard_event.on_down(sdl2.SDLK_n, self._kbd_reset_zoom)
        self.keyboard_event.on_down(sdl2.SDLK_EQUALS, self._kbd_zoom_in)
        self.keyboard_event.on_down(sdl2.SDLK_PLUS, self._kbd_zoom_in)
        self.keyboard_event.on_down(sdl2.SDLK_KP_PLUS, self._kbd_zoom_in)
        self.keyboard_event.on_down(sdl2.SDLK_MINUS, self._kbd_zoom_out)
        self.keyboard_event.on_down(sdl2.SDLK_KP_MINUS, self._kbd_zoom_out)
        self._build_sidebar()
        self._tooltip_par = Paragraph(
            x=0,
            y=0,
            text="",
            font="console",
            font_size=11,
            color=(255, 255, 255, 255),
            background_color=(20, 20, 28, 230),
            line_spacing=2,
            max_width=280,
        )
        self._tooltip_par.init_gui_system(self.gui)
        self._start_noise_worker()
        self._request_render()

    def stop(self) -> MyContext:
        self._stop_noise_worker()
        self._drain_noise_result_queue()
        self._noise_composite = None
        self._noise_composite_params = None
        self._noise_sprite = None
        self._noise = None
        self._noise_display_params = None
        self._sidebar = None
        self._inp_seed = None
        self._inp_octaves = None
        self._inp_persistence = None
        self._inp_lacunarity = None
        self._inp_scale = None
        self._inp_threshold_low = None
        self._inp_threshold_high = None
        self._inp_zoom = None
        self._txt_center_val = None
        self._para_bounds = None
        self._row_bounds = None
        self._lbl_bounds = None
        self._tooltip_par = None
        context = super().stop()
        assert isinstance(context, MyContext)
        return context

    def every_frame(self, renderer: GfxRenderer) -> None:
        vw = max(1, self.game.width - _SIDEBAR_W)
        vh = max(1, self.game.height)
        if vw != self._viewport_w or vh != self._viewport_h:
            self._viewport_w = vw
            self._viewport_h = vh
            self._request_render()

        self._poll_noise_result()
        self._update_readonly_labels()

        renderer.clear((0, 0, 0, 255))
        if self._noise_sprite is not None:
            sw, sh = self._noise_sprite.size
            if self._noise_should_preview_viewport(sw, sh, vw, vh):
                self._draw_noise_viewport_preview(renderer, sw, sh, vw, vh)
            else:
                renderer.copy(
                    self._noise_sprite,
                    (0, 0, sw, sh),
                    (_SIDEBAR_W, 0, vw, vh),
                )
        self.gui.draw()
        self._draw_render_busy_indicator(renderer)
        self._draw_tooltip(renderer)

    def _start_noise_worker(self) -> None:
        self._stop_worker_event.clear()
        self._recalculate_event.clear()
        self._worker_thread = threading.Thread(
            target=self._noise_worker_main,
            name="NoiseDebugRender",
            daemon=True,
        )
        self._worker_thread.start()

    def _stop_noise_worker(self) -> None:
        t = self._worker_thread
        if t is None or not t.is_alive():
            self._worker_thread = None
            return
        self._stop_worker_event.set()
        self._recalculate_event.set()
        t.join(timeout=15.0)
        self._worker_thread = None

    def _noise_worker_main(self) -> None:
        while True:
            if self._stop_worker_event.is_set():
                return
            if not self._recalculate_event.wait(timeout=0.25):
                continue
            while True:
                if self._stop_worker_event.is_set():
                    return
                self._recalculate_event.clear()
                with self._noise_result_lock:
                    self._noise_worker_computing = True
                try:
                    params = self._worker_parse_noise_view_parameters()
                    if params is None:
                        break
                    vw, vh = self._viewport_w, self._viewport_h
                    if vw < 1 or vh < 1:
                        break

                    def push_tile(
                        tx: int, ty: int, tw: int, th: int, data: bytes
                    ) -> None:
                        self._enqueue_noise_tile(
                            NoiseTileQueueItem(
                                params=params,
                                viewport_w=vw,
                                viewport_h=vh,
                                x=tx,
                                y=ty,
                                width=tw,
                                height=th,
                                pixels=data,
                            )
                        )

                    aborted = render_noise_argb32_streaming(
                        NoiseRenderRequest(params, vw, vh),
                        on_tile=push_tile,
                        should_abort=lambda: self._recalculate_event.is_set()
                        or self._stop_worker_event.is_set(),
                    )
                finally:
                    with self._noise_result_lock:
                        self._noise_worker_computing = False
                if self._stop_worker_event.is_set():
                    return
                if aborted or self._recalculate_event.is_set():
                    continue
                break

    def _worker_parse_noise_view_parameters(self) -> NoiseViewParameters | None:
        if (
            self._inp_seed is None
            or self._inp_octaves is None
            or self._inp_persistence is None
            or self._inp_lacunarity is None
            or self._inp_scale is None
            or self._inp_threshold_low is None
            or self._inp_threshold_high is None
        ):
            return None
        seed = _parse_int(self._inp_seed.text, 1)
        octaves = _clamp_octaves(_parse_int(self._inp_octaves.text, 1))
        persistence = _parse_float(self._inp_persistence.text, 1.0)
        lacunarity = _parse_float(self._inp_lacunarity.text, 1.0)
        scale = _parse_float(self._inp_scale.text, 1.0)
        low = _parse_float(self._inp_threshold_low.text, -0.5)
        high = _parse_float(self._inp_threshold_high.text, 0.5)
        return NoiseViewParameters(
            seed=seed,
            octaves=octaves,
            persistence=persistence,
            lacunarity=lacunarity,
            scale=scale,
            center_x=self._center_x,
            center_y=self._center_y,
            zoom=self._zoom,
            low_threshold=low,
            high_threshold=high,
        )

    def _request_render(self) -> None:
        self._viewport_w = max(1, self.game.width - _SIDEBAR_W)
        self._viewport_h = max(1, self.game.height)
        self._recalculate_event.set()

    def _enqueue_noise_tile(self, item: NoiseTileQueueItem) -> None:
        q = self._noise_tile_queue
        while True:
            try:
                q.put_nowait(item)
                return
            except queue.Full:
                try:
                    q.get_nowait()
                except queue.Empty:
                    pass

    def _drain_noise_result_queue(self) -> None:
        while True:
            try:
                self._noise_tile_queue.get_nowait()
            except queue.Empty:
                return

    def _poll_noise_result(self) -> None:
        last_merged: NoiseTileQueueItem | None = None
        while True:
            try:
                tile = self._noise_tile_queue.get_nowait()
            except queue.Empty:
                break
            if not self._noise_tile_matches_viewport(tile):
                continue
            if not self._merge_noise_tile(tile):
                continue
            last_merged = tile
        if last_merged is None:
            return
        if self._noise_composite is not None:
            self._apply_noise_pixels_to_sprite(
                self._noise_composite.tobytes(),
                self._noise_composite_w,
                self._noise_composite_h,
            )
        p = last_merged.params
        self._noise = PerlinNoise(
            seed=p.seed,
            octaves=p.octaves,
            persistence=p.persistence,
            lacunarity=p.lacunarity,
            scale=p.scale,
        )
        self._noise_display_params = p
        self._noise_bake_center_x = p.center_x
        self._noise_bake_center_y = p.center_y
        self._noise_bake_zoom = p.zoom
        self._noise_bake_tw = last_merged.viewport_w
        self._noise_bake_th = last_merged.viewport_h

    def _noise_tile_matches_viewport(self, tile: NoiseTileQueueItem) -> bool:
        return (
            tile.viewport_w == self._viewport_w and tile.viewport_h == self._viewport_h
        )

    def _merge_noise_tile(self, tile: NoiseTileQueueItem) -> bool:
        need = 4 * tile.width * tile.height
        if len(tile.pixels) != need:
            return False
        vw, vh = tile.viewport_w, tile.viewport_h
        prev = self._noise_composite
        pw, ph = self._noise_composite_w, self._noise_composite_h
        prev_p = self._noise_composite_params
        view_changed = prev is None or pw != vw or ph != vh or tile.params != prev_p
        if view_changed:
            if prev is not None and prev_p is not None:
                self._noise_composite = self._resample_composite_between_views(
                    prev,
                    pw,
                    ph,
                    prev_p,
                    vw,
                    vh,
                    tile.params,
                )
            else:
                self._noise_composite = array.array("I", [_OPAQUE_BLACK_ARGB]) * (
                    vw * vh
                )
            self._noise_composite_w = vw
            self._noise_composite_h = vh
            self._noise_composite_params = tile.params
        comp = self._noise_composite
        assert comp is not None
        src = array.array("I")
        src.frombytes(tile.pixels)
        self._blit_packed_tile_to_composite(
            comp,
            vw,
            src,
            tile.x,
            tile.y,
            tile.width,
            tile.height,
        )
        return True

    @staticmethod
    def _resample_composite_between_views(
        src: array.array,
        src_w: int,
        src_h: int,
        old_vp: NoiseViewParameters,
        dst_w: int,
        dst_h: int,
        new_vp: NoiseViewParameters,
    ) -> array.array:
        wpp_n = 1.0 / new_vp.zoom
        wpp_o = 1.0 / old_vp.zoom
        sx0_n = new_vp.center_x - 0.5 * dst_w * wpp_n
        sy0_n = new_vp.center_y - 0.5 * dst_h * wpp_n
        sx0_o = old_vp.center_x - 0.5 * src_w * wpp_o
        sy0_o = old_vp.center_y - 0.5 * src_h * wpp_o
        out = array.array("I", [_OPAQUE_BLACK_ARGB]) * (dst_w * dst_h)
        for dy in range(dst_h):
            base = dy * dst_w
            wy = sy0_n + dy * wpp_n
            for dx in range(dst_w):
                wx = sx0_n + dx * wpp_n
                col_f = (wx - sx0_o) / wpp_o
                row_f = (wy - sy0_o) / wpp_o
                ix = int(math.floor(col_f))
                iy = int(math.floor(row_f))
                if 0 <= ix < src_w and 0 <= iy < src_h:
                    out[base + dx] = src[iy * src_w + ix]
        return out

    @staticmethod
    def _blit_packed_tile_to_composite(
        dst: array.array,
        dst_w: int,
        src: array.array,
        dst_x: int,
        dst_y: int,
        tw: int,
        th: int,
    ) -> None:
        for row in range(th):
            sy = row * tw
            dy = (dst_y + row) * dst_w + dst_x
            dst[dy : dy + tw] = src[sy : sy + tw]

    def _apply_noise_pixels_to_sprite(self, pixels: bytes, w: int, h: int) -> None:
        surface_ptr = sdl2.SDL_CreateRGBSurfaceWithFormat(
            0, w, h, 32, sdl2.SDL_PIXELFORMAT_ARGB8888
        )
        if surface_ptr is None or not surface_ptr:
            return
        surf = surface_ptr.contents
        sdl2.SDL_LockSurface(surface_ptr)
        try:
            ctypes.memmove(surf.pixels, pixels, len(pixels))
        finally:
            sdl2.SDL_UnlockSurface(surface_ptr)
        self._noise_sprite = self.game.sprite_factory.from_surface(
            surface_ptr, free=True
        )

    def _noise_should_preview_viewport(
        self, tw: int, th: int, vw: int, vh: int
    ) -> bool:
        if not self._noise_render_busy_for_hud():
            return False
        if self._noise_bake_zoom <= 0.0:
            return False
        if tw != self._noise_bake_tw or th != self._noise_bake_th:
            return False
        if vw < 1 or vh < 1:
            return False
        return True

    def _draw_noise_viewport_preview(
        self, renderer: GfxRenderer, tw: int, th: int, vw: int, vh: int
    ) -> None:
        sprite = self._noise_sprite
        if sprite is None:
            return
        wpp_cur = 1.0 / self._zoom
        wpp_old = 1.0 / self._noise_bake_zoom
        start_x_cur = self._center_x - 0.5 * vw * wpp_cur
        start_y_cur = self._center_y - 0.5 * vh * wpp_cur
        start_x_old = self._noise_bake_center_x - 0.5 * tw * wpp_old
        start_y_old = self._noise_bake_center_y - 0.5 * th * wpp_old
        sx_f = (start_x_cur - start_x_old) / wpp_old
        sy_f = (start_y_cur - start_y_old) / wpp_old
        sw_f = vw * wpp_cur / wpp_old
        sh_f = vh * wpp_cur / wpp_old
        ix0 = max(0.0, sx_f)
        ix1 = min(float(tw), sx_f + sw_f)
        iy0 = max(0.0, sy_f)
        iy1 = min(float(th), sy_f + sh_f)
        if ix1 <= ix0 or iy1 <= iy0:
            return
        sx_i = max(0, min(tw - 1, int(math.floor(ix0))))
        sy_i = max(0, min(th - 1, int(math.floor(iy0))))
        ex_i = max(sx_i + 1, min(tw, int(math.ceil(ix1))))
        ey_i = max(sy_i + 1, min(th, int(math.ceil(iy1))))
        sw_i = ex_i - sx_i
        sh_i = ey_i - sy_i
        dst_x0f = vw * (float(sx_i) - sx_f) / sw_f
        dst_x1f = vw * (float(sx_i + sw_i) - sx_f) / sw_f
        dst_y0f = vh * (float(sy_i) - sy_f) / sh_f
        dst_y1f = vh * (float(sy_i + sh_i) - sy_f) / sh_f
        renderer.copy_texture(
            sprite.texture,
            (sx_i, sy_i, sw_i, sh_i),
            (
                float(_SIDEBAR_W) + dst_x0f,
                dst_y0f,
                dst_x1f - dst_x0f,
                dst_y1f - dst_y0f,
            ),
        )

    def _noise_render_busy_for_hud(self) -> bool:
        with self._noise_result_lock:
            computing = self._noise_worker_computing
        return computing or self._recalculate_event.is_set()

    def _draw_render_busy_indicator(self, renderer: GfxRenderer) -> None:
        if not self._noise_render_busy_for_hud():
            return
        r = _BUSY_INDICATOR_RADIUS
        m = _BUSY_INDICATOR_MARGIN
        cx = _SIDEBAR_W + m + r
        cy = self.game.height - m - r
        renderer.filled_circle([(cx, cy, r)], _BUSY_INDICATOR_COLOR)

    def _relayout_sidebar_rows(self) -> None:
        bar = self._sidebar
        if bar is None:
            return
        bar.rearrange_blocks(
            padding=_SIDEBAR_BLOCKS_PAD,
            margin=_ROW_GAP,
            flow="vertical",
        )
        bar.width = _SIDEBAR_W
        bar.height = self.game.height

    def _build_sidebar(self) -> None:
        panel = Panel(
            x=0,
            y=0,
            width=_SIDEBAR_W,
            height=self.game.height,
            background_color=(32, 32, 40, 255),
        )
        self.system.add_all(panel)
        self._sidebar = panel

        inner_w = _SIDEBAR_W - 2 * _INNER_MARGIN
        pad_lr = _ROW_LBL_VAL_PAD[3] + _ROW_LBL_VAL_PAD[1]

        def make_label(text: str) -> Text:
            return Text(
                x=0,
                y=0,
                text=text,
                font="console",
                font_size=12,
                color=(190, 190, 200, 255),
                background_color=None,
            )

        def add_labeled_value_row(
            label: str,
            *,
            value: TextInput | Text,
        ) -> TextInput | Text:
            row = Panel(width=inner_w, height=0, background_color=(44, 44, 52, 255))
            lbl = make_label(f"{label}:")
            row.add_child(lbl)
            row.add_child(value)
            panel.add_child(row)
            lbl.fit_to_text()
            vw = max(40, inner_w - pad_lr - lbl.width - _LABEL_GAP)
            value.width = vw
            if isinstance(value, TextInput):
                value.height = _FIELD_ROW_H
            else:
                value.max_width = vw
                value.fit_to_text()
            row.rearrange_blocks(
                padding=_ROW_LBL_VAL_PAD,
                margin=_LABEL_GAP,
                flow="horizontal",
            )
            return value

        def add_field_row(label: str, initial: str) -> TextInput:
            inp = TextInput(
                x=0,
                y=0,
                width=0,
                height=_FIELD_ROW_H,
                text=initial,
                font="console",
                font_size=12,
                color=(240, 240, 245, 255),
                background_color=(50, 50, 58, 255),
                on_submit=lambda _: self._apply_params(),
            )
            add_labeled_value_row(label, value=inp)
            return inp

        def add_readonly_text_row(label: str, placeholder: str) -> Text:
            val = Text(
                x=0,
                y=0,
                width=0,
                height=0,
                text=placeholder,
                font="console",
                font_size=12,
                color=(220, 225, 235, 255),
                background_color=None,
            )
            add_labeled_value_row(label, value=val)
            return val

        def add_readonly_paragraph_row(label: str) -> tuple[Panel, Text, Paragraph]:
            row = Panel(width=inner_w, height=0, background_color=(44, 44, 52, 255))
            lbl = make_label(f"{label}:")
            para = Paragraph(
                x=0,
                y=0,
                width=40,
                text="—",
                font="console",
                font_size=11,
                color=(220, 225, 235, 255),
                background_color=None,
                line_spacing=2,
            )
            row.add_child(lbl)
            row.add_child(para)
            panel.add_child(row)
            lbl.fit_to_text()
            para.width = max(40, inner_w - pad_lr - lbl.width - _LABEL_GAP)
            para.fit_to_text()
            row.rearrange_blocks(
                padding=_ROW_SECTION_PAD,
                margin=_LABEL_GAP,
                flow="horizontal",
            )
            return row, lbl, para

        def add_button_row(btn: PrettyButton) -> None:
            row = Panel(width=inner_w, height=0, background_color=(52, 52, 62, 255))
            row.add_child(btn)
            panel.add_child(row)
            inner_btn_w = inner_w - _ROW_SECTION_PAD[1] - _ROW_SECTION_PAD[3]
            btn.fit_to_text(padding=(6, 8, 6, 8))
            btn.width = inner_btn_w
            btn.text.x = btn.width // 2 - btn.text.width // 2
            row.rearrange_blocks(
                padding=_ROW_SECTION_PAD,
                margin=0,
                flow="vertical",
            )

        self._inp_seed = add_field_row("seed", "42")
        self._inp_octaves = add_field_row("octaves", "3")
        self._inp_persistence = add_field_row("persistence", "0.45")
        self._inp_lacunarity = add_field_row("lacunarity", "2.0")
        self._inp_scale = add_field_row("scale", "420.0")
        self._inp_threshold_low = add_field_row("low (red)", "-0.42")
        self._inp_threshold_high = add_field_row("high (green)", "0.42")

        self._inp_zoom = add_field_row("zoom", f"{self._zoom:g}")

        self._txt_center_val = add_readonly_text_row("center", "—")
        self._row_bounds, self._lbl_bounds, self._para_bounds = (
            add_readonly_paragraph_row("bounds")
        )

        apply_btn = PrettyButton(
            text=Text(
                x=10,
                y=6,
                text="Apply params",
                font="sans",
                font_size=14,
                color=(0, 0, 0, 255),
                background_color=None,
            ),
            hover_color=(255, 255, 255, 255),
            hover_background_color=(80, 120, 200, 255),
            width=inner_w,
            height=32,
            background_color=(200, 200, 210, 255),
            on_click=self._apply_params,
        )
        add_button_row(apply_btn)

        self._relayout_sidebar_rows()

    def _world_under_screen(self, sx: int, sy: int) -> tuple[float, float] | None:
        if sx < _SIDEBAR_W:
            return None
        vx = sx - _SIDEBAR_W
        if vx < 0 or vx >= self._viewport_w or sy < 0 or sy >= self._viewport_h:
            return None
        wpp = 1.0 / self._zoom
        half_w = 0.5 * self._viewport_w * wpp
        half_h = 0.5 * self._viewport_h * wpp
        start_x = self._center_x - half_w
        start_y = self._center_y - half_h
        return start_x + vx * wpp, start_y + sy * wpp

    def _viewport_nav_ok(self) -> bool:
        fo = self.gui.focused_object
        if fo is None:
            return True
        return not isinstance(fo, (TextInput, Console))

    def _sync_zoom_field(self) -> None:
        if self._inp_zoom is not None:
            self._inp_zoom.text = f"{self._zoom:g}"

    def _multiply_zoom_center(self, factor: float) -> None:
        z_old = self._zoom
        z_new = max(_MIN_ZOOM, min(_MAX_ZOOM, z_old * factor))
        if math.isclose(z_new, z_old, rel_tol=0.0, abs_tol=z_old * 1e-9):
            return
        self._zoom = z_new
        self._sync_zoom_field()
        self._request_render()

    def _kbd_pan_left(self, event: sdl2.SDL_Event) -> bool:
        if not self._viewport_nav_ok():
            return False
        self._center_x -= _PAN_STEP_WORLD / self._zoom
        self._request_render()
        return True

    def _kbd_pan_right(self, event: sdl2.SDL_Event) -> bool:
        if not self._viewport_nav_ok():
            return False
        self._center_x += _PAN_STEP_WORLD / self._zoom
        self._request_render()
        return True

    def _kbd_pan_up(self, event: sdl2.SDL_Event) -> bool:
        if not self._viewport_nav_ok():
            return False
        self._center_y -= _PAN_STEP_WORLD / self._zoom
        self._request_render()
        return True

    def _kbd_pan_down(self, event: sdl2.SDL_Event) -> bool:
        if not self._viewport_nav_ok():
            return False
        self._center_y += _PAN_STEP_WORLD / self._zoom
        self._request_render()
        return True

    def _kbd_reset_origin(self, event: sdl2.SDL_Event) -> bool:
        if not self._viewport_nav_ok():
            return False
        self._center_x = 0.0
        self._center_y = 0.0
        self._request_render()
        return True

    def _kbd_reset_zoom(self, event: sdl2.SDL_Event) -> bool:
        if not self._viewport_nav_ok():
            return False
        self._zoom = _INITIAL_ZOOM
        self._sync_zoom_field()
        self._request_render()
        return True

    def _kbd_zoom_in(self, event: sdl2.SDL_Event) -> bool:
        if not self._viewport_nav_ok():
            return False
        self._multiply_zoom_center(_KEY_ZOOM_FACTOR)
        return True

    def _kbd_zoom_out(self, event: sdl2.SDL_Event) -> bool:
        if not self._viewport_nav_ok():
            return False
        self._multiply_zoom_center(1.0 / _KEY_ZOOM_FACTOR)
        return True

    def _on_mouse_motion(self, event: sdl2.SDL_Event) -> bool | None:
        if not self._dragging:
            return None
        rel_x = float(event.motion.xrel)
        rel_y = float(event.motion.yrel)
        wpp = 1.0 / self._zoom
        self._center_x -= rel_x * wpp
        self._center_y -= rel_y * wpp
        self._request_render()
        return True

    def _on_left_down(self, event: sdl2.SDL_Event) -> bool | None:
        if event.button.x < _SIDEBAR_W:
            return None
        self._dragging = True
        return True

    def _on_left_up(self, event: sdl2.SDL_Event) -> bool | None:
        self._dragging = False
        return None

    def _on_mouse_wheel(self, event: sdl2.SDL_Event) -> bool | None:
        mx, my = int(self.game.mouse_state[0]), int(self.game.mouse_state[1])
        if mx < _SIDEBAR_W:
            return None
        vx = mx - _SIDEBAR_W
        vw, vh = self._viewport_w, self._viewport_h
        if vx < 0 or vx >= vw or my < 0 or my >= vh:
            return None
        wheel = event.wheel
        dy = float(getattr(wheel, "preciseY", 0.0))
        if abs(dy) < 1e-6:
            dy = float(wheel.y)
        if abs(dy) < 1e-6:
            return None
        z_old = self._zoom
        z_new = max(_MIN_ZOOM, min(_MAX_ZOOM, z_old * (_WHEEL_ZOOM_FACTOR**dy)))
        if math.isclose(z_new, z_old, rel_tol=0.0, abs_tol=z_old * 1e-9):
            return True
        wpp_old = 1.0 / z_old
        wx = self._center_x + (vx - 0.5 * vw) * wpp_old
        wy = self._center_y + (my - 0.5 * vh) * wpp_old
        wpp_new = 1.0 / z_new
        self._center_x = wx - (vx - 0.5 * vw) * wpp_new
        self._center_y = wy - (my - 0.5 * vh) * wpp_new
        self._zoom = z_new
        self._sync_zoom_field()
        self._request_render()
        return True

    def _apply_params(self) -> None:
        assert self._inp_zoom is not None
        assert self._inp_octaves is not None
        z = _parse_float(self._inp_zoom.text, self._zoom)
        self._zoom = max(_MIN_ZOOM, z)
        self._sync_zoom_field()
        octaves = _clamp_octaves(_parse_int(self._inp_octaves.text, 3))
        self._inp_octaves.text = str(octaves)
        self._request_render()

    def _update_readonly_labels(self) -> None:
        if (
            self._txt_center_val is None
            or self._para_bounds is None
            or self._row_bounds is None
            or self._lbl_bounds is None
        ):
            return
        half_w = 0.5 * self._viewport_w / self._zoom
        half_h = 0.5 * self._viewport_h / self._zoom
        sx0 = self._center_x - half_w
        sx1 = self._center_x + half_w
        sy0 = self._center_y - half_h
        sy1 = self._center_y + half_h
        self._txt_center_val.text = f"({self._center_x:.2f}, {self._center_y:.2f})"
        self._para_bounds.text = (
            f"x: [{sx0:.2f}, {sx1:.2f}]\n" f"y: [{sy0:.2f}, {sy1:.2f}]"
        )
        self._para_bounds.fit_to_text()
        self._row_bounds.rearrange_blocks(
            padding=_ROW_SECTION_PAD,
            margin=_LABEL_GAP,
            flow="horizontal",
        )
        self._relayout_sidebar_rows()

    def _draw_tooltip(self, renderer: GfxRenderer) -> None:
        par = self._tooltip_par
        if par is None:
            return
        mx, my = int(self.game.mouse_state[0]), int(self.game.mouse_state[1])
        world = self._world_under_screen(mx, my)
        if world is None or self._noise is None:
            return
        wx, wy = world
        value = self._noise.get2d(wx, wy)
        par.text = f"{value:.6f}\n ({wx:.5f}, {wy:.5f})"
        par.fit_to_text()
        tw, th = par.width, par.height
        tx = min(mx + 14, self.game.width - tw - 8)
        ty = min(my + 14, self.game.height - th - 8)
        if tx < 8:
            tx = 8
        if ty < 8:
            ty = 8
        par.x = tx
        par.y = ty
        par.draw()
