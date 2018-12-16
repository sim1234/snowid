import typing

from .vector import Vector


class Object:
    def __init__(
        self,
        frozen: bool = False,
        passive: bool = False,
        __suppress_te: bool = False,
        *args,
        **kwargs,
    ):
        """Init object"""
        if (not __suppress_te) and (args or kwargs):
            raise TypeError(f"Not all arguments consumed: {args!r} {kwargs!r}")
        self.frozen = frozen
        self.passive = passive

    def tick(self, time: float):
        """Evolve forward in time"""

    def tick_frozen(self, time: float):
        """Nothing"""

    def apply(self, *args, **kwargs):
        """Apply (store) object interaction"""

    def apply_passive(self, *args, **kwargs):
        """Nothing"""

    def clear(self):
        """Clear object of any interactions"""

    def __getattribute__(self, item):
        if item == "tick" and self.frozen:
            return self.tick_frozen
        if item == "apply" and self.passive:
            return self.apply_passive
        return super().__getattribute__(item)

    def get_energy(self) -> float:
        """Calculate object energy"""
        return 0.0

    def __copy__(self):
        return self.__class__(
            **{
                k: (v.copy() if isinstance(v, Vector) else v)
                for k, v in self.__dict__.items()
            }
        )


class PositedObject(Object):
    def __init__(self, position: Vector = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position = Vector.to(position)  # m


class MovingObject(PositedObject):
    def __init__(self, velocity: Vector = None, mass: float = 1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.velocity = Vector.to(velocity)  # m/s
        self.mass = mass  # kg
        self.force = Vector()  # N (kg*m/s^2)

    def tick(self, time: float):
        super().tick(time)
        acceleration = self.force * self.mass
        self.position += self.velocity * time + acceleration * (time ** 2 / 2)
        self.velocity += acceleration * time

    def apply(self, force: Vector, *args, **kwargs):
        super().apply(*args, **kwargs)
        self.force += force

    def clear(self):
        super().clear()
        self.force.update()

    def get_energy(self) -> float:
        e = super().get_energy()
        return e + (self.mass * self.velocity.r ** 2) / 2


class RotatedObject(Object):
    def __init__(self, rotation: float = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rotation = rotation  # rad (m/m)

    @property
    def rotation_unit(self):
        return Vector.polar(1, self.rotation)


class RotatingObject(RotatedObject):
    def __init__(
        self, angular_velocity: float = 0, inertia: float = 1, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.angular_velocity = angular_velocity  # rad/s ((m/m)/s)
        self.inertia = inertia  # kg*m^2
        self.torque = 0.0  # N*m (kg*m^2/s^2)

    def tick(self, time: float):
        super().tick(time)
        acceleration = self.torque * self.inertia
        self.rotation += self.angular_velocity * time + acceleration * (time ** 2 / 2)
        self.angular_velocity += acceleration * time

    def apply(self, torque: float, *args, **kwargs):
        super().apply(*args, **kwargs)
        self.torque += torque

    def clear(self):
        super().clear()
        self.torque = 0.0

    def get_energy(self) -> float:
        e = super().get_energy()
        return e + (self.inertia * self.angular_velocity ** 2) / 2


class CompleteObject(MovingObject, RotatingObject):
    def get_force_torque(
        self, apply_point: Vector, force: Vector
    ) -> typing.Tuple[Vector, float]:
        point = apply_point - self.position
        pure_force, torque_force = force.decompose(point.phi)
        return pure_force, torque_force.r * point.r
