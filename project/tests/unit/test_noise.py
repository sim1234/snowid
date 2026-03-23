"""Tests for the Perlin noise generator."""

import numpy as np
import pytest
from gamepart.noise import PerlinNoise
from gamepart.noise_numba import fbm2d, fill_noise_rect_argb32


def _argb_from_noise_value(
    value: float,
    low: float,
    high: float,
    red_px: int,
    green_px: int,
) -> int:
    if value < low:
        return red_px
    if value > high:
        return green_px
    g = int(max(0.0, min(255.0, (value + 1.0) * 127.5)))
    return (255 << 24) | (g << 16) | (g << 8) | g


def _expected_argb_at_pixel(
    perm: np.ndarray,
    row: int,
    col: int,
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
) -> int:
    wx = start_x + col * wpp
    wy = start_y + row * wpp
    inv_s = 1.0 / scale if scale else 1.0
    sx = wx * inv_s if scale else wx
    sy = wy * inv_s if scale else wy
    value = float(fbm2d(perm, sx, sy, octaves, persistence, lacunarity))
    return _argb_from_noise_value(value, low, high, red_px, green_px)


class TestPerlinNoiseBasic:
    """Basic functionality tests."""

    def test_instantiation_with_defaults(self) -> None:
        noise = PerlinNoise()
        assert noise.seed == 0
        assert noise.octaves == 1
        assert noise.persistence == 0.5
        assert noise.lacunarity == 2.0
        assert noise.scale == 1.0

    def test_instantiation_with_custom_params(self) -> None:
        noise = PerlinNoise(
            seed=42,
            octaves=4,
            persistence=0.6,
            lacunarity=2.5,
            scale=10.0,
        )
        assert noise.seed == 42
        assert noise.octaves == 4
        assert noise.persistence == 0.6
        assert noise.lacunarity == 2.5
        assert noise.scale == 10.0


class TestPerlinNoiseDeterminism:
    """Tests for deterministic output."""

    def test_same_seed_same_output_1d(self) -> None:
        noise1 = PerlinNoise(seed=42)
        noise2 = PerlinNoise(seed=42)
        for x in [0.0, 0.5, 1.0, 2.5, -3.7]:
            assert noise1.get1d(x) == noise2.get1d(x)

    def test_same_seed_same_output_2d(self) -> None:
        noise1 = PerlinNoise(seed=42)
        noise2 = PerlinNoise(seed=42)
        for x, y in [(0.0, 0.0), (0.5, 0.5), (1.0, 2.0), (-1.5, 3.7)]:
            assert noise1.get2d(x, y) == noise2.get2d(x, y)

    def test_same_seed_same_output_3d(self) -> None:
        noise1 = PerlinNoise(seed=42)
        noise2 = PerlinNoise(seed=42)
        for x, y, z in [(0.0, 0.0, 0.0), (0.5, 0.5, 0.5), (1.0, 2.0, 3.0)]:
            assert noise1.get3d(x, y, z) == noise2.get3d(x, y, z)

    def test_different_seed_different_output(self) -> None:
        noise1 = PerlinNoise(seed=42)
        noise2 = PerlinNoise(seed=43)
        results_differ = False
        for x in [0.5, 1.5, 2.5]:
            if noise1.get1d(x) != noise2.get1d(x):
                results_differ = True
                break
        assert results_differ


class TestPerlinNoiseRange:
    """Tests for output range."""

    def test_1d_output_in_range(self) -> None:
        noise = PerlinNoise(seed=42)
        for x in range(-100, 100):
            value = noise.get1d(x * 0.1)
            assert -1.0 <= value <= 1.0, f"1D value {value} out of range at x={x * 0.1}"

    def test_2d_output_in_range(self) -> None:
        noise = PerlinNoise(seed=42)
        for x in range(-20, 20):
            for y in range(-20, 20):
                value = noise.get2d(x * 0.1, y * 0.1)
                assert -1.0 <= value <= 1.0, f"2D value {value} out of range"

    def test_3d_output_in_range(self) -> None:
        noise = PerlinNoise(seed=42)
        for x in range(-10, 10):
            for y in range(-10, 10):
                for z in range(-10, 10):
                    value = noise.get3d(x * 0.1, y * 0.1, z * 0.1)
                    assert -1.0 <= value <= 1.0, f"3D value {value} out of range"

    def test_output_in_range_with_octaves(self) -> None:
        noise = PerlinNoise(seed=42, octaves=6, persistence=0.5)
        for x in range(-50, 50):
            value = noise.get1d(x * 0.1)
            assert -1.0 <= value <= 1.0, f"fBm value {value} out of range"


