"""Tests for ViewPort classes."""

import typing
from unittest.mock import MagicMock

import pytest
from gamepart.viewport import CulledFlippedViewPort, FlippedViewPort, ViewPort
from gamepart.viewport.graphicalobject import GraphicalObject


@pytest.fixture
def mock_renderer() -> MagicMock:
    """Create a mock renderer for testing."""
    return MagicMock()


@pytest.fixture
def viewport(mock_renderer: MagicMock) -> ViewPort:
    """Create a ViewPort for testing."""
    return ViewPort(mock_renderer, width=800, height=600, zoom=1.0, x=0.0, y=0.0)


@pytest.fixture
def flipped_viewport(mock_renderer: MagicMock) -> FlippedViewPort:
    """Create a FlippedViewPort for testing."""
    return FlippedViewPort(mock_renderer, width=800, height=600, zoom=1.0, x=0.0, y=0.0)


class TestViewPort:
    """Test ViewPort basic methods."""

    def test_accepts_graphical_object(self) -> None:
        """accepts should return True for GraphicalObject instances."""

        class TestGraphicalObject(GraphicalObject):
            def __init__(self) -> None:
                super().__init__()
                self.position = (0.0, 0.0)
                self.angle = 0.0

            def draw(self, vp: typing.Any) -> None:
                pass

        obj = TestGraphicalObject()
        assert ViewPort.accepts(obj) is True

    def test_accepts_rejects_non_graphical_object(self) -> None:
        """accepts should return False for non-GraphicalObject instances."""
        assert ViewPort.accepts("not a graphical object") is False
        assert ViewPort.accepts(123) is False
        assert ViewPort.accepts(None) is False

    def test_draw_calls_draw_on_all_objects(self, viewport: ViewPort) -> None:
        """draw should call draw on all added objects."""
        mock_obj1 = MagicMock()
        mock_obj2 = MagicMock()
        viewport.objects = [mock_obj1, mock_obj2]

        viewport.draw()

        mock_obj1.draw.assert_called_once_with(viewport)
        mock_obj2.draw.assert_called_once_with(viewport)

    def test_draw_with_no_objects(self, viewport: ViewPort) -> None:
        """draw should handle empty objects list."""
        viewport.objects = []
        viewport.draw()

    def test_d_to_view_at_zoom_1(self, viewport: ViewPort) -> None:
        """d_to_view should return same distance at zoom 1."""
        viewport.zoom = 1.0
        assert viewport.d_to_view(100.0) == 100.0
        assert viewport.d_to_view(50.0) == 50.0

    def test_d_to_view_at_zoom_2(self, viewport: ViewPort) -> None:
        """d_to_view should double distance at zoom 2."""
        viewport.zoom = 2.0
        assert viewport.d_to_view(100.0) == 200.0
        assert viewport.d_to_view(50.0) == 100.0

    def test_d_to_view_at_zoom_half(self, viewport: ViewPort) -> None:
        """d_to_view should halve distance at zoom 0.5."""
        viewport.zoom = 0.5
        assert viewport.d_to_view(100.0) == 50.0

    def test_d_to_world_at_zoom_1(self, viewport: ViewPort) -> None:
        """d_to_world should return same distance at zoom 1."""
        viewport.zoom = 1.0
        assert viewport.d_to_world(100.0) == 100.0
        assert viewport.d_to_world(50.0) == 50.0

    def test_d_to_world_at_zoom_2(self, viewport: ViewPort) -> None:
        """d_to_world should halve distance at zoom 2."""
        viewport.zoom = 2.0
        assert viewport.d_to_world(100.0) == 50.0
        assert viewport.d_to_world(200.0) == 100.0

    def test_d_to_world_at_zoom_half(self, viewport: ViewPort) -> None:
        """d_to_world should double distance at zoom 0.5."""
        viewport.zoom = 0.5
        assert viewport.d_to_world(100.0) == 200.0

    def test_d_to_view_and_d_to_world_are_inverse(self, viewport: ViewPort) -> None:
        """d_to_view and d_to_world should be inverse operations."""
        viewport.zoom = 1.5
        original = 123.0
        assert viewport.d_to_world(viewport.d_to_view(original)) == pytest.approx(
            original
        )
        assert viewport.d_to_view(viewport.d_to_world(original)) == pytest.approx(
            original
        )


