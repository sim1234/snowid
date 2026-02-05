"""Tests for Panel component."""

from typing import Any

from gamepart.gui.guiobject import GUIObject
from gamepart.gui.panel import Panel


class MockChild(GUIObject):
    def __init__(self, width: int = 0, height: int = 0) -> None:
        super().__init__(width=width, height=height)
        self.draw_called = False
        self.event_called = False

    def draw(self) -> None:
        self.draw_called = True

    def event(self, event: Any) -> bool:
        self.event_called = True
        return False


class TestPanel:
    def test_initialization(self) -> None:
        panel = Panel()
        assert panel.children == []
        assert panel.background_color is None
        assert panel.x == 0
        assert panel.y == 0
        assert panel.width == 0
        assert panel.height == 0
        assert panel.parent is None

    def test_add_child(self) -> None:
        panel = Panel()
        child = MockChild()
        result = panel.add_child(child)

        assert result is child
        assert child in panel.children
        assert child.parent is panel

    def test_add_multiple_children(self) -> None:
        panel = Panel()
        child1 = MockChild()
        child2 = MockChild()

        panel.add_child(child1)
        panel.add_child(child2)

        assert len(panel.children) == 2
        assert child1.parent is panel
        assert child2.parent is panel

    def test_remove_child(self) -> None:
        panel = Panel()
        child = MockChild()
        panel.add_child(child)
        result = panel.remove_child(child)

        assert result is child
        assert child not in panel.children
        assert child.parent is None

    def test_nested_panels(self) -> None:
        parent = Panel()
        parent.x = 10
        parent.y = 20

        child_panel = Panel()
        child_panel.x = 5
        child_panel.y = 5

        parent.add_child(child_panel)

        abs_x, abs_y = child_panel.get_absolute_position()
        assert abs_x == 15
        assert abs_y == 25


class TestPanelRearrangeBlocks:
    def test_rearrange_blocks_horizontal(self) -> None:
        panel = Panel()
        child1 = MockChild(width=50, height=30)
        child2 = MockChild(width=60, height=40)
        child3 = MockChild(width=40, height=20)
        panel.add_child(child1)
        panel.add_child(child2)
        panel.add_child(child3)

        panel.rearrange_blocks(flow="horizontal")

        assert child1.x == 0
        assert child1.y == 0
        assert child2.x == 50
        assert child2.y == 0
        assert child3.x == 110
        assert child3.y == 0
        assert panel.width == 150
        assert panel.height == 40

    def test_rearrange_blocks_vertical(self) -> None:
        panel = Panel()
        child1 = MockChild(width=50, height=30)
        child2 = MockChild(width=60, height=40)
        child3 = MockChild(width=40, height=20)
        panel.add_child(child1)
        panel.add_child(child2)
        panel.add_child(child3)

        panel.rearrange_blocks(flow="vertical")

        assert child1.x == 0
        assert child1.y == 0
        assert child2.x == 0
        assert child2.y == 30
        assert child3.x == 0
        assert child3.y == 70
        assert panel.width == 60
        assert panel.height == 90

    def test_rearrange_blocks_with_margin(self) -> None:
        panel = Panel()
        child1 = MockChild(width=50, height=30)
        child2 = MockChild(width=60, height=40)
        panel.add_child(child1)
        panel.add_child(child2)

        panel.rearrange_blocks(flow="horizontal", margin=10)

        assert child1.x == 0
        assert child2.x == 60
        # width includes trailing margin: 0 + 50 + 10 + 60 + 10 = 130
        assert panel.width == 130

    def test_rearrange_blocks_with_padding(self) -> None:
        panel = Panel()
        child1 = MockChild(width=50, height=30)
        panel.add_child(child1)

        # padding = (left, top, right, bottom), but impl uses (top, left, bottom, right)
        panel.rearrange_blocks(padding=(5, 10, 15, 20), flow="horizontal")

        # x starts at padding[1]=10, y starts at padding[0]=5
        assert child1.x == 10
        assert child1.y == 5
        # width = (10 + 50) + 20 = 80
        assert panel.width == 80
        # height = max(5, 5 + 30) + 15 = 35 + 15 = 50
        assert panel.height == 50


class TestPanelRearrangeStretch:
    def test_rearrange_stretch_horizontal(self) -> None:
        panel = Panel()
        panel.width = 200
        panel.height = 100
        child1 = MockChild()
        child2 = MockChild()
        panel.add_child(child1)
        panel.add_child(child2)

        panel.rearrange_stretch(flow="horizontal")

        assert child1.x == 0
        assert child1.width == 100
        assert child1.height == 100
        assert child2.x == 100
        assert child2.width == 100
        assert child2.height == 100

    def test_rearrange_stretch_vertical(self) -> None:
        panel = Panel()
        panel.width = 200
        panel.height = 100
        child1 = MockChild()
        child2 = MockChild()
        panel.add_child(child1)
        panel.add_child(child2)

        panel.rearrange_stretch(flow="vertical")

        assert child1.y == 0
        assert child1.width == 200
        assert child1.height == 50
        assert child2.y == 50
        assert child2.width == 200
        assert child2.height == 50

    def test_rearrange_stretch_with_weights(self) -> None:
        panel = Panel()
        panel.width = 300
        panel.height = 100
        child1 = MockChild()
        child2 = MockChild()
        child3 = MockChild()
        panel.add_child(child1)
        panel.add_child(child2)
        panel.add_child(child3)

        panel.rearrange_stretch(flow="horizontal", size_weights=[1, 2, 1])

        # Total weight = 4, each unit = 75px
        assert child1.width == 75
        assert child2.width == 150
        assert child3.width == 75
