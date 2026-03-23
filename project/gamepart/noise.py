"""Perlin noise generator with configurable dimensions and fractal support."""

import random

import numpy as np
from numpy.typing import NDArray

from gamepart.noise_numba import noise1d_raw as _noise1d_raw_nb
from gamepart.noise_numba import noise2d_raw as _noise2d_raw_nb
from gamepart.noise_numba import noise3d_raw as _noise3d_raw_nb


class PerlinNoise:
    """Configurable Perlin noise generator.

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
    ) -> None:
        """Initialize a Perlin noise generator.

        Args:
            seed: Random seed for reproducible noise patterns.
            octaves: Number of noise layers to combine (more = more detail).
            persistence: Amplitude multiplier per octave (0.0-1.0, lower = smoother).
            lacunarity: Frequency multiplier per octave (typically 2.0).
            scale: Coordinate divisor (larger = slower variation).
        """
        self.seed = seed
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
        self.scale = scale

        self._permutation = self._generate_permutation(seed)
        self._perm_arr: NDArray[np.uint8] = np.asarray(
            self._permutation, dtype=np.uint8
        )

    @property
    def permutation_uint8(self) -> NDArray[np.uint8]:
        return self._perm_arr

    def _generate_permutation(self, seed: int) -> list[int]:
        """Generate a permutation table seeded with the given seed."""
        rng = random.Random(seed)
        perm = list(range(256))
        rng.shuffle(perm)
        return perm + perm  # Double for overflow handling

    def _noise1d_raw(self, x: float) -> float:
        """Raw 1D Perlin noise computation."""
        return float(_noise1d_raw_nb(self._perm_arr, x))

    def _noise2d_raw(self, x: float, y: float) -> float:
        """Raw 2D Perlin noise computation."""
        return float(_noise2d_raw_nb(self._perm_arr, x, y))

    def _noise3d_raw(self, x: float, y: float, z: float) -> float:
        """Raw 3D Perlin noise computation."""
        return float(_noise3d_raw_nb(self._perm_arr, x, y, z))

    def _fbm1d(self, x: float) -> float:
        """Fractal Brownian Motion for 1D."""
        total = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0

        for _ in range(self.octaves):
            total += amplitude * self._noise1d_raw(x * frequency)
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
            total += amplitude * self._noise2d_raw(x * frequency, y * frequency)
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
            total += amplitude * self._noise3d_raw(
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