class TestViewPortChangeZoom:
    """Test change_zoom method."""

    def test_change_zoom_multiplies_zoom(self, viewport: ViewPort) -> None:
        """change_zoom should multiply current zoom by change factor."""
        viewport.zoom = 1.0
        viewport.change_zoom(2.0)
        assert viewport.zoom == 2.0

    def test_change_zoom_with_factor_less_than_one(self, viewport: ViewPort) -> None:
        """change_zoom with factor < 1 should zoom out."""
        viewport.zoom = 2.0
        viewport.change_zoom(0.5)
        assert viewport.zoom == 1.0

    def test_change_zoom_default_uses_center(self, viewport: ViewPort) -> None:
        """change_zoom without pos should zoom around center."""
        viewport.x = 0
        viewport.y = 0
        viewport.zoom = 1.0
        center_before = viewport.center

        viewport.change_zoom(2.0)

        center_after = viewport.center
        assert center_before[0] == pytest.approx(center_after[0], abs=0.01)
        assert center_before[1] == pytest.approx(center_after[1], abs=0.01)

    def test_change_zoom_around_specific_point(self, viewport: ViewPort) -> None:
        """change_zoom with pos should zoom around that point."""
        viewport.x = 0
        viewport.y = 0
        viewport.zoom = 1.0
        zoom_point = (100.0, 100.0)

        viewport.change_zoom(2.0, pos=zoom_point)

        view_pos_after = viewport.to_view(zoom_point)
        assert view_pos_after[0] == pytest.approx(100.0, abs=0.01)
        assert view_pos_after[1] == pytest.approx(100.0, abs=0.01)

    def test_change_zoom_preserves_point_screen_position(
        self, viewport: ViewPort
    ) -> None:
        """The zoom point should stay at same screen position after zoom."""
        viewport.x = 50
        viewport.y = 50
        viewport.zoom = 1.0
        zoom_point = (200.0, 150.0)
        screen_pos_before = viewport.to_view(zoom_point)

        viewport.change_zoom(1.5, pos=zoom_point)

        screen_pos_after = viewport.to_view(zoom_point)
        assert screen_pos_before[0] == pytest.approx(screen_pos_after[0], abs=0.01)
        assert screen_pos_before[1] == pytest.approx(screen_pos_after[1], abs=0.01)


