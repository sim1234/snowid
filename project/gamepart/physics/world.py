import typing

import pymunk

from ..subsystem import SubSystem
from .physicalobject import AwareObject, CollisionObject, PhysicalObject


class World(SubSystem[PhysicalObject]):
    def __init__(self, speed: float = 1.0):
        super().__init__()
        self.speed = speed
        self.space = pymunk.Space()
        self.shape_map: dict[pymunk.Shape, PhysicalObject] = {}

    @staticmethod
    def accepts(obj: typing.Any) -> bool:
        return isinstance(obj, PhysicalObject)

    def add(self, *objects: PhysicalObject) -> typing.Iterable[PhysicalObject]:
        super().add(*objects)
        for obj in objects:
            self.space.add(*obj.bodies, *obj.shapes)
            for shape in obj.shapes:
                self.shape_map[shape] = obj
        return objects

    def remove(self, *objects: PhysicalObject) -> typing.Iterable[PhysicalObject]:  # type: ignore[override]
        for obj in objects:
            self.space.remove(*obj.bodies, *obj.shapes)
            for shape in obj.shapes:
                del self.shape_map[shape]
        return super().remove(*objects)

    def _collide(self, arbiter: pymunk.Arbiter, obj: CollisionObject) -> None:
        other = self.shape_map[arbiter.shapes[1]]
        obj.collide(arbiter, other)

    def tick(self, delta: float) -> None:
        self.space.step(delta * self.speed)
        for a_obj in self.get_objects(AwareObject):
            a_obj.tick(delta)
        for c_obj in self.get_objects(CollisionObject):
            for body in c_obj.bodies:
                body.each_arbiter(self._collide, c_obj)
