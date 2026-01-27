"""Integration tests for physics utility functions."""

import pymunk
from gamepart.physics.utils import make_body, typed_property, update_shape


class TestMakeBody:
    """Tests for make_body factory function."""

    def test_creates_dynamic_body_by_default(self) -> None:
        """Test make_body creates dynamic body by default."""
        body = make_body()
        assert body.body_type == pymunk.Body.DYNAMIC

    def test_creates_body_with_mass_and_moment(self) -> None:
        """Test make_body sets mass and moment."""
        body = make_body(mass=10.0, moment=100.0)
        assert body.mass == 10.0
        assert body.moment == 100.0

    def test_creates_static_body(self) -> None:
        """Test make_body can create static body."""
        body = make_body(body_type=pymunk.Body.STATIC)
        assert body.body_type == pymunk.Body.STATIC

    def test_creates_kinematic_body(self) -> None:
        """Test make_body can create kinematic body."""
        body = make_body(body_type=pymunk.Body.KINEMATIC)
        assert body.body_type == pymunk.Body.KINEMATIC

    def test_sets_position_via_kwargs(self) -> None:
        """Test make_body sets position via kwargs."""
        body = make_body(position=(100.0, 200.0))
        assert body.position.x == 100.0
        assert body.position.y == 200.0

    def test_sets_velocity_via_kwargs(self) -> None:
        """Test make_body sets velocity via kwargs."""
        body = make_body(velocity=(50.0, -25.0))
        assert body.velocity.x == 50.0
        assert body.velocity.y == -25.0

    def test_sets_angle_via_kwargs(self) -> None:
        """Test make_body sets angle via kwargs."""
        import math

        body = make_body(angle=math.pi / 2)
        assert abs(body.angle - math.pi / 2) < 0.0001

    def test_sets_multiple_kwargs(self) -> None:
        """Test make_body sets multiple kwargs."""
        body = make_body(
            mass=5.0,
            moment=50.0,
            position=(10.0, 20.0),
            velocity=(1.0, 2.0),
        )
        assert body.mass == 5.0
        assert body.moment == 50.0
        assert body.position.x == 10.0
        assert body.velocity.y == 2.0


class TestUpdateShape:
    """Tests for update_shape function."""

    def test_updates_friction(self) -> None:
        """Test update_shape sets friction."""
        shape = pymunk.Circle(None, 10)
        update_shape(shape, friction=0.5)
        assert shape.friction == 0.5

    def test_updates_elasticity(self) -> None:
        """Test update_shape sets elasticity."""
        shape = pymunk.Circle(None, 10)
        update_shape(shape, elasticity=0.8)
        assert shape.elasticity == 0.8

    def test_updates_collision_type(self) -> None:
        """Test update_shape sets collision_type."""
        shape = pymunk.Circle(None, 10)
        update_shape(shape, collision_type=5)
        assert shape.collision_type == 5

    def test_updates_multiple_attributes(self) -> None:
        """Test update_shape sets multiple attributes."""
        shape = pymunk.Circle(None, 10)
        update_shape(shape, friction=0.3, elasticity=0.7, collision_type=2)
        assert shape.friction == 0.3
        assert shape.elasticity == 0.7
        assert shape.collision_type == 2

    def test_returns_shape(self) -> None:
        """Test update_shape returns the shape."""
        shape = pymunk.Circle(None, 10)
        result = update_shape(shape, friction=0.5)
        assert result is shape

    def test_works_with_segment_shape(self) -> None:
        """Test update_shape works with Segment."""
        shape = pymunk.Segment(None, (0, 0), (10, 10), 1)
        update_shape(shape, friction=0.9)
        assert shape.friction == 0.9

    def test_works_with_poly_shape(self) -> None:
        """Test update_shape works with Poly."""
        vertices = [(0, 0), (10, 0), (10, 10), (0, 10)]
        shape = pymunk.Poly(None, vertices)
        update_shape(shape, elasticity=0.5)
        assert shape.elasticity == 0.5


class TestTypedProperty:
    """Tests for typed_property decorator."""

    def test_creates_property(self) -> None:
        """Test typed_property creates a property."""
        prop = typed_property(int)

        def getter(self: object) -> int:
            return 42

        result = prop(getter)
        assert isinstance(result, property)

    def test_property_works_as_getter(self) -> None:
        """Test typed_property property works as getter."""
        prop_factory = typed_property(str)

        class TestClass:
            @prop_factory
            def name(self) -> str:
                return "test_value"

        obj = TestClass()
        assert obj.name == "test_value"

    def test_preserves_return_type_annotation(self) -> None:
        """Test typed_property preserves type annotation."""
        prop = typed_property(float)
        assert prop.__annotations__.get("return") is float
