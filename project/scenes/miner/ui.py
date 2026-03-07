from gamepart.gui.panel import Panel
from gamepart.gui.system import GUISystem
from gamepart.gui.text import Text


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
