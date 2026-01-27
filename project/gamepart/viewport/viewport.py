import typing

from ..render import GfxRenderer
from ..subsystem import SubSystem


class ViewPort(SubSystem["GraphicalObject"]):
    __slots__ = ("renderer", "width", "height", "zoom", "x", "y")

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
        self.renderer: GfxRenderer = renderer
        self.width = width
        self.height = height
        self.zoom = zoom
        self.x = x
        self.y = y

    @staticmethod
    def accepts(obj: typing.Any) -> bool:
        return isinstance(obj, GraphicalObject)

    def draw(self) -> None:
        for obj in self.objects:
            obj.draw(self)

    def x_to_view(self, x: float) -> float:
        return (x - self.x) * self.zoom

    def y_to_view(self, y: float) -> float:
        return (y - self.y) * self.zoom

    def to_view(self, pos: tuple[float, float]) -> tuple[float, float]:
        return self.x_to_view(pos[0]), self.y_to_view(pos[1])  # TODO: inline?

    def to_view_int(self, pos: tuple[float, float]) -> tuple[int, int]:
        return int(self.x_to_view(pos[0])), int(self.y_to_view(pos[1]))  # TODO: inline?

    def d_to_view(self, d: float) -> float:
        return d * self.zoom

    def x_to_world(self, x: float) -> float:
        return (x / self.zoom) + self.x

    def y_to_world(self, y: float) -> float:
        return (y / self.zoom) + self.y

    def to_world(self, pos: tuple[float, float]) -> tuple[float, float]:
        return self.x_to_world(pos[0]), self.y_to_world(pos[1])  # TODO: inline?

    def d_to_world(self, d: float) -> float:
        return d / self.zoom

    @property
    def center(self) -> tuple[float, float]:
        return self.to_world((self.width / 2, self.height / 2))

    @center.setter
    def center(self, value: tuple[float, float]) -> None:
        cx, cy = self.center
        self.x += value[0] - cx
        self.y += value[1] - cy

    def change_zoom(
        self, change: float = 1, pos: tuple[float, float] | None = None
    ) -> None:
        if pos is None:
            pos = self.center
        self.x += (1 - 1 / change) * (pos[0] - self.x)
        self.y += (1 - 1 / change) * (pos[1] - self.y)
        self.zoom *= change

    def follow_target(
        self,
        target_position: tuple[float, float],
        delta: float,
        edge_margin: float = 0.25,
        smoothing_speed: float = 5.0,
    ) -> tuple[float, float]:
        """Smoothly move the viewport to keep target within safe zone.

        Args:
            target_position: World coordinates of the target to follow.
            delta: Time delta for smooth interpolation.
            edge_margin: Fraction of screen edge that triggers following (0.25 = 1/4).
            smoothing_speed: Camera movement speed (higher = faster response).
        """
        smoothing = 1.0 - (0.5 ** (delta * smoothing_speed))

        screen_pos = self.to_view(target_position)
        margin_x = self.width * edge_margin
        margin_y = self.height * edge_margin

        offset_x = min(0.0, screen_pos[0] - margin_x) + max(
            0.0, screen_pos[0] - (self.width - margin_x)
        )
        offset_y = min(0.0, screen_pos[1] - margin_y) + max(
            0.0, screen_pos[1] - (self.height - margin_y)
        )

        x_offset_world = self.x_to_world(screen_pos[0]) - self.x_to_world(
            screen_pos[0] - offset_x
        )
        y_offset_world = self.y_to_world(screen_pos[1]) - self.y_to_world(
            screen_pos[1] - offset_y
        )
        diff_x = x_offset_world * smoothing
        diff_y = y_offset_world * smoothing
        self.x += diff_x
        self.y += diff_y
        return diff_x, diff_y


class FlippedViewPort(ViewPort):
    def y_to_view(self, y: float) -> float:
        return self.height - (y - self.y) * self.zoom  # flip y

    def y_to_world(self, y: float) -> float:
        return ((self.height - y) / self.zoom) + self.y  # flip y


from .graphicalobject import GraphicalObject  # noqa
