import typing

from ..subsystem import SubSystemObject
from .utils import pymunk, typed_property
from .category import Category, cat_none


class PhysicalObject(SubSystemObject):
    def __init__(
        self,
        body: typing.Optional[pymunk.Body],
        shapes: typing.Iterable[pymunk.Shape],
        category: Category = cat_none,
    ):
        super().__init__()
        self.body: pymunk.Body = body
        self.shapes = list(shapes)
        self.category = category

    @typed_property(typing.Tuple[float, float])
    def position(self) -> typing.Tuple[float, float]:
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
        body: typing.Optional[pymunk.Body],
        shape: T,
        category: Category = cat_none,
    ):
        super().__init__(body, [shape], category)

    @property
    def shape(self) -> T:
        return self.shapes[0]
