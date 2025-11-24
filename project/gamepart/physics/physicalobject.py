import typing

from ..subsystem import SubSystemObject
from .category import Category, cat_none
from .utils import pymunk


class PhysicalObject(SubSystemObject):
    def __init__(
        self,
        body: pymunk.Body | None,
        shapes: typing.Iterable[pymunk.Shape],
        category: Category = cat_none,
    ):
        super().__init__()
        self.body: pymunk.Body | None = body
        self.shapes = list(shapes)
        self.category = category

    @property
    def position(self) -> tuple[float, float]:
        if self.body is None:
            raise ValueError("Cannot get position: body is None")
        return self.body.position

    @property
    def bodies(self) -> typing.Iterable[pymunk.Body]:
        return [self.body] if self.body else []


class CollisionObject(PhysicalObject):
    def collide(self, arbiter: pymunk.Arbiter, other: "PhysicalObject"):
        raise NotImplementedError()


class AwareObject(PhysicalObject):
    def tick(self, delta: float):
        raise NotImplementedError()


T = typing.TypeVar("T", bound=pymunk.Shape)


class SimplePhysicalObject(PhysicalObject, typing.Generic[T]):
    def __init__(
        self,
        body: pymunk.Body | None,
        shape: T,
        category: Category = cat_none,
    ):
        super().__init__(body, [shape], category)

    @property
    def shape(self) -> T:
        return typing.cast(T, self.shapes[0])
