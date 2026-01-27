"""Tests for Vector class."""

import math

import pytest
from gamepart.physics.vector import Vector


class TestVectorCreation:
    """Test Vector creation and initialization."""

    def test_default_creation(self) -> None:
        """Test creating a vector with default values."""
        v = Vector()
        assert v.x == 0.0
        assert v.y == 0.0

    def test_creation_with_values(self) -> None:
        """Test creating a vector with specific values."""
        v = Vector(3.0, 4.0)
        assert v.x == 3.0
        assert v.y == 4.0

    def test_to_from_tuple(self) -> None:
        """Test creating a vector from a tuple."""
        v = Vector.to((5.0, 6.0))
        assert v.x == 5.0
        assert v.y == 6.0

    def test_to_from_list(self) -> None:
        """Test creating a vector from a list."""
        v = Vector.to([7.0, 8.0])
        assert v.x == 7.0
        assert v.y == 8.0

    def test_to_from_vector(self) -> None:
        """Test creating a vector from another vector."""
        v1 = Vector(9.0, 10.0)
        v2 = Vector.to(v1)
        assert v2.x == 9.0
        assert v2.y == 10.0
        assert v2 is not v1  # Should be a copy

    def test_to_from_none(self) -> None:
        """Test creating a vector from None."""
        v = Vector.to(None)
        assert v.x == 0.0
        assert v.y == 0.0

    def test_polar_creation(self) -> None:
        """Test creating a vector from polar coordinates."""
        v = Vector.polar(5.0, math.pi / 4)  # 45 degrees
        assert abs(v.x - 5.0 * math.cos(math.pi / 4)) < 1e-10
        assert abs(v.y - 5.0 * math.sin(math.pi / 4)) < 1e-10

    def test_copy(self) -> None:
        """Test copying a vector."""
        v1 = Vector(3.0, 4.0)
        v2 = v1.copy()
        assert v2.x == v1.x
        assert v2.y == v1.y
        assert v2 is not v1


class TestVectorOperations:
    """Test Vector arithmetic operations."""

    def test_addition(self) -> None:
        """Test vector addition."""
        v1 = Vector(1.0, 2.0)
        v2 = Vector(3.0, 4.0)
        result = v1 + v2
        assert result.x == 4.0
        assert result.y == 6.0

    def test_subtraction(self) -> None:
        """Test vector subtraction."""
        v1 = Vector(5.0, 6.0)
        v2 = Vector(2.0, 3.0)
        result = v1 - v2
        assert result.x == 3.0
        assert result.y == 3.0

    def test_multiplication(self) -> None:
        """Test vector scalar multiplication."""
        v = Vector(2.0, 3.0)
        result = v * 2.0
        assert result.x == 4.0
        assert result.y == 6.0

    def test_division(self) -> None:
        """Test vector scalar division."""
        v = Vector(6.0, 8.0)
        result = v / 2.0
        assert result.x == 3.0
        assert result.y == 4.0

    def test_dot_product(self) -> None:
        """Test vector dot product."""
        v1 = Vector(1.0, 2.0)
        v2 = Vector(3.0, 4.0)
        result = v1 @ v2
        assert result == 1.0 * 3.0 + 2.0 * 4.0  # 11.0

    def test_inplace_addition(self) -> None:
        """Test in-place addition."""
        v = Vector(1.0, 2.0)
        v += Vector(3.0, 4.0)
        assert v.x == 4.0
        assert v.y == 6.0

    def test_inplace_multiplication(self) -> None:
        """Test in-place multiplication."""
        v = Vector(2.0, 3.0)
        v *= 2.0
        assert v.x == 4.0
        assert v.y == 6.0

    def test_negation(self) -> None:
        """Test vector negation."""
        v = Vector(3.0, 4.0)
        result = -v
        assert result.x == -3.0
        assert result.y == -4.0

    def test_invert(self) -> None:
        """Test vector inversion (swap x and y)."""
        v = Vector(3.0, 4.0)
        result = ~v
        assert result.x == 4.0
        assert result.y == 3.0

    def test_inplace_subtraction(self) -> None:
        """Test in-place subtraction."""
        v = Vector(5.0, 6.0)
        v -= Vector(2.0, 3.0)
        assert v.x == 3.0
        assert v.y == 3.0

    def test_reverse_subtraction(self) -> None:
        """Test reverse subtraction (tuple - vector)."""
        v = Vector(2.0, 3.0)
        result = (5.0, 6.0) - v
        assert result.x == 3.0
        assert result.y == 3.0

    def test_inplace_division(self) -> None:
        """Test in-place division."""
        v = Vector(6.0, 8.0)
        v /= 2.0
        assert v.x == 3.0
        assert v.y == 4.0

    def test_unary_positive(self) -> None:
        """Test unary positive operator returns copy."""
        v = Vector(3.0, 4.0)
        result = +v
        assert result.x == 3.0
        assert result.y == 4.0
        assert result is not v

    def test_reverse_addition(self) -> None:
        """Test reverse addition (tuple + vector)."""
        v = Vector(1.0, 2.0)
        result = (3.0, 4.0) + v
        assert result.x == 4.0
        assert result.y == 6.0

    def test_reverse_multiplication(self) -> None:
        """Test reverse multiplication (scalar * vector)."""
        v = Vector(2.0, 3.0)
        result = 2.0 * v
        assert result.x == 4.0
        assert result.y == 6.0


