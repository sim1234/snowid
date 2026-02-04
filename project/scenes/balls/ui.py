from gamepart.gui.button import ButtonMixin
from gamepart.gui.guiobject import GUIObject
from gamepart.gui.panel import Panel
from gamepart.gui.system import GUISystem
from gamepart.gui.text import Text
from gamepart.gui.textinput import TextInput


class Button(ButtonMixin, Text):  # noqa: F821
    pass


def create_ui(gui: GUISystem) -> list[GUIObject]:
    panel = Panel(x=10, y=10, width=100, height=100)
    text_input = TextInput(
        x=10,
        y=10,
        width=200,
        height=24,
        font="sans",
        font_size=16,
        color=(0, 0, 0, 255),
    )
    text_input.color = (255, 0, 0, 255)
    text = Text(x=10, y=10, width=100, height=100, text="Hello, world!")
    button = Button(x=10, y=10, width=100, height=100, text="Click me")
    button.on_click = lambda: print("Button clicked")
    panel.add_child(text_input)
    panel.add_child(text)
    panel.add_child(button)
    panel.rearrange_blocks(flow="vertical")
    gui.add(panel, text_input, text, button)
    gui.change_focus(text_input)
    return [panel, text_input, text, button]