class TestViewPortFollowTarget:
    """Test follow_target method."""

    def test_no_movement_when_target_in_center(self, viewport: ViewPort) -> None:
        """Target in center should not move camera."""
        viewport.x = 0
        viewport.y = 0
        diff_x, diff_y = viewport.follow_target(
            target_position=(400.0, 300.0),
            delta=0.1,
            edge_margin=0.25,
        )
        assert diff_x == 0.0
        assert diff_y == 0.0

    def test_no_movement_when_target_in_safe_zone(self, viewport: ViewPort) -> None:
        """Target within safe zone should not move camera."""
        viewport.x = 0
        viewport.y = 0
        diff_x, diff_y = viewport.follow_target(
            target_position=(300.0, 200.0),
            delta=0.1,
            edge_margin=0.25,
        )
        assert diff_x == 0.0
        assert diff_y == 0.0

    def test_moves_right_when_target_past_right_margin(
        self, viewport: ViewPort
    ) -> None:
        """Camera should move right when target is past right margin."""
        viewport.x = 0
        viewport.y = 0
        diff_x, diff_y = viewport.follow_target(
            target_position=(700.0, 300.0),
            delta=0.1,
            edge_margin=0.25,
        )
        assert diff_x > 0.0
        assert diff_y == 0.0

    def test_moves_left_when_target_past_left_margin(self, viewport: ViewPort) -> None:
        """Camera should move left when target is past left margin."""
        viewport.x = 0
        viewport.y = 0
        diff_x, diff_y = viewport.follow_target(
            target_position=(100.0, 300.0),
            delta=0.1,
            edge_margin=0.25,
        )
        assert diff_x < 0.0
        assert diff_y == 0.0

    def test_moves_down_when_target_past_bottom_margin(
        self, viewport: ViewPort
    ) -> None:
        """Camera should move down when target is past bottom margin."""
        viewport.x = 0
        viewport.y = 0
        diff_x, diff_y = viewport.follow_target(
            target_position=(400.0, 500.0),
            delta=0.1,
            edge_margin=0.25,
        )
        assert diff_x == 0.0
        assert diff_y > 0.0

    def test_moves_up_when_target_past_top_margin(self, viewport: ViewPort) -> None:
        """Camera should move up when target is past top margin."""
        viewport.x = 0
        viewport.y = 0
        diff_x, diff_y = viewport.follow_target(
            target_position=(400.0, 100.0),
            delta=0.1,
            edge_margin=0.25,
        )
        assert diff_x == 0.0
        assert diff_y < 0.0

    def test_no_movement_when_delta_zero(self, viewport: ViewPort) -> None:
        """No movement when delta is zero."""
        viewport.x = 0
        viewport.y = 0
        diff_x, diff_y = viewport.follow_target(
            target_position=(700.0, 500.0),
            delta=0.0,
            edge_margin=0.25,
        )
        assert diff_x == 0.0
        assert diff_y == 0.0

    def test_larger_delta_means_larger_movement(self, viewport: ViewPort) -> None:
        """Larger delta should result in larger movement."""
        viewport.x = 0
        viewport.y = 0
        diff_small_x, _ = viewport.follow_target(
            target_position=(700.0, 300.0),
            delta=0.01,
            edge_margin=0.25,
        )

        viewport.x = 0
        viewport.y = 0
        diff_large_x, _ = viewport.follow_target(
            target_position=(700.0, 300.0),
            delta=0.1,
            edge_margin=0.25,
        )

        assert abs(diff_large_x) > abs(diff_small_x)

    def test_updates_viewport_position(self, viewport: ViewPort) -> None:
        """follow_target should update viewport x and y."""
        viewport.x = 0
        viewport.y = 0
        viewport.follow_target(
            target_position=(700.0, 500.0),
            delta=0.1,
            edge_margin=0.25,
        )
        assert viewport.x > 0.0
        assert viewport.y > 0.0

    def test_respects_zoom(self, viewport: ViewPort) -> None:
        """Movement should be adjusted for zoom level."""
        viewport.x = 0
        viewport.y = 0
        viewport.zoom = 2.0
        diff_zoomed_x, _ = viewport.follow_target(
            target_position=(400.0, 300.0),
            delta=0.1,
            edge_margin=0.25,
        )

        viewport.x = 0
        viewport.y = 0
        viewport.zoom = 1.0
        diff_normal_x, _ = viewport.follow_target(
            target_position=(400.0, 300.0),
            delta=0.1,
            edge_margin=0.25,
        )

        assert diff_zoomed_x != diff_normal_x or (
            diff_zoomed_x == 0.0 and diff_normal_x == 0.0
        )


class TestFlippedViewPortFollowTarget:
    """Test follow_target method for FlippedViewPort."""

    def test_no_movement_when_target_in_center(
        self, flipped_viewport: FlippedViewPort
    ) -> None:
        """Target in center should not move camera."""
        flipped_viewport.center = (400.0, 300.0)
        diff_x, diff_y = flipped_viewport.follow_target(
            target_position=(400.0, 300.0),
            delta=0.1,
            edge_margin=0.25,
        )
        assert diff_x == 0.0
        assert diff_y == 0.0

    def test_moves_up_when_target_past_top_margin(
        self, flipped_viewport: FlippedViewPort
    ) -> None:
        """Camera should move up (increase y) when target is past top margin."""
        flipped_viewport.x = 0
        flipped_viewport.y = 0
        diff_x, diff_y = flipped_viewport.follow_target(
            target_position=(400.0, 500.0),
            delta=0.1,
            edge_margin=0.25,
        )
        assert diff_x == 0.0
        assert diff_y > 0.0

    def test_moves_down_when_target_past_bottom_margin(
        self, flipped_viewport: FlippedViewPort
    ) -> None:
        """Camera should move down (decrease y) when target is past bottom margin."""
        flipped_viewport.x = 0
        flipped_viewport.y = 0
        diff_x, diff_y = flipped_viewport.follow_target(
            target_position=(400.0, -100.0),
            delta=0.1,
            edge_margin=0.25,
        )
        assert diff_x == 0.0
        assert diff_y < 0.0

    def test_x_movement_same_as_regular_viewport(
        self, viewport: ViewPort, flipped_viewport: FlippedViewPort
    ) -> None:
        """X movement should be the same for both viewport types."""
        viewport.x = 0
        viewport.y = 0
        flipped_viewport.x = 0
        flipped_viewport.y = 0

        diff_x_regular, _ = viewport.follow_target(
            target_position=(700.0, 300.0),
            delta=0.1,
            edge_margin=0.25,
        )
        diff_x_flipped, _ = flipped_viewport.follow_target(
            target_position=(700.0, 300.0),
            delta=0.1,
            edge_margin=0.25,
        )

        assert diff_x_regular == diff_x_flipped


