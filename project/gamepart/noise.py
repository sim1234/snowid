"""Perlin noise generator with configurable dimensions and fractal support."""

import math
import random
from functools import lru_cache


class PerlinNoise:
    """Configurable Perlin noise generator with LRU caching.

    Perlin noise produces smooth, continuous pseudo-random values that are
    useful for procedural generation of textures, terrain, animations, and
    other natural-looking patterns. Unlike pure random noise, Perlin noise
    has spatial coherence - nearby coordinates produce similar values.

    This implementation supports fractal Brownian motion (fBm), which layers
    multiple octaves of noise at different frequencies to create more complex,
    natural-looking patterns with both large-scale features and fine detail.

    Configuration Guide:

        seed: Controls the randomness. Same seed always produces identical
            noise patterns, allowing reproducible procedural generation.

        octaves: Number of noise layers to combine (1-8 typical).
            - 1 octave: Smooth, simple noise with only large-scale features
            - 4-6 octaves: Natural-looking noise with mixed detail levels
            - More octaves = more fine detail, but diminishing returns past 8
            Each octave adds noise at higher frequency and lower amplitude.

        persistence: How much each octave contributes relative to the previous
            (0.0-1.0, typically 0.5). Controls the "roughness" of the result.
            - Low (0.3): Smooth, dominated by large-scale features
            - Medium (0.5): Balanced mix of scales (most natural-looking)
            - High (0.7): Rough, with prominent fine details
            Mathematically: amplitude of octave n = persistence^n

        lacunarity: Frequency multiplier between octaves (typically 2.0).
            Controls how quickly detail scale decreases.
            - 2.0: Each octave is twice the frequency (standard)
            - Higher: Bigger jumps between detail levels
            - Lower: More gradual frequency progression
            Mathematically: frequency of octave n = lacunarity^n

        scale: Overall coordinate scaling factor.
            - Larger scale = more "zoomed in", slower variation
            - Smaller scale = more "zoomed out", faster variation
            Coordinates are divided by scale before noise computation.

        cache_size: LRU cache size for memoizing noise computations.
            - 0: Disable caching entirely
            - None: Unlimited cache size
            - Positive int: Maximum cached values per dimension
            Useful when sampling the same coordinates repeatedly.

    Example:
        # Terrain-like noise with natural appearance
        terrain = PerlinNoise(seed=42, octaves=6, persistence=0.5, scale=100.0)
        height = terrain.get2d(x, y)  # Returns value in [-1, 1]

        # Smooth cloud-like noise
        clouds = PerlinNoise(seed=123, octaves=4, persistence=0.4, scale=50.0)

        # Rough rocky texture
        rocks = PerlinNoise(seed=456, octaves=8, persistence=0.65, scale=10.0)
    """

    def __init__(
        self,
        seed: int = 0,
        octaves: int = 1,
        persistence: float = 0.5,
        lacunarity: float = 2.0,
        scale: float = 1.0,
        cache_size: int | None = 1024,
    ) -> None:
        """Initialize a Perlin noise generator.

        Args:
            seed: Random seed for reproducible noise patterns.
            octaves: Number of noise layers to combine (more = more detail).
            persistence: Amplitude multiplier per octave (0.0-1.0, lower = smoother).
            lacunarity: Frequency multiplier per octave (typically 2.0).
            scale: Coordinate divisor (larger = slower variation).
            cache_size: LRU cache size (0 = disabled, None = unlimited).
        """
        self.seed = seed
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
        self.scale = scale
        self.cache_size = cache_size

        self._permutation = self._generate_permutation(seed)
        self._setup_cached_methods(cache_size)

    def _generate_permutation(self, seed: int) -> list[int]:
        """Generate a permutation table seeded with the given seed."""
        rng = random.Random(seed)
        perm = list(range(256))
        rng.shuffle(perm)
        return perm + perm  # Double for overflow handling

    def _setup_cached_methods(self, cache_size: int | None) -> None:
        """Set up LRU-cached internal noise methods."""
        if cache_size == 0:
            self._noise1d_cached = self._noise1d_raw
            self._noise2d_cached = self._noise2d_raw
            self._noise3d_cached = self._noise3d_raw
        else:
            self._noise1d_cached = lru_cache(maxsize=cache_size)(self._noise1d_raw)
            self._noise2d_cached = lru_cache(maxsize=cache_size)(self._noise2d_raw)
            self._noise3d_cached = lru_cache(maxsize=cache_size)(self._noise3d_raw)

    @staticmethod
    def _fade(t: float) -> float:
        """Smoothstep fade function: 6t^5 - 15t^4 + 10t^3"""
        return t * t * t * (t * (t * 6 - 15) + 10)

    @staticmethod
    def _lerp(a: float, b: float, t: float) -> float:
        """Linear interpolation between a and b."""
        return a + t * (b - a)

    def _hash(self, *indices: int) -> int:
        """Hash function using permutation table."""
        result = 0
        for idx in indices:
            result = self._permutation[(result + idx) & 255]
        return result

    def _grad1d(self, hash_val: int, x: float) -> float:
        """1D gradient function."""
        return x if (hash_val & 1) else -x

    def _grad2d(self, hash_val: int, x: float, y: float) -> float:
        """2D gradient function using 8 gradient directions."""
        h = hash_val & 7
        u = x if h < 4 else y
        v = y if h < 4 else x
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

    def _grad3d(self, hash_val: int, x: float, y: float, z: float) -> float:
        """3D gradient function using 12 gradient directions."""
        h = hash_val & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h in (12, 14) else z)
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

    def _noise1d_raw(self, x: float) -> float:
        """Raw 1D Perlin noise computation."""
        xi = int(math.floor(x)) & 255
        xf = x - math.floor(x)

        u = self._fade(xf)

        a = self._hash(xi)
        b = self._hash(xi + 1)

        return self._lerp(self._grad1d(a, xf), self._grad1d(b, xf - 1), u)

    def _noise2d_raw(self, x: float, y: float) -> float:
        """Raw 2D Perlin noise computation."""
        xi = int(math.floor(x)) & 255
        yi = int(math.floor(y)) & 255
        xf = x - math.floor(x)
        yf = y - math.floor(y)

        u = self._fade(xf)
        v = self._fade(yf)

        aa = self._hash(xi, yi)
        ab = self._hash(xi, yi + 1)
        ba = self._hash(xi + 1, yi)
        bb = self._hash(xi + 1, yi + 1)

        x1 = self._lerp(self._grad2d(aa, xf, yf), self._grad2d(ba, xf - 1, yf), u)
        x2 = self._lerp(
            self._grad2d(ab, xf, yf - 1), self._grad2d(bb, xf - 1, yf - 1), u
        )

        return self._lerp(x1, x2, v)

    def _noise3d_raw(self, x: float, y: float, z: float) -> float:
        """Raw 3D Perlin noise computation."""
        xi = int(math.floor(x)) & 255
        yi = int(math.floor(y)) & 255
        zi = int(math.floor(z)) & 255
        xf = x - math.floor(x)
        yf = y - math.floor(y)
        zf = z - math.floor(z)

        u = self._fade(xf)
        v = self._fade(yf)
        w = self._fade(zf)

        aaa = self._hash(xi, yi, zi)
        aba = self._hash(xi, yi + 1, zi)
        aab = self._hash(xi, yi, zi + 1)
        abb = self._hash(xi, yi + 1, zi + 1)
        baa = self._hash(xi + 1, yi, zi)
        bba = self._hash(xi + 1, yi + 1, zi)
        bab = self._hash(xi + 1, yi, zi + 1)
        bbb = self._hash(xi + 1, yi + 1, zi + 1)

        x1 = self._lerp(
            self._grad3d(aaa, xf, yf, zf), self._grad3d(baa, xf - 1, yf, zf), u
        )
        x2 = self._lerp(
            self._grad3d(aba, xf, yf - 1, zf), self._grad3d(bba, xf - 1, yf - 1, zf), u
        )
        y1 = self._lerp(x1, x2, v)

        x1 = self._lerp(
            self._grad3d(aab, xf, yf, zf - 1), self._grad3d(bab, xf - 1, yf, zf - 1), u
        )
        x2 = self._lerp(
            self._grad3d(abb, xf, yf - 1, zf - 1),
            self._grad3d(bbb, xf - 1, yf - 1, zf - 1),
            u,
        )
        y2 = self._lerp(x1, x2, v)

        return self._lerp(y1, y2, w)

    def _fbm1d(self, x: float) -> float:
        """Fractal Brownian Motion for 1D."""
        total = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0

        for _ in range(self.octaves):
            total += amplitude * self._noise1d_cached(x * frequency)
            max_value += amplitude
            amplitude *= self.persistence
            frequency *= self.lacunarity

        return total / max_value if max_value else 0.0

    def _fbm2d(self, x: float, y: float) -> float:
        """Fractal Brownian Motion for 2D."""
        total = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0

        for _ in range(self.octaves):
            total += amplitude * self._noise2d_cached(x * frequency, y * frequency)
            max_value += amplitude
            amplitude *= self.persistence
            frequency *= self.lacunarity

        return total / max_value if max_value else 0.0

    def _fbm3d(self, x: float, y: float, z: float) -> float:
        """Fractal Brownian Motion for 3D."""
        total = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0

        for _ in range(self.octaves):
            total += amplitude * self._noise3d_cached(
                x * frequency, y * frequency, z * frequency
            )
            max_value += amplitude
            amplitude *= self.persistence
            frequency *= self.lacunarity

        return total / max_value if max_value else 0.0

    def get1d(self, x: float) -> float:
        """Get 1D noise value at coordinate x."""
        scaled_x = x / self.scale if self.scale else x
        return self._fbm1d(scaled_x)

    def get2d(self, x: float, y: float) -> float:
        """Get 2D noise value at coordinates (x, y)."""
        scaled_x = x / self.scale if self.scale else x
        scaled_y = y / self.scale if self.scale else y
        return self._fbm2d(scaled_x, scaled_y)

    def get3d(self, x: float, y: float, z: float) -> float:
        """Get 3D noise value at coordinates (x, y, z)."""
        scaled_x = x / self.scale if self.scale else x
        scaled_y = y / self.scale if self.scale else y
        scaled_z = z / self.scale if self.scale else z
        return self._fbm3d(scaled_x, scaled_y, scaled_z)

    def get(self, *coords: float) -> float:
        """Get noise value at the given coordinates.

        Dispatches to get1d, get2d, or get3d based on the number of coordinates.

        Raises:
            ValueError: If the number of coordinates is not 1, 2, or 3.
        """
        num_coords = len(coords)
        if num_coords == 1:
            return self.get1d(coords[0])
        elif num_coords == 2:
            return self.get2d(coords[0], coords[1])
        elif num_coords == 3:
            return self.get3d(coords[0], coords[1], coords[2])
        else:
            raise ValueError(f"Expected 1, 2, or 3 coordinates, got {num_coords}")

    def clear_cache(self) -> None:
        """Clear the LRU cache for all noise methods."""
        if hasattr(self._noise1d_cached, "cache_clear"):
            self._noise1d_cached.cache_clear()
        if hasattr(self._noise2d_cached, "cache_clear"):
            self._noise2d_cached.cache_clear()
        if hasattr(self._noise3d_cached, "cache_clear"):
            self._noise3d_cached.cache_clear()

    def cache_info(self) -> dict[str, object]:
        """Get cache statistics for all noise methods."""
        info: dict[str, object] = {}
        if hasattr(self._noise1d_cached, "cache_info"):
            info["1d"] = self._noise1d_cached.cache_info()
        if hasattr(self._noise2d_cached, "cache_info"):
            info["2d"] = self._noise2d_cached.cache_info()
        if hasattr(self._noise3d_cached, "cache_info"):
            info["3d"] = self._noise3d_cached.cache_info()
        return info