class TestPerlinNoiseGetDispatch:
    """Tests for the get() method dispatch."""

    def test_get_1d_dispatch(self) -> None:
        noise = PerlinNoise(seed=42)
        assert noise.get(1.5) == noise.get1d(1.5)

    def test_get_2d_dispatch(self) -> None:
        noise = PerlinNoise(seed=42)
        assert noise.get(1.5, 2.5) == noise.get2d(1.5, 2.5)

    def test_get_3d_dispatch(self) -> None:
        noise = PerlinNoise(seed=42)
        assert noise.get(1.5, 2.5, 3.5) == noise.get3d(1.5, 2.5, 3.5)

    def test_get_invalid_dimensions_zero(self) -> None:
        noise = PerlinNoise(seed=42)
        with pytest.raises(ValueError, match="Expected 1, 2, or 3 coordinates"):
            noise.get()

    def test_get_invalid_dimensions_four(self) -> None:
        noise = PerlinNoise(seed=42)
        with pytest.raises(ValueError, match="Expected 1, 2, or 3 coordinates"):
            noise.get(1.0, 2.0, 3.0, 4.0)


class TestPerlinNoiseOctaves:
    """Tests for octave/fBm functionality."""

    def test_single_octave_equals_base_noise(self) -> None:
        noise = PerlinNoise(seed=42, octaves=1, scale=1.0)
        value = noise.get1d(1.5)
        assert isinstance(value, float)

    def test_more_octaves_adds_detail(self) -> None:
        noise_1_octave = PerlinNoise(seed=42, octaves=1)
        noise_4_octaves = PerlinNoise(seed=42, octaves=4)

        values_1 = [noise_1_octave.get1d(x * 0.01) for x in range(100)]
        values_4 = [noise_4_octaves.get1d(x * 0.01) for x in range(100)]

        assert values_1 != values_4

    def test_octaves_parameter_affects_output(self) -> None:
        noise1 = PerlinNoise(seed=42, octaves=1)
        noise2 = PerlinNoise(seed=42, octaves=4)
        assert noise1.get2d(0.7, 1.3) != noise2.get2d(0.7, 1.3)

    def test_persistence_affects_output(self) -> None:
        noise1 = PerlinNoise(seed=42, octaves=4, persistence=0.3)
        noise2 = PerlinNoise(seed=42, octaves=4, persistence=0.7)
        assert noise1.get2d(0.7, 1.3) != noise2.get2d(0.7, 1.3)

    def test_lacunarity_affects_output(self) -> None:
        noise1 = PerlinNoise(seed=42, octaves=4, lacunarity=1.5)
        noise2 = PerlinNoise(seed=42, octaves=4, lacunarity=3.0)
        assert noise1.get2d(1.5, 2.5) != noise2.get2d(1.5, 2.5)


class TestPerlinNoiseScale:
    """Tests for scale parameter."""

    def test_scale_affects_frequency(self) -> None:
        noise_small_scale = PerlinNoise(seed=42, scale=0.5)
        noise_large_scale = PerlinNoise(seed=42, scale=2.0)

        values_small = [noise_small_scale.get1d(x * 0.1) for x in range(20)]
        values_large = [noise_large_scale.get1d(x * 0.1) for x in range(20)]

        assert values_small != values_large

    def test_scale_relationship(self) -> None:
        noise = PerlinNoise(seed=42, scale=2.0)
        noise_base = PerlinNoise(seed=42, scale=1.0)
        assert noise.get1d(2.0) == noise_base.get1d(1.0)


