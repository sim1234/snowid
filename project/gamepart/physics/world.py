import typing

import pymunk

from ..time import TimeFeeder
from .object import Object


class World:
    def __init__(self, time_step: float = 1 / 2 ** 10, speed: float = 1.0):
        self.feeder = TimeFeeder(time_step, speed)
        self.objects: typing.List[Object] = []
        self.space = pymunk.Space()

    def get_objects(self, *types) -> typing.Iterable[Object]:
        for obj in self.objects:
            if isinstance(obj, types):
                yield obj

    def add(self, *objects: Object):
        for obj in objects:
            self.space.add(obj.body, *obj.shapes)
        self.objects.extend(objects)

    def remove(self, *objects: Object):
        for obj in objects:
            self.space.remove(obj.body, *obj.shapes)
            self.objects.remove(obj)

    def clear(self):
        for obj in self.objects:
            self.space.remove(obj.body, *obj.shapes)
        self.objects.clear()

    def tick(self, delta: float):
        for delta in self.feeder.tick(delta, 30):
            self.space.step(delta)

    def catch_up(self):
        return self.feeder.catch_up()

    def __del__(self):
        self.clear()
