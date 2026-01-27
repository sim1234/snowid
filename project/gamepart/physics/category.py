import typing

import pymunk


class Category:
    global_index = 1
    __slots__ = ("_index",)

    def __init__(self, forced_index: typing.SupportsInt | None = None):
        if forced_index is None:
            forced_index = Category.global_index
            Category.global_index *= 2
        self._index: int = int(forced_index)
        assert 0 <= self._index <= pymunk.ShapeFilter.ALL_MASKS(), self._index

    def __int__(self) -> int:
        return self._index

    def __bool__(self) -> bool:
        return self._index == 0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({bin(self._index)})"

    def __or__(self, other: typing.SupportsInt) -> "Category":
        return Category(self._index | int(other))

    def __and__(self, other: typing.SupportsInt) -> "Category":
        return Category(self._index & int(other))

    def __xor__(self, other: typing.SupportsInt) -> "Category":
        return Category(self._index ^ int(other))

    def __neg__(self) -> "Category":
        return Category(~self._index)

    __add__ = __or__

    def __sub__(self, other: typing.SupportsInt) -> "Category":
        return Category(self._index & ~int(other))

    def __contains__(self, item: typing.SupportsInt) -> bool:
        return bool(self._index & int(item))

    def filter(
        self,
        mask: typing.SupportsInt | None = None,
        group: typing.SupportsInt = 0,
    ) -> pymunk.ShapeFilter:
        if mask is None:
            mask = pymunk.ShapeFilter.ALL_MASKS()
        return pymunk.ShapeFilter(int(group), self._index, int(mask))


cat_none = Category(0)
cat_all = Category(pymunk.ShapeFilter.ALL_MASKS())
