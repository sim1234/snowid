"""Pytest configuration and shared fixtures."""

import pytest
from gamepart.physics.category import Category
from gamepart.physics.vector import Vector
from gamepart.subsystem import SubSystem, SubSystemObject
from gamepart.time import FPSCounter, TimeFeeder


@pytest.fixture
def sample_vector() -> Vector:
    """Create a sample Vector for testing."""
    return Vector(3.0, 4.0)


@pytest.fixture
def zero_vector() -> Vector:
    """Create a zero Vector for testing."""
    return Vector(0.0, 0.0)


@pytest.fixture
def sample_category() -> Category:
    """Create a sample Category for testing."""
    Category.global_index = 1
    return Category()


@pytest.fixture
def fps_counter() -> FPSCounter:
    """Create an FPSCounter for testing."""
    return FPSCounter(maxlen=10)


@pytest.fixture
def time_feeder() -> TimeFeeder:
    """Create a TimeFeeder for testing."""
    return TimeFeeder(time_step=0.1, speed=1.0)


class TestObject(SubSystemObject):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name


class TestSubSystem(SubSystem[TestObject]):
    pass


@pytest.fixture
def subsystem() -> TestSubSystem:
    """Create a SubSystem for testing."""

    return TestSubSystem()
