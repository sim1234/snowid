import typing

import sdl2.ext
from gamepart.physics import SimplePhysicalObject, pymunk, typed_property
from gamepart.viewport import Circle, TexturedObject, ViewPort

from .category import cat_enemy, cat_enemy_collide


class Ball(Circle, SimplePhysicalObject[pymunk.Circle]):
    color = sdl2.ext.Color(0, 255, 0)

    def __init__(
        self,
        radius: float = 1,
        mass: float = 1,
        position: tuple[float, float] = (0, 0),
        velocity: tuple[float, float] = (0, 0),
    ) -> None:
        body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius))
        body.position = position
        body.velocity = velocity
        shape = pymunk.Circle(body, radius)
        shape.filter = cat_enemy.filter(cat_enemy_collide)
        shape.elasticity = 0.9
        shape.friction = 0.01
        super().__init__(body, shape, cat_enemy)

    @typed_property(float)
    def radius(self) -> float:
        return self.shape.radius

    @property
    def angle(self) -> float:
        if self.body is None:
            return 0.0
        return self.body.angle

    @angle.setter
    def angle(self, value: float) -> None:
        raise NotImplementedError()


class TexturedBall(Ball, TexturedObject):
    def __init__(
        self,
        *args: typing.Any,
        texture: sdl2.ext.TextureSprite,
        scale: float = 1.0,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.texture = texture
        self.scale = scale

    def draw(self, vp: "ViewPort") -> None:
        Ball.draw(self, vp)
        TexturedObject.draw(self, vp)
