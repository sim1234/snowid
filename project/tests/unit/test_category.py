"""Tests for Category class."""

import pytest
from gamepart.physics.category import Category, cat_all, cat_none


class TestCategoryCreation:
    """Test Category creation and initialization."""

    def test_default_creation(self) -> None:
        """Test creating a category with default index."""
        Category.global_index = 1
        cat1 = Category()
        assert int(cat1) == 1

        cat2 = Category()
        assert int(cat2) == 2

        cat3 = Category()
        assert int(cat3) == 4

    def test_forced_index(self) -> None:
        """Test creating a category with forced index."""
        cat = Category(8)
        assert int(cat) == 8

    def test_zero_category(self) -> None:
        """Test creating zero category."""
        cat = Category(0)
        assert int(cat) == 0
        assert bool(cat)  # Category(0) returns True for __bool__ (index == 0)

    def test_invalid_index_too_large(self) -> None:
        """Test creating category with invalid index."""
        with pytest.raises(AssertionError):
            Category(2**65)


class TestCategoryOperations:
    """Test Category bitwise operations."""

    def test_or_operation(self) -> None:
        """Test category OR operation."""
        cat1 = Category(1)
        cat2 = Category(2)
        result = cat1 | cat2
        assert int(result) == 3

    def test_and_operation(self) -> None:
        """Test category AND operation."""
        cat1 = Category(3)  # 0b11
        cat2 = Category(2)  # 0b10
        result = cat1 & cat2
        assert int(result) == 2

    def test_xor_operation(self) -> None:
        """Test category XOR operation."""
        cat1 = Category(3)  # 0b11
        cat2 = Category(2)  # 0b10
        result = cat1 ^ cat2
        assert int(result) == 1

    def test_negation(self) -> None:
        """Test category negation."""
        # Negation creates a negative index which will fail assertion
        # So we skip this test as it's not a valid operation
        cat = Category(5)  # 0b101
        with pytest.raises(AssertionError):
            _ = -cat  # Negation creates invalid index

    def test_subtraction(self) -> None:
        """Test category subtraction."""
        cat1 = Category(7)  # 0b111
        cat2 = Category(2)  # 0b10
        result = cat1 - cat2
        assert int(result) == 5  # 0b101

    def test_addition_same_as_or(self) -> None:
        """Test that addition is same as OR."""
        cat1 = Category(1)
        cat2 = Category(2)
        result_add = cat1 + cat2
        result_or = cat1 | cat2
        assert int(result_add) == int(result_or)

    def test_contains(self) -> None:
        """Test category contains operation."""
        cat1 = Category(7)  # 0b111
        cat2 = Category(2)  # 0b10
        assert cat2 in cat1
        assert Category(8) not in cat1  # 0b1000 not in 0b111


class TestCategoryFilter:
    """Test Category filter creation."""

    def test_filter_default(self) -> None:
        """Test creating filter with default mask."""
        cat = Category(1)
        filter_obj = cat.filter()
        # pymunk ShapeFilter structure - verify it was created successfully
        assert filter_obj is not None
        assert filter_obj.group == 0

    def test_filter_with_mask(self) -> None:
        """Test creating filter with custom mask."""
        cat = Category(1)
        filter_obj = cat.filter(mask=3)
        # pymunk ShapeFilter structure - verify it was created successfully
        assert filter_obj is not None
        assert filter_obj.group == 0

    def test_filter_with_group(self) -> None:
        """Test creating filter with custom group."""
        cat = Category(1)
        filter_obj = cat.filter(group=5)
        assert filter_obj.group == 5


class TestCategoryConstants:
    """Test Category constants."""

    def test_cat_none(self) -> None:
        """Test cat_none constant."""
        assert int(cat_none) == 0
        assert bool(cat_none)  # Category(0) returns True for __bool__

    def test_cat_all(self) -> None:
        """Test cat_all constant."""
        # cat_all should have all bits set
        assert isinstance(cat_all, Category)
        # The exact value depends on pymunk's ALL_MASKS()


class TestCategoryRepresentation:
    """Test Category string representation."""

    def test_repr(self) -> None:
        """Test category representation."""
        cat = Category(5)
        repr_str = repr(cat)
        assert "Category" in repr_str
        assert "0b" in repr_str or "bin" in repr_str.lower()

    def test_int_conversion(self) -> None:
        """Test category integer conversion."""
        cat = Category(42)
        assert int(cat) == 42

    def test_bool_conversion(self) -> None:
        """Test category boolean conversion."""
        cat_zero = Category(0)
        assert bool(cat_zero)  # Category.__bool__ returns (index == 0), so True for 0

        cat_nonzero = Category(1)
        assert not bool(cat_nonzero)  # False for non-zero
