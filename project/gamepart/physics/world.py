import typing

from ..subsystem import SubSystem
from ..time import TimeFeeder
from .utils import pymunk
from .physicalobject import PhysicalObject


class World(SubSystem[PhysicalObject]):
    def __init__(self, time_step: float = 1 / 2 ** 8, speed: float = 1.0):
        super(World, self).__init__()
        self.feeder = TimeFeeder(time_step, speed)
        self.space = pymunk.Space()

    def add(self, *objects: PhysicalObject) -> typing.Iterable[PhysicalObject]:
        for obj in objects:
            self.space.add(obj.body, *obj.shapes)
        return super().add(*objects)

    def remove(self, *objects: PhysicalObject) -> typing.Iterable[PhysicalObject]:
        for obj in objects:
            self.space.remove(obj.body, *obj.shapes)
        return super().remove(*objects)

    def tick(self, delta: float, max_iter: int = 10):
        for delta in self.feeder.tick(delta, max_iter):
            self.space.step(delta)

    def catch_up(self):
        return self.feeder.catch_up()
