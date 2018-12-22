import typing

from ..subsystem import SubSystem
from ..render import GfxRenderer


class ViewPort(SubSystem["GraphicalObject"]):
    def __init__(
        self,
        renderer: GfxRenderer,
        width: int,
        height: int,
        zoom: float = 1,
        x: float = 0,
        y: float = 0,
    ):
        super().__init__()
        self.renderer = renderer
        self.width = width
        self.height = height
        self.zoom = zoom
        self.x = x
        self.y = y

    def draw(self):
        for obj in self.objects:
            obj.draw(self)

    def x_to_view(self, x: float) -> float:
        return (x - self.x) * self.zoom

    def y_to_view(self, y: float) -> float:
        return self.height - (y - self.y) * self.zoom

    def to_view(self, pos: typing.Tuple[float, float]) -> typing.Tuple[float, float]:
        return self.x_to_view(pos[0]), self.y_to_view(pos[1])

    def x_to_world(self, x: float) -> float:
        return (x / self.zoom) + self.x

    def y_to_world(self, y: float) -> float:
        return (y / self.zoom) + self.y

    def to_world(self, pos: typing.Tuple[float, float]) -> typing.Tuple[float, float]:
        return self.x_to_world(pos[0]), self.y_to_world(pos[1])


class FlippedViewPort(ViewPort):
    def y_to_view(self, y: float) -> float:
        return self.height - (y - self.y) * self.zoom  # flip y

    def y_to_world(self, y: float) -> float:
        return ((self.height - y) / self.zoom) + self.y  # flip y


from .graphicalobject import GraphicalObject  # noqa
