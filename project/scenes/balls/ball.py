import sdl2.ext

from gamepart.physics import PhysicalCircle
from gamepart.viewport import ViewPort, Circle, TexturedObject


class Ball(Circle, PhysicalCircle):
    color = sdl2.ext.Color(0, 255, 0)

    @property
    def angle(self):
        return self.body.angle


class TexturedBall(Ball, TexturedObject):
    def __init__(self, *args, texture: sdl2.ext.TextureSprite, scale: float = 1.0, **kwargs):
        super(TexturedBall, self).__init__(*args, **kwargs)
        self.texture = texture
        self.scale = scale

    def draw(self, vp: "ViewPort"):
        Ball.draw(self, vp)
        TexturedObject.draw(self, vp)
