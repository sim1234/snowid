import pymunk

from .object import Object, SimpleObject


class Circle(SimpleObject):
    def __init__(
        self, radius: float = 1, mass: float = 1, position=(0, 0), velocity=(0, 0)
    ):
        body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius))
        body.position = position
        body.velocity = velocity
        shape = pymunk.Circle(body, radius)
        shape.elasticity = 1.0
        shape.friction = 0.0
        super().__init__(body, shape)

    @property
    def radius(self):
        return self.shape.radius
