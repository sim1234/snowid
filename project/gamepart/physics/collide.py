import typing
import copy

import scipy.optimize

from .vector import Vector
from .object import Object, CompleteObject


def find_zero(
    f: typing.Callable,
    obj1: Object,
    obj2: Object,
    min_bound: float = -1 / 32,
    maxiter: int = 50,
    xatol: float = 0.0,
) -> typing.Tuple[bool, float]:
    def fn(t):
        o1 = copy.deepcopy(obj1)
        o2 = copy.deepcopy(obj2)
        o1.tick(t)
        o2.tick(t)
        r = f(o1, o2)
        return r ** 2

    ret = scipy.optimize.minimize_scalar(
        fn,
        method="bounded",
        bounds=(min_bound, 0.0),
        options={"maxiter": maxiter, "xatol": xatol},
    )
    return ret.success, ret.x


class CollidableObject(Object):
    collide_map: typing.Dict[typing.Tuple, typing.Callable] = {}

    def __init__(self, restitution: float = 1, ghost: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.restitution = restitution
        self.ghost = ghost

    def collide(self, other: "CollidableObject", time: float):
        if self.ghost or other.ghost:
            return
        for types, callback in self.collide_map.items():
            if isinstance(self, types[0]) and isinstance(other, types[1]):
                return callback(self, other, time)
            if isinstance(self, types[1]) and isinstance(other, types[0]):
                return callback(other, self, time)
        raise TypeError(
            f"Unable to collide {self.__class__.__qualname__}"
            f" object with {other.__class__.__qualname__} object"
        )

    @classmethod
    def register(
        cls,
        type1: typing.Type["CollidableObject"],
        type2: typing.Type["CollidableObject"],
    ):
        def decorator(callback):
            if not issubclass(type1, CollidableObject):
                raise TypeError(f"{type1.__qualname__} is not collidable")
            if not issubclass(type2, CollidableObject):
                raise TypeError(f"{type2.__qualname__} is not collidable")
            if (type1, type2) in cls.collide_map or (type2, type1) in cls.collide_map:
                raise TypeError(
                    f"{type1.__qualname__} and {type2.__qualname__} already registered"
                )
            cls.collide_map[(type1, type2)] = callback
            return callback

        return decorator

    @classmethod
    def register_with(cls, type2: typing.Type["CollidableObject"]):
        return cls.register(cls, type2)


class PointObject(CompleteObject, CollidableObject):
    pass


@PointObject.register_with(PointObject)
def collide_point_point(point1: "PointObject", point2: PointObject, time: float):
    """Nothing happens"""


class LineObject(CompleteObject, CollidableObject):
    def __init__(self, width: float = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.width = width

    @property
    def end_points(self) -> typing.Tuple[Vector, Vector]:
        off = Vector.polar(self.width / 2, self.rotation)
        return self.position - off, self.position + off

    def distance_to(self, point: Vector) -> float:
        if self.width == 0:
            return (self.position - point).r
        v, w = self.end_points
        t = max(0, min(1, (point - v) @ (w - v) / (self.width ** 2)))
        projection = v + t * (w - v)
        return (point - projection).r

    def side_of(self, point: Vector) -> float:
        v, w = self.end_points
        return (w - v).cross(point - v)


@LineObject.register_with(PointObject)
def collide_line_point(line: "LineObject", point: PointObject, time: float):
    """Nothing happens"""
    o_line = copy.deepcopy(line)
    o_point = copy.deepcopy(point)
    o_line.tick(-time)
    o_point.tick(-time)
    # n_phi = ((point.position - line.position).phi - line.rotation) % (2 * math.pi)
    # o_phi = ((o_point.position - o_line.position).phi - o_line.rotation) % (2 * math.pi)
    if line.side_of(point.position) * o_line.side_of(o_point.position) <= 0:
        success, total_dt = find_zero(
            lambda a, b: a.distance_to(b.position), line, point, -time
        )
        if not success:
            return  # TODO: do something
        point.tick(total_dt)
        line.tick(total_dt)

        phi = (point.position - line.position).phi
        c1_vn, c1_vt = line.velocity.decompose(phi)
        c2_vn, c2_vt = point.velocity.decompose(phi)
        mass = line.mass + point.mass
        cr = min(line.restitution, point.restitution)
        smv = line.mass * c1_vn + point.mass * c2_vn
        c1_vnn = (cr * point.mass * (c2_vn - c1_vn) + smv) / mass
        c2_vnn = (cr * line.mass * (c1_vn - c2_vn) + smv) / mass
        line.velocity.replace(c1_vt + c1_vnn)
        point.velocity.replace(c2_vt + c2_vnn)

        line.tick(-total_dt)
        point.tick(-total_dt)

        import logging

        logging.getLogger(__name__).info("Point Line collision")
    # line.rotation_unit
    # success, total_dt = find_zero(lambda o1, o2: o1.distance_to(o2.position), line, point, -time, maxiter=10, xatol=0.0)
    # if success:
    #     print("col", line.distance_to(point.position))
    # direction = Vector.polar(1, line.rotation)


@LineObject.register_with(LineObject)
def collide_line_line(line1: "LineObject", line2: LineObject, time: float):
    """Nothing happens"""


class CircleObject(CompleteObject, CollidableObject):
    def __init__(self, radius: float = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.radius = radius


@CircleObject.register_with(PointObject)
def collide_circle_point(circle: CircleObject, point: PointObject, time: float):
    d_pos = circle.position - point.position
    if d_pos.r <= circle.radius:
        success, total_dt = find_zero(
            lambda a, b: (a.position - b.position).r - a.radius, circle, point, -time
        )
        if not success:
            return  # TODO: do something
        circle.tick(total_dt)
        point.tick(total_dt)

        phi = (point.position - circle.position).phi
        c1_vn, c1_vt = circle.velocity.decompose(phi)
        c2_vn, c2_vt = point.velocity.decompose(phi)
        mass = circle.mass + point.mass
        cr = min(circle.restitution, point.restitution)
        smv = circle.mass * c1_vn + point.mass * c2_vn
        c1_vnn = (cr * point.mass * (c2_vn - c1_vn) + smv) / mass
        c2_vnn = (cr * circle.mass * (c1_vn - c2_vn) + smv) / mass
        circle.velocity.replace(c1_vt + c1_vnn)
        point.velocity.replace(c2_vt + c2_vnn)

        circle.tick(-total_dt)
        point.tick(-total_dt)

        import logging

        logging.getLogger(__name__).info("Point Ball collision")


@CircleObject.register_with(LineObject)
def collide_circle_line(circle: CircleObject, line: LineObject, time: float):
    pass


@CircleObject.register_with(CircleObject)
def collide_circle_circle(c1: CircleObject, c2: CircleObject, time: float):
    if (c1.position - c2.position).r < c1.radius + c2.radius:
        success, total_dt = find_zero(
            lambda a, b: (a.position - b.position).r - a.radius - b.radius,
            c1,
            c2,
            -time,
        )
        if not success:
            return  # TODO: do something
        c1.tick(total_dt)
        c2.tick(total_dt)

        phi = (c2.position - c1.position).phi
        c1_vn, c1_vt = c1.velocity.decompose(phi)
        c2_vn, c2_vt = c2.velocity.decompose(phi)
        mass = c1.mass + c2.mass
        cr = min(c1.restitution, c2.restitution)
        smv = c1.mass * c1_vn + c2.mass * c2_vn
        c1_vnn = (cr * c2.mass * (c2_vn - c1_vn) + smv) / mass
        c2_vnn = (cr * c1.mass * (c1_vn - c2_vn) + smv) / mass
        c1.velocity.replace(c1_vt + c1_vnn)
        c2.velocity.replace(c2_vt + c2_vnn)

        c1.tick(-total_dt)
        c2.tick(-total_dt)

        import logging

        logging.getLogger(__name__).info("Ball Ball collision")


class RectangleObject(CompleteObject, CollidableObject):
    def __init__(self, width: float = 0, height: float = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.width = width
        self.height = height
