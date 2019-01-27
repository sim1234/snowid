import typing

import sdl2.ext

from gamepart.physics import pymunk, PhysicalObject, CollisionObject, AwareObject
from gamepart.viewport import Polygon
from gamepart.control import Input, Controller

from .category import cat_player, cat_player_collide, cat_terrain


class PlayerState:
    def __init__(self):
        # Dynamic
        self.position: typing.Tuple[float, float] = (0.0, 0.0)
        # State
        self.jumps: int = 0
        self.last_shoot: float = 0.0
        # Stats
        self.mass: float = 200.0
        self.air_acceleration: float = 300.0
        self.jump_speed: float = 1000.0
        self.ground_speed: float = 300.0
        self.max_jumps: int = 2


class Player(Polygon, CollisionObject, AwareObject):
    color = sdl2.ext.Color(0, 0, 255)

    def __init__(self, position: typing.Tuple[float, float]):
        self.state = PlayerState()
        body = pymunk.Body(self.state.mass, pymunk.inf)
        body.position = position
        self.head = pymunk.Circle(body, 40, (0, 20))
        self.head.filter = cat_player.filter(cat_player_collide)
        self.head.friction = 0.0
        self.head.elasticity = 0.0
        self.feet = pymunk.Circle(body, 10, (0, -50))
        self.feet.filter = cat_player.filter(cat_player_collide)
        self.feet.friction = 10.0
        self.feet.elasticity = 0.0
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
        mass = self.object.body.mass
        feet_vx: float = 0
        feet_vy: float = 0
        impulse_x: float = 0
        impulse_y: float = 0
        if self.object.on_ground:
            self.object.state.jumps = 0
        if self.input.left and not self.input.right:  # go left
            if self.object.on_ground:
                feet_vx += self.object.state.ground_speed
            else:
                impulse_x -= self.object.state.air_acceleration * delta
        elif self.input.right and not self.input.left:  # go right
            if self.object.on_ground:
                feet_vx -= self.object.state.ground_speed
            else:
                impulse_x += self.object.state.air_acceleration * delta
        if self.input.jump:  # jump
            if self.object.state.jumps < self.object.state.max_jumps:
                self.object.state.jumps += 1
                impulse_y += self.object.state.jump_speed

        self.object.feet.surface_velocity = (feet_vx, feet_vy)
        self.object.body.apply_impulse_at_local_point(
            (impulse_x * mass, impulse_y * mass)
        )
