import math
import typing

VectorLike = typing.Union["Vector", tuple[typing.SupportsFloat, typing.SupportsFloat]]


class Vector:
    """2D vector"""

    __slots__ = ("x", "y")

    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    @classmethod
    def to(cls, *args) -> "Vector":
        """Create Vector fom arbitrary data"""
        if not args or args[0] is None:
            return cls()
        if len(args) == 1:  # Vector, tuple, list
            args = args[0]
        return cls(args[0], args[1])

    @classmethod
    def polar(cls, r: float, phi: float) -> "Vector":
        """Create vector from polar data"""
        v = cls(r)
        v.phi = phi
        return v

    def copy(self) -> "Vector":
        return self.__class__(self.x, self.y)

    def update(self, x: float = 0, y: float = 0) -> "Vector":
        self.x = x
        self.y = y
        return self

    def replace(self, other: VectorLike) -> "Vector":
        self.x = float(other[0])
        self.y = float(other[1])
        return self

    def __getitem__(self, item: int) -> float:
        if item == 0:
            return self.x
        if item == 1:
            return self.y
        raise IndexError(f"Index {item} out of range for Vector")

    def __setitem__(self, key: int, value: float) -> None:
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise IndexError(f"Index {key} out of range for Vector")

    def __add__(self, other: VectorLike) -> "Vector":
        return self.__class__(self.x + float(other[0]), self.y + float(other[1]))

    def __iadd__(self, other: VectorLike) -> "Vector":
        self.x += float(other[0])
        self.y += float(other[1])
        return self

    __radd__ = __add__

    def __sub__(self, other: VectorLike) -> "Vector":
        return self.__class__(self.x - float(other[0]), self.y - float(other[1]))

    def __isub__(self, other: VectorLike) -> "Vector":
        self.x -= float(other[0])
        self.y -= float(other[1])
        return self

    def __rsub__(self, other: VectorLike) -> "Vector":
        return self.__class__(float(other[0]) - self.x, float(other[1]) - self.y)

    def __mul__(self, other: float) -> "Vector":
        return self.__class__(self.x * other, self.y * other)

    def __imul__(self, other: float) -> "Vector":
        self.x *= other
        self.y *= other
        return self

    __rmul__ = __mul__

    def __truediv__(self, other: float) -> "Vector":
        return self.__class__(self.x / other, self.y / other)

    def __itruediv__(self, other: float) -> "Vector":
        self.x /= other
        self.y /= other
        return self

    def __matmul__(self, other: VectorLike) -> float:
        """Dot product"""
        return self.x * float(other[0]) + self.y * float(other[1])

    def __pos__(self):
        return self.copy()

    def __neg__(self) -> "Vector":
        return self.__class__(-self.x, -self.y)

    def __invert__(self) -> "Vector":
        return self.__class__(self.y, self.x)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (tuple, list)) and len(other) == 2:
            return self.x == float(other[0]) and self.y == float(other[1])
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __bool__(self) -> bool:
        return bool(self.x and self.y)

    def __len__(self) -> int:
        return 2

    @property
    def r(self) -> float:
        return math.hypot(self.x, self.y)

    @r.setter
    def r(self, value: float):
        phi = self.phi
        self.x = value * math.cos(phi)
        self.y = value * math.sin(phi)

    @property
    def phi(self) -> float:
        return math.atan2(self.y, self.x)

    @phi.setter
    def phi(self, value: float):
        r = self.r
        self.x = r * math.cos(value)
        self.y = r * math.sin(value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.x!r}, {self.y!r})"

    def __complex__(self) -> complex:
        return complex(self.x, self.y)

    def __iter__(self) -> typing.Generator[float, None, None]:
        yield self.x
        yield self.y

    def cross(self, other: VectorLike) -> float:
        """Pseudo cross product"""
        other = self.to(other)
        return self.r * other.r * math.sin(self.phi - other.phi)

    def decompose(self, phi: float) -> tuple["Vector", "Vector"]:
        """Decompose vector into orthogonal vectors, first with angle phi"""
        n = self.polar(1, phi)
        parallel = n * (self @ n)
        orthogonal = self - parallel
        return parallel, orthogonal

    def normal(self) -> "Vector":
        """Get normal of this vector"""
        r = self.r
        return self.__class__(self.x / r, self.y / r)

    def tangent(self) -> "Vector":
        """Get vector rotated by 90 degrees counterclockwise"""
        return self.__class__(-self.y, self.x)
