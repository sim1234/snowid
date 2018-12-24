import typing

from ..subsystem import SubSystemObject
from .utils import pymunk, typed_property


class PhysicalObject(SubSystemObject):
    def __init__(
        self, body: typing.Optional[pymunk.Body], shapes: typing.Iterable[pymunk.Shape]
    ):
        self.body = body
        self.shapes = list(shapes)

    @typed_property(typing.Tuple[float, float])
    def position(self) -> typing.Tuple[float, float]:
        return self.body.position if self.body else (0, 0)

    @property
    def bodies(self) -> typing.Iterable[pymunk.Body]:
        return [self.body] if self.body else []


T = typing.TypeVar("T", bound=pymunk.Shape)


class SimplePhysicalObject(PhysicalObject, typing.Generic[T]):
    def __init__(self, body: typing.Optional[pymunk.Body], shape: T):
        super().__init__(body, [shape])

    @property
    def shape(self) -> T:
        return self.shapes[0]


class PhysicalCircle(SimplePhysicalObject[pymunk.Circle]):
    def __init__(
        self, radius: float = 1, mass: float = 1, position=(0, 0), velocity=(0, 0)
    ):
        body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius))
        body.position = position
        body.velocity = velocity
        shape = pymunk.Circle(body, radius)
        shape.elasticity = 1.0
        shape.friction = 0.01
        super().__init__(body, shape)

    @typed_property(float)
    def radius(self) -> float:
        return self.shape.radius
