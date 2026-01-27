"""Integration tests for World physics subsystem."""

import pymunk
from gamepart.physics.physicalobject import (
    AwareObject,
    PhysicalObject,
)
from gamepart.physics.world import World


class TestWorldInit:
    """Tests for World initialization."""

    def test_creates_with_default_speed(self) -> None:
        """Test World creates with default speed of 1.0."""
        world = World()
        assert world.speed == 1.0

    def test_creates_with_custom_speed(self) -> None:
        """Test World creates with custom speed."""
        world = World(speed=2.0)
        assert world.speed == 2.0

    def test_creates_pymunk_space(self) -> None:
        """Test World creates a pymunk Space."""
        world = World()
        assert isinstance(world.space, pymunk.Space)

    def test_creates_empty_shape_map(self) -> None:
        """Test World creates empty shape_map."""
        world = World()
        assert world.shape_map == {}

    def test_creates_empty_objects_list(self) -> None:
        """Test World creates empty objects list."""
        world = World()
        assert len(world.objects) == 0


class TestWorldAccepts:
    """Tests for World.accepts method."""

    def test_accepts_physical_object(self) -> None:
        """Test accepts returns True for PhysicalObject."""
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = PhysicalObject(body, [shape])

        assert World.accepts(obj) is True

    def test_rejects_non_physical_object(self) -> None:
        """Test accepts returns False for non-PhysicalObject."""
        assert World.accepts("not a physical object") is False
        assert World.accepts(42) is False
        assert World.accepts(None) is False


class TestWorldAdd:
    """Tests for World.add method."""

    def test_adds_object_to_objects_list(self) -> None:
        """Test add puts object in objects list."""
        world = World()
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = PhysicalObject(body, [shape])

        world.add(obj)

        assert obj in world.objects

    def test_adds_body_to_space(self) -> None:
        """Test add puts body in space."""
        world = World()
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = PhysicalObject(body, [shape])

        world.add(obj)

        assert body in world.space.bodies

    def test_adds_shapes_to_space(self) -> None:
        """Test add puts shapes in space."""
        world = World()
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = PhysicalObject(body, [shape])

        world.add(obj)

        assert shape in world.space.shapes

    def test_maps_shapes_to_object(self) -> None:
        """Test add maps shapes to object in shape_map."""
        world = World()
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = PhysicalObject(body, [shape])

        world.add(obj)

        assert world.shape_map[shape] is obj

    def test_adds_multiple_objects(self) -> None:
        """Test add works with multiple objects."""
        world = World()
        body1 = pymunk.Body(1, 1)
        shape1 = pymunk.Circle(body1, 10)
        obj1 = PhysicalObject(body1, [shape1])

        body2 = pymunk.Body(1, 1)
        shape2 = pymunk.Circle(body2, 5)
        obj2 = PhysicalObject(body2, [shape2])

        world.add(obj1, obj2)

        assert obj1 in world.objects
        assert obj2 in world.objects
        assert len(world.objects) == 2

    def test_adds_object_with_multiple_shapes(self) -> None:
        """Test add works with object having multiple shapes."""
        world = World()
        body = pymunk.Body(1, 1)
        shape1 = pymunk.Circle(body, 10)
        shape2 = pymunk.Circle(body, 5, (10, 0))
        obj = PhysicalObject(body, [shape1, shape2])

        world.add(obj)

        assert world.shape_map[shape1] is obj
        assert world.shape_map[shape2] is obj

    def test_adds_static_object_with_static_body(self) -> None:
        """Test add works with static body."""
        world = World()
        static_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Segment(static_body, (0, 0), (100, 0), 1)
        obj = PhysicalObject(static_body, [shape])

        world.add(obj)

        assert obj in world.objects
        assert shape in world.space.shapes


class TestWorldRemove:
    """Tests for World.remove method."""

    def test_removes_object_from_list(self) -> None:
        """Test remove removes object from objects list."""
        world = World()
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = PhysicalObject(body, [shape])
        world.add(obj)

        world.remove(obj)

        assert obj not in world.objects

    def test_removes_body_from_space(self) -> None:
        """Test remove removes body from space."""
        world = World()
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = PhysicalObject(body, [shape])
        world.add(obj)

        world.remove(obj)

        assert body not in world.space.bodies

    def test_removes_shapes_from_space(self) -> None:
        """Test remove removes shapes from space."""
        world = World()
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = PhysicalObject(body, [shape])
        world.add(obj)

        world.remove(obj)

        assert shape not in world.space.shapes

    def test_removes_shapes_from_shape_map(self) -> None:
        """Test remove removes shapes from shape_map."""
        world = World()
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = PhysicalObject(body, [shape])
        world.add(obj)

        world.remove(obj)

        assert shape not in world.shape_map

    def test_removes_multiple_objects(self) -> None:
        """Test remove works with multiple objects."""
        world = World()
        body1 = pymunk.Body(1, 1)
        shape1 = pymunk.Circle(body1, 10)
        obj1 = PhysicalObject(body1, [shape1])

        body2 = pymunk.Body(1, 1)
        shape2 = pymunk.Circle(body2, 5)
        obj2 = PhysicalObject(body2, [shape2])

        world.add(obj1, obj2)
        world.remove(obj1, obj2)

        assert len(world.objects) == 0
        assert len(world.space.bodies) == 0


