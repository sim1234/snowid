"""Integration tests for PhysicalObject classes."""

import pymunk
import pytest
from gamepart.physics.category import Category, cat_none
from gamepart.physics.physicalobject import (
    AwareObject,
    CollisionObject,
    PhysicalObject,
    SimplePhysicalObject,
)


class TestPhysicalObjectInit:
    """Tests for PhysicalObject initialization."""

    def test_creates_with_body_and_shapes(self) -> None:
        """Test PhysicalObject creates with body and shapes."""
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = PhysicalObject(body, [shape])

        assert obj.body is body
        assert shape in obj.shapes

    def test_creates_with_none_body(self) -> None:
        """Test PhysicalObject creates with None body (static)."""
        shape = pymunk.Circle(None, 10)
        obj = PhysicalObject(None, [shape])

        assert obj.body is None
        assert shape in obj.shapes

    def test_creates_with_multiple_shapes(self) -> None:
        """Test PhysicalObject creates with multiple shapes."""
        body = pymunk.Body(1, 1)
        shape1 = pymunk.Circle(body, 10)
        shape2 = pymunk.Circle(body, 5, (10, 0))
        obj = PhysicalObject(body, [shape1, shape2])

        assert len(obj.shapes) == 2
        assert shape1 in obj.shapes
        assert shape2 in obj.shapes

    def test_default_category_is_cat_none(self) -> None:
        """Test default category is cat_none."""
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = PhysicalObject(body, [shape])

        assert obj.category == cat_none

    def test_accepts_custom_category(self) -> None:
        """Test PhysicalObject accepts custom category."""
        Category.global_index = 1
        category = Category()
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = PhysicalObject(body, [shape], category=category)

        assert obj.category == category


class TestPhysicalObjectPosition:
    """Tests for PhysicalObject position property."""

    def test_get_position(self) -> None:
        """Test getting position from body."""
        body = pymunk.Body(1, 1)
        body.position = (100.0, 200.0)
        shape = pymunk.Circle(body, 10)
        obj = PhysicalObject(body, [shape])

        pos = obj.position
        assert pos[0] == 100.0
        assert pos[1] == 200.0

    def test_set_position(self) -> None:
        """Test setting position on body."""
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = PhysicalObject(body, [shape])

        obj.position = (50.0, 75.0)
        assert body.position.x == 50.0
        assert body.position.y == 75.0

    def test_get_position_raises_when_body_none(self) -> None:
        """Test getting position raises when body is None."""
        shape = pymunk.Circle(None, 10)
        obj = PhysicalObject(None, [shape])

        with pytest.raises(ValueError, match="Cannot get position"):
            _ = obj.position

    def test_set_position_raises_when_body_none(self) -> None:
        """Test setting position raises when body is None."""
        shape = pymunk.Circle(None, 10)
        obj = PhysicalObject(None, [shape])

        with pytest.raises(ValueError, match="Cannot set position"):
            obj.position = (10.0, 20.0)


class TestPhysicalObjectBodies:
    """Tests for PhysicalObject bodies property."""

    def test_bodies_returns_list_with_body(self) -> None:
        """Test bodies returns list with body."""
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = PhysicalObject(body, [shape])

        bodies = list(obj.bodies)
        assert len(bodies) == 1
        assert body in bodies

    def test_bodies_returns_empty_when_body_none(self) -> None:
        """Test bodies returns empty list when body is None."""
        shape = pymunk.Circle(None, 10)
        obj = PhysicalObject(None, [shape])

        bodies = list(obj.bodies)
        assert len(bodies) == 0


class TestSimplePhysicalObject:
    """Tests for SimplePhysicalObject class."""

    def test_creates_with_single_shape(self) -> None:
        """Test SimplePhysicalObject creates with single shape."""
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = SimplePhysicalObject(body, shape)

        assert obj.body is body
        assert len(obj.shapes) == 1
        assert obj.shapes[0] is shape

    def test_shape_property_returns_shape(self) -> None:
        """Test shape property returns the shape."""
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = SimplePhysicalObject(body, shape)

        assert obj.shape is shape

    def test_shape_property_typed(self) -> None:
        """Test shape property works with typed shapes."""
        body = pymunk.Body(1, 1)
        circle = pymunk.Circle(body, 10)
        obj: SimplePhysicalObject[pymunk.Circle] = SimplePhysicalObject(body, circle)

        assert obj.shape.radius == 10

    def test_accepts_category(self) -> None:
        """Test SimplePhysicalObject accepts category."""
        Category.global_index = 1
        category = Category()
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = SimplePhysicalObject(body, shape, category=category)

        assert obj.category == category


class TestCollisionObject:
    """Tests for CollisionObject class."""

    def test_collide_raises_not_implemented(self) -> None:
        """Test collide raises NotImplementedError."""

        class TestCollisionObject(CollisionObject):
            pass

        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = TestCollisionObject(body, [shape])

        with pytest.raises(NotImplementedError):
            obj.collide(None, None)  # type: ignore[arg-type]

    def test_custom_collide_implementation(self) -> None:
        """Test custom collide implementation."""
        collision_log: list[tuple[object, object]] = []

        class TestCollisionObject(CollisionObject):
            def collide(self, arbiter: pymunk.Arbiter, other: PhysicalObject) -> bool:
                collision_log.append((arbiter, other))
                return True

        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = TestCollisionObject(body, [shape])

        other_body = pymunk.Body(1, 1)
        other_shape = pymunk.Circle(other_body, 5)
        other = PhysicalObject(other_body, [other_shape])

        result = obj.collide(None, other)  # type: ignore[arg-type]
        assert result is True
        assert len(collision_log) == 1


class TestAwareObject:
    """Tests for AwareObject class."""

    def test_tick_raises_not_implemented(self) -> None:
        """Test tick raises NotImplementedError."""

        class TestAwareObject(AwareObject):
            pass

        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = TestAwareObject(body, [shape])

        with pytest.raises(NotImplementedError):
            obj.tick(0.016)

    def test_custom_tick_implementation(self) -> None:
        """Test custom tick implementation."""
        tick_log: list[float] = []

        class TestAwareObject(AwareObject):
            def tick(self, delta: float) -> None:
                tick_log.append(delta)

        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = TestAwareObject(body, [shape])

        obj.tick(0.016)
        obj.tick(0.033)

        assert tick_log == [0.016, 0.033]