class TestVectorProperties:
    """Test Vector properties and attributes."""

    def test_magnitude(self) -> None:
        """Test vector magnitude (r property)."""
        v = Vector(3.0, 4.0)
        assert abs(v.r - 5.0) < 1e-10  # 3-4-5 triangle

    def test_angle(self) -> None:
        """Test vector angle (phi property)."""
        v = Vector(1.0, 0.0)  # Pointing right
        assert abs(v.phi - 0.0) < 1e-10

        v = Vector(0.0, 1.0)  # Pointing up
        assert abs(v.phi - math.pi / 2) < 1e-10

    def test_set_magnitude(self) -> None:
        """Test setting vector magnitude."""
        v = Vector(3.0, 4.0)
        original_angle = v.phi
        v.r = 10.0
        assert abs(v.r - 10.0) < 1e-10
        assert abs(v.phi - original_angle) < 1e-10

    def test_set_angle(self) -> None:
        """Test setting vector angle."""
        v = Vector(5.0, 0.0)
        original_magnitude = v.r
        v.phi = math.pi / 2
        assert abs(v.phi - math.pi / 2) < 1e-10
        assert abs(v.r - original_magnitude) < 1e-10

    def test_indexing(self) -> None:
        """Test vector indexing."""
        v = Vector(3.0, 4.0)
        assert v[0] == 3.0
        assert v[1] == 4.0

    def test_indexing_out_of_range(self) -> None:
        """Test vector indexing with out of range index."""
        v = Vector(3.0, 4.0)
        with pytest.raises(IndexError):
            _ = v[2]

    def test_setitem_x(self) -> None:
        """Test setting x via index."""
        v = Vector(3.0, 4.0)
        v[0] = 10.0
        assert v.x == 10.0
        assert v.y == 4.0

    def test_setitem_y(self) -> None:
        """Test setting y via index."""
        v = Vector(3.0, 4.0)
        v[1] = 10.0
        assert v.x == 3.0
        assert v.y == 10.0

    def test_setitem_out_of_range(self) -> None:
        """Test setting with out of range index raises IndexError."""
        v = Vector(3.0, 4.0)
        with pytest.raises(IndexError):
            v[2] = 10.0

    def test_length(self) -> None:
        """Test vector length."""
        v = Vector(3.0, 4.0)
        assert len(v) == 2

    def test_bool(self) -> None:
        """Test vector boolean conversion."""
        v1 = Vector(0.0, 0.0)
        assert not bool(v1)  # Both zero

        v2 = Vector(1.0, 0.0)
        assert not bool(v2)  # Vector.__bool__ requires BOTH x and y to be truthy

        v3 = Vector(0.0, 1.0)
        assert not bool(v3)  # Vector.__bool__ requires BOTH x and y to be truthy

        v4 = Vector(1.0, 1.0)
        assert bool(v4)  # Both non-zero


