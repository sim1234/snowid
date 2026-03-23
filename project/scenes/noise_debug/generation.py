from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from gamepart.noise import PerlinNoise
from gamepart.noise_numba import fill_noise_rect_argb32

NOISE_RENDER_TILE_GRID = 4

RenderAbortCheck = Callable[[], bool]
TilePush = Callable[[int, int, int, int, bytes], None]


@dataclass(frozen=True, slots=True)
class NoiseViewParameters:
    seed: int
    octaves: int
    persistence: float
    lacunarity: float
    scale: float
    center_x: float
    center_y: float
    zoom: float
    low_threshold: float
    high_threshold: float


@dataclass(frozen=True, slots=True)
class NoiseRenderRequest:
    params: NoiseViewParameters
    viewport_w: int
    viewport_h: int


@dataclass(frozen=True, slots=True)
class NoiseTileQueueItem:
    params: NoiseViewParameters
    viewport_w: int
    viewport_h: int
    x: int
    y: int
    width: int
    height: int
    pixels: bytes


def _split_range(length: int, parts: int) -> list[tuple[int, int]]:
    edges = [(i * length) // parts for i in range(parts + 1)]
    return list(zip(edges[:-1], edges[1:], strict=True))


def _argb_pixel(r: int, g: int, b: int) -> int:
    return (255 << 24) | (r << 16) | (g << 8) | b


def render_noise_argb32_streaming(
    req: NoiseRenderRequest,
    *,
    on_tile: TilePush,
    should_abort: RenderAbortCheck | None = None,
    grid: int = NOISE_RENDER_TILE_GRID,
) -> bool:
    """Renders tiles in order, pushing each to ``on_tile`` when done.

    Returns True if aborted before all tiles were finished, else False.
    """
    p = req.params
    vw, vh = req.viewport_w, req.viewport_h
    parts = max(1, grid)
    abort = should_abort or (lambda: False)
    noise = PerlinNoise(
        seed=p.seed,
        octaves=p.octaves,
        persistence=p.persistence,
        lacunarity=p.lacunarity,
        scale=p.scale,
    )
    perm = noise.permutation_uint8
    wpp = 1.0 / p.zoom
    half_w = 0.5 * vw * wpp
    half_h = 0.5 * vh * wpp
    start_x = p.center_x - half_w
    start_y = p.center_y - half_h
    low = p.low_threshold
    high = p.high_threshold
    red_px = _argb_pixel(255, 0, 0)
    green_px = _argb_pixel(0, 255, 0)
    buf = np.zeros(vw * vh, dtype=np.uint32)
    col_ranges = _split_range(vw, parts)
    row_ranges = _split_range(vh, parts)
    for r0, r1 in row_ranges:
        for c0, c1 in col_ranges:
            if abort():
                return True
            if r0 >= r1 or c0 >= c1:
                continue
            tw, th = c1 - c0, r1 - r0
            fill_noise_rect_argb32(
                perm,
                buf,
                vw,
                c0,
                c1,
                r0,
                r1,
                start_x,
                start_y,
                wpp,
                p.scale,
                p.octaves,
                p.persistence,
                p.lacunarity,
                low,
                high,
                red_px,
                green_px,
            )
            tile_blob = b"".join(
                buf[row * vw + c0 : row * vw + c1].tobytes() for row in range(r0, r1)
            )
            on_tile(c0, r0, tw, th, tile_blob)
    return False
