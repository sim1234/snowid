from collections.abc import Callable
from typing import Any

from gamepart.gui.button import PrettyButton
from gamepart.gui.panel import Panel
from gamepart.gui.system import GUISystem
from gamepart.gui.text import Text

from .upgrades import UpgradeDef


def create_resource_panel(
    gui: GUISystem,
    panel_width: int,
) -> tuple[Panel, Text, Text, Text, Text, Text, Text]:
    panel = Panel(
        width=panel_width,
        background_color=(50, 50, 55, 255),
    )
    gui.add(panel)
    iron_text = Text(
        width=panel_width - 20,
        height=24,
        text="Iron: 0",
        font="sans",
        font_size=16,
        color=(220, 220, 220, 255),
    )
    iron_per_sec_text = Text(
        width=panel_width - 20,
        height=20,
        text="Iron/s: 0",
        font="sans",
        font_size=14,
        color=(180, 180, 180, 255),
    )
    copper_text = Text(
        width=panel_width - 20,
        height=24,
        text="Copper: 0",
        font="sans",
        font_size=16,
        color=(220, 220, 220, 255),
    )
    copper_per_sec_text = Text(
        width=panel_width - 20,
        height=20,
        text="Copper/s: 0",
        font="sans",
        font_size=14,
        color=(180, 180, 180, 255),
    )
    coal_text = Text(
        width=panel_width - 20,
        height=24,
        text="Coal: 0",
        font="sans",
        font_size=16,
        color=(220, 220, 220, 255),
    )
    coal_per_sec_text = Text(
        width=panel_width - 20,
        height=20,
        text="Coal/s: 0",
        font="sans",
        font_size=14,
        color=(180, 180, 180, 255),
    )
    panel.add_child(iron_text)
    panel.add_child(iron_per_sec_text)
    panel.add_child(copper_text)
    panel.add_child(copper_per_sec_text)
    panel.add_child(coal_text)
    panel.add_child(coal_per_sec_text)
    panel.rearrange_blocks(flow="vertical", padding=(10, 10, 10, 10), margin=8)
    return (
        panel,
        iron_text,
        iron_per_sec_text,
        copper_text,
        copper_per_sec_text,
        coal_text,
        coal_per_sec_text,
    )


TOOL_BAR_BUTTON_SIZE = 44
TOOL_BAR_MARGIN = 8
TOOL_BAR_SELECTED_COLOR = (70, 90, 120, 255)
TOOL_BAR_NORMAL_COLOR = (50, 50, 55, 255)


class ToolSlotButton(PrettyButton):
    tool: str | None

    def __init__(self, tool: str | None, **kwargs: Any) -> None:
        self.tool = tool
        super().__init__(**kwargs)


def create_tool_bar(
    gui: GUISystem,
    game_width: int,
    game_height: int,
    slot_tools: list[str | None],
    on_toggle_tool: Callable[[str | None], None],
) -> tuple[Panel, list[ToolSlotButton]]:
    panel = Panel(
        width=len(slot_tools) * TOOL_BAR_BUTTON_SIZE
        + (len(slot_tools) - 1) * TOOL_BAR_MARGIN
        + 2 * TOOL_BAR_MARGIN,
        height=TOOL_BAR_BUTTON_SIZE + 2 * TOOL_BAR_MARGIN,
        background_color=TOOL_BAR_NORMAL_COLOR,
    )
    panel.x = (game_width - panel.width) // 2
    panel.y = game_height - panel.height - TOOL_BAR_MARGIN
    gui.add(panel)
    buttons: list[ToolSlotButton] = []
    labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    for i, tool in enumerate(slot_tools):
        label = labels[i]
        text = Text(
            width=TOOL_BAR_BUTTON_SIZE - 4,
            height=TOOL_BAR_BUTTON_SIZE - 4,
            text=label,
            font="sans",
            font_size=16,
            color=(220, 220, 220, 255),
            background_color=TOOL_BAR_NORMAL_COLOR,
        )
        btn = ToolSlotButton(
            tool,
            width=TOOL_BAR_BUTTON_SIZE,
            height=TOOL_BAR_BUTTON_SIZE,
            text=text,
            background_color=TOOL_BAR_NORMAL_COLOR,
            hover_background_color=(60, 60, 65, 255),
            on_click=lambda t=tool: on_toggle_tool(t),
        )
        panel.add_child(btn)
        buttons.append(btn)
    panel.rearrange_blocks(
        flow="horizontal",
        padding=(TOOL_BAR_MARGIN, TOOL_BAR_MARGIN, TOOL_BAR_MARGIN, TOOL_BAR_MARGIN),
        margin=TOOL_BAR_MARGIN,
    )
    return panel, buttons


UPGRADE_PANEL_WIDTH = 220


def create_upgrade_panel(
    gui: GUISystem,
    x: int,
    y: int,
    upgrades: list[UpgradeDef],
    get_level: Callable[[str], int],
    on_upgrade_click: Callable[[str], None],
) -> tuple[Panel, list[tuple[Text, Text, PrettyButton]]]:
    row_height = 28
    panel = Panel(
        x=x,
        y=y,
        width=UPGRADE_PANEL_WIDTH,
        height=len(upgrades) * row_height + 50,
        background_color=(50, 50, 55, 255),
    )
    gui.add(panel)
    title = Text(
        width=UPGRADE_PANEL_WIDTH - 20,
        height=22,
        text="Upgrades",
        font="sans",
        font_size=16,
        color=(220, 220, 220, 255),
    )
    panel.add_child(title)
    rows: list[tuple[Text, Text, PrettyButton]] = []
    for upgrade in upgrades:
        row_panel = Panel(width=UPGRADE_PANEL_WIDTH - 20, height=row_height)
        level_text = Text(
            width=60,
            height=20,
            text="Lv 0",
            font="sans",
            font_size=14,
            color=(200, 200, 200, 255),
        )
        cost_text = Text(
            width=100,
            height=20,
            text="",
            font="sans",
            font_size=14,
            color=(160, 160, 160, 255),
        )
        btn_text = Text(
            width=50,
            height=20,
            text="Upgrade",
            font="sans",
            font_size=14,
            color=(220, 220, 220, 255),
            background_color=(60, 70, 90, 255),
        )
        btn = PrettyButton(
            width=60,
            height=22,
            text=btn_text,
            background_color=(60, 70, 90, 255),
            hover_background_color=(70, 80, 100, 255),
            on_click=lambda u=upgrade: on_upgrade_click(u.id),
        )
        row_panel.add_child(level_text)
        row_panel.add_child(cost_text)
        row_panel.add_child(btn)
        row_panel.rearrange_blocks(flow="horizontal", padding=(0, 0, 0, 0), margin=4)
        panel.add_child(row_panel)
        rows.append((level_text, cost_text, btn))
    panel.rearrange_blocks(
        flow="vertical",
        padding=(10, 10, 10, 10),
        margin=4,
    )
    return panel, rows
