import itertools
import typing

from .object import Object
from .collide import CollidableObject


class World:
    def __init__(self, time_step: float = 1 / 2 ** 10, speed: float = 1.0):
        self.time_step = time_step
        self.objects: typing.List[Object] = []
        self.speed = speed
        self.system_time = 0.0
        self.world_time = 0.0

    def get_objects(self, *types) -> typing.Iterable[Object]:
        for obj in self.objects:
            if isinstance(obj, types):
                yield obj

    def add(self, *objects: Object):
        self.objects.extend(objects)

    def clear(self):
        self.objects.clear()

    def tick(self, delta: float):
        self.system_time += delta * self.speed
        x = 0
        while self.world_time < self.system_time:
            self.world_time += self.time_step
            self._tick()
            x += 1
            if x > 10:
                break

    def _tick(self):
        collidables = self.get_objects(CollidableObject)
        for obj1, obj2 in itertools.combinations(collidables, 2):
            obj1.collide(obj2, self.time_step)

        for obj in self.objects:
            obj.tick(self.time_step)

    def get_energy(self) -> float:
        return sum([o.get_energy() for o in self.objects])
