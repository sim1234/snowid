"""Numba-accelerated Perlin noise kernels (same math as ``noise.PerlinNoise``)."""

from __future__ import annotations

import math

import numpy as np
from numba import njit, prange


@njit(cache=True)
def _fade(t: float) -> float:
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


@njit(cache=True)
def _lerp(a: float, b: float, t: float) -> float:
    return a + t * (b - a)


@njit(cache=True)
def _grad1d(h: int, x: float) -> float:
    return x if (h & 1) else -x


@njit(cache=True)
def _grad2d(h: int, x: float, y: float) -> float:
    hh = h & 7
    u = x if hh < 4 else y
    v = y if hh < 4 else x
    return (u if (hh & 1) == 0 else -u) + (v if (hh & 2) == 0 else -v)


@njit(cache=True)
def _grad3d(h: int, x: float, y: float, z: float) -> float:
    hh = h & 15
    u = x if hh < 8 else y
    if hh < 4:
        v = y
    elif hh == 12 or hh == 14:
        v = x
    else:
        v = z
    return (u if (hh & 1) == 0 else -u) + (v if (hh & 2) == 0 else -v)


@njit(cache=True)
def noise1d_raw(perm: np.ndarray, x: float) -> float:
    xi = int(math.floor(x)) & 255
    xf = x - math.floor(x)
    u = _fade(xf)
    a = perm[(0 + xi) & 255]
    b = perm[(0 + xi + 1) & 255]
    return _lerp(_grad1d(a, xf), _grad1d(b, xf - 1.0), u)


@njit(cache=True)
def noise2d_raw(perm: np.ndarray, x: float, y: float) -> float:
    xi = int(math.floor(x)) & 255
    yi = int(math.floor(y)) & 255
    xf = x - math.floor(x)
    yf = y - math.floor(y)
    u = _fade(xf)
    v = _fade(yf)
    aa = perm[(perm[(0 + xi) & 255] + yi) & 255]
    ab = perm[(perm[(0 + xi) & 255] + yi + 1) & 255]
    ba = perm[(perm[(0 + xi + 1) & 255] + yi) & 255]
    bb = perm[(perm[(0 + xi + 1) & 255] + yi + 1) & 255]
    x1 = _lerp(_grad2d(aa, xf, yf), _grad2d(ba, xf - 1.0, yf), u)
    x2 = _lerp(_grad2d(ab, xf, yf - 1.0), _grad2d(bb, xf - 1.0, yf - 1.0), u)
    return _lerp(x1, x2, v)


@njit(cache=True)
def noise3d_raw(perm: np.ndarray, x: float, y: float, z: float) -> float:
    xi = int(math.floor(x)) & 255
    yi = int(math.floor(y)) & 255
    zi = int(math.floor(z)) & 255
    xf = x - math.floor(x)
    yf = y - math.floor(y)
    zf = z - math.floor(z)
    u = _fade(xf)
    v = _fade(yf)
    w = _fade(zf)
    aaa = perm[(perm[(perm[(0 + xi) & 255] + yi) & 255] + zi) & 255]
    aba = perm[(perm[(perm[(0 + xi) & 255] + yi + 1) & 255] + zi) & 255]
    aab = perm[(perm[(perm[(0 + xi) & 255] + yi) & 255] + zi + 1) & 255]
    abb = perm[(perm[(perm[(0 + xi) & 255] + yi + 1) & 255] + zi + 1) & 255]
    baa = perm[(perm[(perm[(0 + xi + 1) & 255] + yi) & 255] + zi) & 255]
    bba = perm[(perm[(perm[(0 + xi + 1) & 255] + yi + 1) & 255] + zi) & 255]
    bab = perm[(perm[(perm[(0 + xi + 1) & 255] + yi) & 255] + zi + 1) & 255]
    bbb = perm[(perm[(perm[(0 + xi + 1) & 255] + yi + 1) & 255] + zi + 1) & 255]
    x1 = _lerp(_grad3d(aaa, xf, yf, zf), _grad3d(baa, xf - 1.0, yf, zf), u)
    x2 = _lerp(_grad3d(aba, xf, yf - 1.0, zf), _grad3d(bba, xf - 1.0, yf - 1.0, zf), u)
    y1 = _lerp(x1, x2, v)
    x1 = _lerp(_grad3d(aab, xf, yf, zf - 1.0), _grad3d(bab, xf - 1.0, yf, zf - 1.0), u)
    x2 = _lerp(
        _grad3d(abb, xf, yf - 1.0, zf - 1.0),
        _grad3d(bbb, xf - 1.0, yf - 1.0, zf - 1.0),
        u,
    )
    y2 = _lerp(x1, x2, v)
    return _lerp(y1, y2, w)


@njit(cache=True)
def fbm1d(
    perm: np.ndarray,
    x: float,
    octaves: int,
    persistence: float,
    lacunarity: float,
) -> float:
    total = 0.0
    amplitude = 1.0
    frequency = 1.0
    max_value = 0.0
    for _ in range(octaves):
        total += amplitude * noise1d_raw(perm, x * frequency)
        max_value += amplitude
        amplitude *= persistence
        frequency *= lacunarity
    return total / max_value if max_value else 0.0


@njit(cache=True)
def fbm2d(
    perm: np.ndarray,
    x: float,
    y: float,
    octaves: int,
    persistence: float,
    lacunarity: float,
) -> float:
    total = 0.0
    amplitude = 1.0
    frequency = 1.0
    max_value = 0.0
    for _ in range(octaves):
        total += amplitude * noise2d_raw(perm, x * frequency, y * frequency)
        max_value += amplitude
        amplitude *= persistence
        frequency *= lacunarity
    return total / max_value if max_value else 0.0


@njit(cache=True)
def fbm3d(
    perm: np.ndarray,
    x: float,
    y: float,
    z: float,
    octaves: int,
    persistence: float,
    lacunarity: float,
) -> float:
    total = 0.0
    amplitude = 1.0
    frequency = 1.0
    max_value = 0.0
    for _ in range(octaves):
        total += amplitude * noise3d_raw(
            perm,
            x * frequency,
            y * frequency,
            z * frequency,
        )
        max_value += amplitude
        amplitude *= persistence
        frequency *= lacunarity
    return total / max_value if max_value else 0.0


@njit(cache=True, parallel=True)
def fill_noise_rect_argb32(
    perm: np.ndarray,
    out: np.ndarray,
    vw: int,
    c0: int,
    c1: int,
    r0: int,
    r1: int,
    start_x: float,
    start_y: float,
    wpp: float,
    scale: float,
    octaves: int,
    persistence: float,
    lacunarity: float,
    low: float,
    high: float,
    red_px: int,
    green_px: int,
) -> None:
    inv_s = 1.0 / scale if scale else 1.0
    for row in prange(r0, r1):
        wy = start_y + row * wpp
        sy = wy * inv_s if scale else wy
        base = row * vw
        for col in range(c0, c1):
            wx = start_x + col * wpp
            sx = wx * inv_s if scale else wx
            value = fbm2d(perm, sx, sy, octaves, persistence, lacunarity)
            if value < low:
                out[base + col] = np.uint32(red_px)
            elif value > high:
                out[base + col] = np.uint32(green_px)
            else:
                g = int(max(0.0, min(255.0, (value + 1.0) * 127.5)))
                out[base + col] = np.uint32((255 << 24) | (g << 16) | (g << 8) | g)