class TestPerlinNoiseContinuity:
    """Tests for noise continuity."""

    def test_1d_continuity(self) -> None:
        noise = PerlinNoise(seed=42)
        for x in range(100):
            x_float = x * 0.01
            v1 = noise.get1d(x_float)
            v2 = noise.get1d(x_float + 0.001)
            assert abs(v1 - v2) < 0.1, "1D noise should be continuous"

    def test_2d_continuity(self) -> None:
        noise = PerlinNoise(seed=42)
        for x in range(20):
            for y in range(20):
                x_float = x * 0.1
                y_float = y * 0.1
                v1 = noise.get2d(x_float, y_float)
                v2 = noise.get2d(x_float + 0.01, y_float + 0.01)
                assert abs(v1 - v2) < 0.2, "2D noise should be continuous"

    def test_3d_continuity(self) -> None:
        noise = PerlinNoise(seed=42)
        for x in range(10):
            for y in range(10):
                for z in range(10):
                    x_float = x * 0.1
                    y_float = y * 0.1
                    z_float = z * 0.1
                    v1 = noise.get3d(x_float, y_float, z_float)
                    v2 = noise.get3d(x_float + 0.01, y_float + 0.01, z_float + 0.01)
                    assert abs(v1 - v2) < 0.3, "3D noise should be continuous"


class TestFillNoiseRectArgb32:
    def test_fill_noise_rect_argb32_matches_fbm2d(self) -> None:
        scale = 12.5
        octaves = 3
        persistence = 0.55
        lacunarity = 2.1
        noise = PerlinNoise(
            seed=17,
            octaves=octaves,
            persistence=persistence,
            lacunarity=lacunarity,
            scale=scale,
        )
        perm = noise.permutation_uint8
        vw, vh = 23, 19
        c0, c1 = 3, 18
        r0, r1 = 2, 15
        start_x = -0.7
        start_y = 0.4
        wpp = 0.055
        low, high = -0.18, 0.22
        red_px = (255 << 24) | (255 << 16)
        green_px = (255 << 24) | (255 << 8)
        buf = np.zeros(vw * vh, dtype=np.uint32)
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
            scale,
            octaves,
            persistence,
            lacunarity,
            low,
            high,
            red_px,
            green_px,
        )
        for row in range(r0, r1):
            for col in range(c0, c1):
                expected = _expected_argb_at_pixel(
                    perm,
                    row,
                    col,
                    start_x,
                    start_y,
                    wpp,
                    scale,
                    octaves,
                    persistence,
                    lacunarity,
                    low,
                    high,
                    red_px,
                    green_px,
                )
                assert int(buf[row * vw + col]) == expected

    def test_fill_noise_rect_argb32_matches_fbm2d_scale_zero(self) -> None:
        octaves = 2
        persistence = 0.5
        lacunarity = 2.0
        noise = PerlinNoise(
            seed=99,
            octaves=octaves,
            persistence=persistence,
            lacunarity=lacunarity,
            scale=0.0,
        )
        perm = noise.permutation_uint8
        vw, vh = 11, 9
        c0, c1 = 0, vw
        r0, r1 = 0, vh
        start_x = 0.1
        start_y = -0.2
        wpp = 0.08
        low, high = -0.5, 0.5
        red_px = (255 << 24) | (255 << 16) | (10 << 8) | 10
        green_px = (255 << 24) | (10 << 16) | (255 << 8) | 10
        buf = np.zeros(vw * vh, dtype=np.uint32)
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
            0.0,
            octaves,
            persistence,
            lacunarity,
            low,
            high,
            red_px,
            green_px,
        )
        for row in range(r0, r1):
            for col in range(c0, c1):
                expected = _expected_argb_at_pixel(
                    perm,
                    row,
                    col,
                    start_x,
                    start_y,
                    wpp,
                    0.0,
                    octaves,
                    persistence,
                    lacunarity,
                    low,
                    high,
                    red_px,
                    green_px,
                )
                assert int(buf[row * vw + col]) == expected