class TestVectorMethods:
    """Test Vector utility methods."""

    def test_replace(self) -> None:
        """Test replacing vector values."""
        v = Vector(1.0, 2.0)
        v.replace((5.0, 6.0))
        assert v.x == 5.0
        assert v.y == 6.0

    def test_update(self) -> None:
        """Test updating vector values."""
        v = Vector(1.0, 2.0)
        result = v.update(5.0, 6.0)
        assert v.x == 5.0
        assert v.y == 6.0
        assert result is v  # Should return self

    def test_normal(self) -> None:
        """Test getting normalized vector."""
        v = Vector(3.0, 4.0)
        normal = v.normal()
        assert abs(normal.r - 1.0) < 1e-10
        assert abs(normal.phi - v.phi) < 1e-10

    def test_tangent(self) -> None:
        """Test getting tangent vector."""
        v = Vector(1.0, 0.0)  # Pointing right
        tangent = v.tangent()
        assert abs(tangent.x - 0.0) < 1e-10
        assert abs(tangent.y - 1.0) < 1e-10  # Pointing up (90 degrees CCW)

    def test_cross_product(self) -> None:
        """Test pseudo cross product."""
        v1 = Vector(1.0, 0.0)  # phi = 0
        v2 = Vector(0.0, 1.0)  # phi = pi/2
        result = v1.cross(v2)
        # v1.phi - v2.phi = 0 - pi/2 = -pi/2
        # sin(-pi/2) = -1, so result is negative
        assert result < 0

        # Test reverse order
        result2 = v2.cross(v1)
        # v2.phi - v1.phi = pi/2 - 0 = pi/2
        # sin(pi/2) = 1, so result is positive
        assert result2 > 0

    def test_decompose(self) -> None:
        """Test vector decomposition."""
        v = Vector(10.0, 0.0)  # Pointing right
        parallel, orthogonal = v.decompose(0.0)  # Decompose along x-axis
        assert abs(parallel.x - 10.0) < 1e-10
        assert abs(parallel.y - 0.0) < 1e-10
        assert abs(orthogonal.x - 0.0) < 1e-10
        assert abs(orthogonal.y - 0.0) < 1e-10


class TestVectorEquality:
    """Test Vector equality and comparison."""

    def test_equality_with_tuple(self) -> None:
        """Test vector equality with tuple."""
        v = Vector(3.0, 4.0)
        assert v == (3.0, 4.0)

    def test_equality_with_vector(self) -> None:
        """Test vector equality with another vector."""
        v1 = Vector(3.0, 4.0)
        v2 = Vector(3.0, 4.0)
        assert v1 == v2

    def test_inequality(self) -> None:
        """Test vector inequality."""
        v1 = Vector(3.0, 4.0)
        v2 = Vector(5.0, 6.0)
        assert v1 != v2

    def test_hash(self) -> None:
        """Test vector hashing."""
        v1 = Vector(3.0, 4.0)
        v2 = Vector(3.0, 4.0)
        assert hash(v1) == hash(v2)

    def test_complex_conversion(self) -> None:
        """Test vector to complex conversion."""
        v = Vector(3.0, 4.0)
        c = complex(v)
        assert c == complex(3.0, 4.0)

    def test_iteration(self) -> None:
        """Test vector iteration."""
        v = Vector(3.0, 4.0)
        values = list(v)
        assert values == [3.0, 4.0]

    def test_equality_with_unsupported_type(self) -> None:
        """Test vector equality with unsupported type returns NotImplemented."""
        v = Vector(3.0, 4.0)
        assert (v == "not a vector") is False
        assert (v == 42) is False
        assert (v == {"x": 3.0}) is False

    def test_to_tuple(self) -> None:
        """Test converting vector to tuple."""
        v = Vector(3.0, 4.0)
        result = v.to_tuple()
        assert result == (3.0, 4.0)
        assert isinstance(result, tuple)

    def test_to_empty_args(self) -> None:
        """Test Vector.to with no arguments returns zero vector."""
        v = Vector.to()
        assert v.x == 0.0
        assert v.y == 0.0

    def test_to_with_two_args(self) -> None:
        """Test Vector.to with two separate arguments."""
        v = Vector.to(3.0, 4.0)
        assert v.x == 3.0
        assert v.y == 4.0
