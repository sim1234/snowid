from gamepart.gui.button import ButtonMixin
from gamepart.gui.guiobject import GUIObject
from gamepart.gui.panel import Panel
from gamepart.gui.paragraph import Paragraph, ScrollableParagraph
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
    paragraph = Paragraph(
        x=10,
        y=10,
        width=100,
        height=100,
        text="Welcome to the game!\nBy Sim1234\n&AI",
        line_spacing=10,
    )
    scrollable_paragraph = ScrollableParagraph(
        x=10,
        y=10,
        width=200,
        height=80,
        text="\n".join(f"Line {i}: Scrollable content here" for i in range(20)),
        line_spacing=4,
        scroll_speed=20,
        smooth_scroll_factor=0.2,
    )
    panel.add_child(text_input)
    panel.add_child(text)
    panel.add_child(button)
    panel.add_child(paragraph)
    panel.add_child(scrollable_paragraph)
    panel.rearrange_blocks(flow="vertical")
    gui.add(panel, text_input, text, button, paragraph, scrollable_paragraph)
    gui.change_focus(text_input)
    return [panel, text_input, text, button, paragraph, scrollable_paragraph]
