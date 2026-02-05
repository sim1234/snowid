from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from .guiobject import GUIObject


class Panel(GUIObject):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        background_color: tuple[int, int, int, int] | None = None,
    ) -> None:
        super().__init__(x=x, y=y, width=width, height=height)
        self.children: list[GUIObject] = []
        self.background_color: tuple[int, int, int, int] | None = background_color

    def add_child(self, child: GUIObject) -> GUIObject:
        child.parent = self
        self.children.append(child)
        return child

    def remove_child(self, child: GUIObject) -> GUIObject:
        child.parent = None
        self.children.remove(child)
        return child

    def draw(self) -> None:
        if self.background_color:
            x, y = self.get_absolute_position()
            self.gui_system.renderer.fill(
                [(x, y, self.width, self.height)], self.background_color
            )

    def rearrange_blocks(
        self,
        padding: tuple[int, int, int, int] = (0, 0, 0, 0),
        margin: int = 0,
        flow: Literal["horizontal"] | Literal["vertical"] = "horizontal",
    ) -> None:
        """Rearrange the children and treat them as blocks.
        Keeps chlidren size, but changes their position and self size.
        padding: (left, top, right, bottom)
        margin: margin between blocks
        flow: "horizontal" or "vertical" (direction of the blocks)
        """
        x = padding[1]
        y = padding[0]
        max_x = x
        max_y = y
        for child in self.children:
            child.x = x
            child.y = y
            if flow == "horizontal":
                x += child.width + margin
                max_x = x
                max_y = max(max_y, y + child.height)
            elif flow == "vertical":
                y += child.height + margin
                max_x = max(max_x, x + child.width)
                max_y = y

        self.width = max_x + padding[3]
        self.height = max_y + padding[2]

    def rearrange_stretch(
        self,
        padding: tuple[int, int, int, int] = (0, 0, 0, 0),
        margin: int = 0,
        flow: Literal["horizontal"] | Literal["vertical"] = "horizontal",
        size_weights: Iterable[float] = (),
    ) -> None:
        """Rearrange the children and stretch them to fill the panel.
        Keeps self size, and changes children position and size.
        padding: (left, top, right, bottom)
        margin: margin between blocks
        flow: "horizontal" or "vertical" (direction of the blocks)
        """
        children_num = len(self.children)
        weights_map = {i: weight for i, weight in enumerate(size_weights)}
        child_weights = [weights_map.get(i, 1.0) for i in range(children_num)]
        total_weight = sum(child_weights)
        available_width = (
            self.width - padding[1] - padding[3] - margin * (children_num - 1)
        )
        available_height = (
            self.height - padding[0] - padding[2] - margin * (children_num - 1)
        )
        if flow == "horizontal":
            child_width = int(available_width / total_weight)
            child_height = available_height
        elif flow == "vertical":
            child_width = available_width
            child_height = int(available_height / total_weight)
        x = padding[1]
        y = padding[0]
        for weight, child in zip(child_weights, self.children):
            child.x = x
            child.y = y
            if flow == "horizontal":
                child.width = round(child_width * weight)
                child.height = child_height
                x += child_width + margin
            elif flow == "vertical":
                child.width = child_width
                child.height = round(child_height * weight)
                y += child_height + margin