class TestWorldTick:
    """Tests for World.tick method."""

    def test_steps_physics_space(self) -> None:
        """Test tick steps the physics space."""
        world = World()
        body = pymunk.Body(1, 1)
        body.position = (0, 0)
        body.velocity = (100, 0)
        shape = pymunk.Circle(body, 10)
        obj = PhysicalObject(body, [shape])
        world.add(obj)

        world.tick(0.1)

        assert body.position.x > 0

    def test_respects_speed_multiplier(self) -> None:
        """Test tick respects speed multiplier."""
        world_normal = World(speed=1.0)
        world_fast = World(speed=2.0)

        body1 = pymunk.Body(1, 1)
        body1.position = (0, 0)
        body1.velocity = (100, 0)
        shape1 = pymunk.Circle(body1, 10)
        obj1 = PhysicalObject(body1, [shape1])
        world_normal.add(obj1)

        body2 = pymunk.Body(1, 1)
        body2.position = (0, 0)
        body2.velocity = (100, 0)
        shape2 = pymunk.Circle(body2, 10)
        obj2 = PhysicalObject(body2, [shape2])
        world_fast.add(obj2)

        world_normal.tick(0.1)
        world_fast.tick(0.1)

        assert body2.position.x > body1.position.x

    def test_calls_tick_on_aware_objects(self) -> None:
        """Test tick calls tick on AwareObjects."""
        tick_log: list[float] = []

        class TestAwareObject(AwareObject):
            def tick(self, delta: float) -> None:
                tick_log.append(delta)

        world = World()
        body = pymunk.Body(1, 1)
        shape = pymunk.Circle(body, 10)
        obj = TestAwareObject(body, [shape])
        world.add(obj)

        world.tick(0.016)

        assert tick_log == [0.016]

    def test_calls_tick_on_multiple_aware_objects(self) -> None:
        """Test tick calls tick on all AwareObjects."""
        tick_counts: dict[str, int] = {"obj1": 0, "obj2": 0}

        class TestAwareObject(AwareObject):
            def __init__(
                self, body: pymunk.Body, shapes: list[pymunk.Shape], name: str
            ) -> None:
                super().__init__(body, shapes)
                self.name = name

            def tick(self, delta: float) -> None:
                tick_counts[self.name] += 1

        world = World()

        body1 = pymunk.Body(1, 1)
        shape1 = pymunk.Circle(body1, 10)
        obj1 = TestAwareObject(body1, [shape1], "obj1")

        body2 = pymunk.Body(1, 1)
        shape2 = pymunk.Circle(body2, 10)
        obj2 = TestAwareObject(body2, [shape2], "obj2")

        world.add(obj1, obj2)
        world.tick(0.016)

        assert tick_counts["obj1"] == 1
        assert tick_counts["obj2"] == 1


class TestWorldCollision:
    """Tests for World collision handling."""

    def test_collision_detection_works(self) -> None:
        """Test that collision detection works in the space."""
        world = World()

        body1 = pymunk.Body(1, 1)
        body1.position = (0, 0)
        shape1 = pymunk.Circle(body1, 20)
        obj1 = PhysicalObject(body1, [shape1])

        body2 = pymunk.Body(1, 1)
        body2.position = (10, 0)
        shape2 = pymunk.Circle(body2, 20)
        obj2 = PhysicalObject(body2, [shape2])

        world.add(obj1, obj2)
        world.tick(0.016)

        query = world.space.shape_query(shape1)
        assert len(query) > 0

    def test_collision_object_receives_collide_callback(self) -> None:
        """Test CollisionObject.collide is called during tick."""
        from gamepart.physics.physicalobject import CollisionObject

        collision_log: list[tuple[PhysicalObject, PhysicalObject]] = []

        class TestCollisionObject(CollisionObject):
            def collide(self, arbiter: pymunk.Arbiter, other: PhysicalObject) -> bool:
                collision_log.append((self, other))
                return True

        world = World()

        body1 = pymunk.Body(1, 1)
        body1.position = (0, 0)
        shape1 = pymunk.Circle(body1, 20)
        obj1 = TestCollisionObject(body1, [shape1])

        body2 = pymunk.Body(1, 1)
        body2.position = (10, 0)
        shape2 = pymunk.Circle(body2, 20)
        obj2 = PhysicalObject(body2, [shape2])

        world.add(obj1, obj2)

        for _ in range(10):
            world.tick(0.016)

        assert len(collision_log) > 0
        assert any(logged[1] is obj2 for logged in collision_log)

    def test_multiple_collision_objects(self) -> None:
        """Test multiple CollisionObjects receive callbacks."""
        from gamepart.physics.physicalobject import CollisionObject

        collision_counts: dict[str, int] = {"obj1": 0, "obj2": 0}

        class TestCollisionObject(CollisionObject):
            def __init__(
                self, body: pymunk.Body, shapes: list[pymunk.Shape], name: str
            ) -> None:
                super().__init__(body, shapes)
                self.name = name

            def collide(self, arbiter: pymunk.Arbiter, other: PhysicalObject) -> bool:
                collision_counts[self.name] += 1
                return True

        world = World()

        body1 = pymunk.Body(1, 1)
        body1.position = (0, 0)
        shape1 = pymunk.Circle(body1, 20)
        obj1 = TestCollisionObject(body1, [shape1], "obj1")

        body2 = pymunk.Body(1, 1)
        body2.position = (15, 0)
        shape2 = pymunk.Circle(body2, 20)
        obj2 = TestCollisionObject(body2, [shape2], "obj2")

        world.add(obj1, obj2)

        for _ in range(10):
            world.tick(0.016)

        assert collision_counts["obj1"] > 0 or collision_counts["obj2"] > 0
