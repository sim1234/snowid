"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_vector():
    """Create a sample Vector for testing."""
    from gamepart.physics.vector import Vector

    return Vector(3.0, 4.0)


@pytest.fixture
def zero_vector():
    """Create a zero Vector for testing."""
    from gamepart.physics.vector import Vector

    return Vector(0.0, 0.0)


@pytest.fixture
def sample_category():
    """Create a sample Category for testing."""
    from gamepart.physics.category import Category

    # Reset global index for predictable tests
    Category.global_index = 1
    return Category()


@pytest.fixture
def fps_counter():
    """Create an FPSCounter for testing."""
    from gamepart.time import FPSCounter

    return FPSCounter(maxlen=10)


@pytest.fixture
def time_feeder():
    """Create a TimeFeeder for testing."""
    from gamepart.time import TimeFeeder

    return TimeFeeder(time_step=0.1, speed=1.0)


@pytest.fixture
def subsystem():
    """Create a SubSystem for testing."""
    from gamepart.subsystem import SubSystem, SubSystemObject

    class TestObject(SubSystemObject):
        def __init__(self, name: str):
            super().__init__()
            self.name = name

    class TestSubSystem(SubSystem[TestObject]):
        pass

    return TestSubSystem()
