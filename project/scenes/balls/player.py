import typing

import sdl2.ext

from gamepart.physics import pymunk, PhysicalObject, CollisionObject, AwareObject
from gamepart.viewport import Polygon
from gamepart.control import Input, Controller

from .category import cat_player, cat_player_collide, cat_terrain


class PlayerStats:
    def __init__(self):
        self.air_acceleration = 300.0
        self.max_speed = 1000.0
        self.jump_speed = 1000.0
        self.ground_speed = 300.0


class Player(Polygon, CollisionObject, AwareObject):
    color = sdl2.ext.Color(0, 0, 255)

    def __init__(self, position: typing.Tuple[float, float]):
        self.stats = PlayerStats()
        body = pymunk.Body(200, pymunk.inf)
        body.position = position
        self.head = pymunk.Circle(body, 40, (0, 20))
        self.head.filter = cat_player.filter(cat_player_collide)
        self.head.friction = 0.0
        self.head.elasticity = 0.0
        self.feet = pymunk.Circle(body, 40, (0, -20))
        self.feet.filter = cat_player.filter(cat_player_collide)
        # self.feet.friction = 3.0
        self.feet.friction = 0.0
        self.feet.elasticity = 0.0
        self.last_shoot = 0.0
        self.on_ground = False
        super().__init__(body, [self.head, self.feet], cat_player)

    @property
    def points(self):
        px, py = self.position
        yield (px - 40, py + 60)
        yield (px + 40, py + 60)
        yield (px + 40, py - 60)
        yield (px - 40, py - 60)

    def tick(self, delta: float):
        self.on_ground = False

    def collide(self, arbiter: pymunk.Arbiter, other: "PhysicalObject"):
        if cat_terrain in other.category and arbiter.contact_point_set.normal.y < -0.1:
            self.on_ground = True


class PlayerInput(Input):
    __slots__ = ("left", "right", "jump", "shoot")
    default = False
    left: bool
    right: bool
    jump: bool
    shoot: bool


class PlayerController(Controller[PlayerInput, Player]):
    input_class = PlayerInput

    def act(self, game_time: float, delta: float):
        vx, vy = self.object.body.velocity
        if self.input.left:
            if self.object.on_ground:
                vx = -self.object.stats.ground_speed
            else:
                if vx > -self.object.stats.max_speed:
                    vx -= self.object.stats.air_acceleration * delta
        if self.input.right:
            if self.object.on_ground:
                vx = self.object.stats.ground_speed
            else:
                if vx < self.object.stats.max_speed:
                    vx += self.object.stats.air_acceleration * delta
        if self.input.jump and self.object.on_ground:
            vy = self.object.stats.jump_speed
        self.object.body.velocity = vx, vy
        print(delta, self.object.on_ground)