class TestCulledFlippedViewPort:
    """Test CulledFlippedViewPort visible rect and culling."""

    @pytest.fixture
    def culled_viewport(self, mock_renderer: MagicMock) -> CulledFlippedViewPort:
        return CulledFlippedViewPort(
            mock_renderer,
            width=800,
            height=600,
            zoom=1.0,
            x=100.0,
            y=200.0,
            cull_margin=50.0,
        )

    def test_visible_world_rect_expands_by_cull_margin(
        self, culled_viewport: CulledFlippedViewPort
    ) -> None:
        minx, miny, maxx, maxy = culled_viewport._visible_world_rect()
        assert minx == pytest.approx(50.0)
        assert maxx == pytest.approx(950.0)
        assert miny == pytest.approx(150.0)
        assert maxy == pytest.approx(850.0)

    def test_visible_world_rect_respects_zoom(self, mock_renderer: MagicMock) -> None:
        vp = CulledFlippedViewPort(
            mock_renderer,
            width=100,
            height=100,
            zoom=2.0,
            x=0.0,
            y=0.0,
            cull_margin=10.0,
        )
        minx, miny, maxx, maxy = vp._visible_world_rect()
        assert maxx - minx == pytest.approx(100.0 / 2.0 + 20.0)
        assert maxy - miny == pytest.approx(100.0 / 2.0 + 20.0)

    def test_draw_calls_only_objects_inside_visible_rect(
        self, culled_viewport: CulledFlippedViewPort
    ) -> None:
        minx, miny, maxx, maxy = culled_viewport._visible_world_rect()
        inside = MagicMock()
        inside.position = (400.0, 400.0)
        inside.radius = 5.0
        outside_left = MagicMock()
        outside_left.position = (minx - 10.0, 400.0)
        outside_left.radius = 5.0
        outside_right = MagicMock()
        outside_right.position = (maxx + 10.0, 400.0)
        outside_right.radius = 5.0
        culled_viewport.objects = [inside, outside_left, outside_right]
        culled_viewport.draw()
        inside.draw.assert_called_once_with(culled_viewport)
        outside_left.draw.assert_not_called()
        outside_right.draw.assert_not_called()

    def test_draw_uses_default_radius_when_missing(
        self, culled_viewport: CulledFlippedViewPort
    ) -> None:
        obj_at_edge = MagicMock()
        obj_at_edge.position = (95.0, 400.0)
        del obj_at_edge.radius
        culled_viewport.objects = [obj_at_edge]
        culled_viewport.draw()
        obj_at_edge.draw.assert_called_once_with(culled_viewport)

    def test_draw_includes_object_touching_rect_boundary(
        self, culled_viewport: CulledFlippedViewPort
    ) -> None:
        minx, miny, maxx, maxy = culled_viewport._visible_world_rect()
        touching = MagicMock()
        touching.position = (minx + 10.0, miny + 10.0)
        touching.radius = 10.0
        culled_viewport.objects = [touching]
        culled_viewport.draw()
        touching.draw.assert_called_once()
