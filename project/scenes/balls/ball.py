import sdl2.ext
from gamepart.physics import SimplePhysicalObject, pymunk, typed_property
from gamepart.viewport import Circle, TexturedObject, ViewPort

from .category import cat_enemy, cat_enemy_collide


class Ball(Circle, SimplePhysicalObject[pymunk.Circle]):
    color = sdl2.ext.Color(0, 255, 0)

    def __init__(
        self, radius: float = 1, mass: float = 1, position=(0, 0), velocity=(0, 0)
    ):
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
    def angle(self):
        return self.body.angle


class TexturedBall(Ball, TexturedObject):
    def __init__(
        self, *args, texture: sdl2.ext.TextureSprite, scale: float = 1.0, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.texture = texture
        self.scale = scale

    def draw(self, vp: "ViewPort"):
        Ball.draw(self, vp)
        TexturedObject.draw(self, vp)
