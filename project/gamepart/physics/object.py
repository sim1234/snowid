import typing

import pymunk


class Object:
    def __init__(self, body: pymunk.Body, shapes: typing.Iterable[pymunk.Shape]):
        self.body = body
        self.shapes = shapes if isinstance(shapes, list) else list(shapes)

    @property
    def position(self) -> pymunk.Vec2d:
        return self.body.position


class SimpleObject(Object):
    def __init__(self, body: pymunk.Body, shape: pymunk.Shape):
        super().__init__(body, [shape])

    @property
    def shape(self) -> pymunk.Shape:
        return self.shapes[0]
