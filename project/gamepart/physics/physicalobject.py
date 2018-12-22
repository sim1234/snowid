import typing

from ..subsystem import SubSystemObject
from .utils import pymunk


class PhysicalObject(SubSystemObject):
    def __init__(self, body: pymunk.Body, shapes: typing.Iterable[pymunk.Shape]):
        self.body = body
        self.shapes = shapes if isinstance(shapes, list) else list(shapes)

    @property
    def position(self) -> pymunk.Vec2d:
        return self.body.position


class SimplePhysicalObject(PhysicalObject):
    def __init__(self, body: pymunk.Body, shape: pymunk.Shape):
        super().__init__(body, [shape])

    @property
    def shape(self) -> pymunk.Shape:
        return self.shapes[0]


class PhysicalCircle(SimplePhysicalObject):
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

    @property
    def radius(self):
        return self.shape.radius
