"""Tests for miner scene patch module."""

import math

import pytest
from scenes.miner.patch import (
    PATCH_BASE_RADIUS,
    PATCH_RADIUS_PER_RICHNESS,
    RESOURCE_COLORS,
    ResourcePatch,
    richness_to_radius,
)


class TestRichnessToRadius:
    def test_zero_richness(self) -> None:
        assert richness_to_radius(0) == PATCH_BASE_RADIUS

    def test_positive_richness_increases_radius(self) -> None:
        r0 = richness_to_radius(0)
        r100 = richness_to_radius(100)
        assert r100 > r0
        assert r100 == pytest.approx(
            PATCH_BASE_RADIUS + math.sqrt(100) * PATCH_RADIUS_PER_RICHNESS
        )

    def test_negative_richness_treated_as_zero(self) -> None:
        assert richness_to_radius(-10) == PATCH_BASE_RADIUS


class TestResourcePatch:
    def test_init_sets_position_type_richness(self) -> None:
        patch = ResourcePatch((50.0, 60.0), "iron", 100)
        assert patch.position == (50.0, 60.0)
        assert patch.resource_type == "iron"
        assert patch.richness == 100
        assert patch.radius == richness_to_radius(100)

    def test_deplete_reduces_richness(self) -> None:
        patch = ResourcePatch((0.0, 0.0), "copper", 50)
        patch.deplete(10)
        assert patch.richness == 40
        patch.deplete(40)
        assert patch.richness == 0

    def test_deplete_does_not_go_below_zero(self) -> None:
        patch = ResourcePatch((0.0, 0.0), "coal", 5)
        patch.deplete(10)
        assert patch.richness == 0

    def test_deplete_updates_radius(self) -> None:
        patch = ResourcePatch((0.0, 0.0), "iron", 100)
        initial_radius = patch.radius
        patch.deplete(100)
        assert patch.radius < initial_radius
        assert patch.radius == pytest.approx(richness_to_radius(0))

    def test_contains_point_inside(self) -> None:
        patch = ResourcePatch((10.0, 10.0), "iron", 100)
        assert patch.contains_point((10.0, 10.0)) is True
        assert patch.contains_point((10.0 + patch.radius * 0.5, 10.0)) is True

    def test_contains_point_on_edge(self) -> None:
        patch = ResourcePatch((0.0, 0.0), "iron", 100)
        r = patch.radius
        assert patch.contains_point((r, 0.0)) is True
        assert patch.contains_point((r + 0.001, 0.0)) is False

    def test_contains_point_outside(self) -> None:
        patch = ResourcePatch((0.0, 0.0), "iron", 10)
        assert patch.contains_point((100.0, 100.0)) is False

    def test_resource_colors_defined_for_all_types(self) -> None:
        for resource_type in ("iron", "copper", "coal"):
            assert resource_type in RESOURCE_COLORS
            color = RESOURCE_COLORS[resource_type]
            assert len(color) == 4
            assert all(0 <= c <= 255 for c in color)
