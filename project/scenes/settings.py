import typing

import sdl2
from context import MyContext
from gamepart.context import Context
from gamepart.gui import Panel
from gamepart.gui.button import OnClickMixin, OnHoverMixin
from gamepart.gui.text import Text
from settings import KeyBinds, load_key_binds, save_key_binds

from scenes.base import MyBaseScene


def _key_sym_to_name(key_sym: int) -> str:
    key_name_bytes = sdl2.SDL_GetKeyName(key_sym)
    if key_name_bytes:
        return key_name_bytes.decode("utf-8", errors="replace")
    return str(key_sym)


ACTION_LABELS: dict[str, str] = {
    "jump": "Jump",
    "move_left": "Move left",
    "move_right": "Move right",
    "shoot": "Shoot",
    "console": "Console",
    "toggle_fps": "Toggle FPS",
    "switch_scene": "Switch scene",
}


class SettingsButton(OnClickMixin, OnHoverMixin, Text):
    def _on_hover(self, event: sdl2.SDL_Event) -> None:
        super()._on_hover(event)
        self.background_color = (80, 80, 80, 255)
        self.color = (255, 255, 255, 255)

    def _on_unhover(self, event: sdl2.SDL_Event) -> None:
        super()._on_unhover(event)
        self.background_color = None
        self.color = (0, 0, 0, 255)


class SettingsRow(OnClickMixin, OnHoverMixin, Panel):
    def _on_hover(self, event: sdl2.SDL_Event) -> None:
        super()._on_hover(event)
        self.background_color = (80, 80, 80, 255)

    def _on_unhover(self, event: sdl2.SDL_Event) -> None:
        super()._on_unhover(event)
        self.background_color = None


class SettingsScene(MyBaseScene):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.pending_key_binds: dict[str, int] = {}
        self.listening_for_action: str | None = None
        self._key_label_widgets: dict[str, Text] = {}

    def start(self, context: Context) -> None:
        super().start(context)
        if isinstance(context, MyContext):
            self.pending_key_binds = dict(context.key_binds.to_dict())
        else:
            self.pending_key_binds = dict(load_key_binds().to_dict())
        self.listening_for_action = None
        self._key_label_widgets = {}
        gui = self.gui

        panel = Panel(
            width=400,
            height=400,
            background_color=(40, 40, 40, 255),
        )
        for action in KeyBinds.ACTION_ORDER:
            row = SettingsRow(x=0, y=0, width=380, height=36)
            row.on_click = self._make_change_callback(action)
            label_text = Text(
                x=0,
                y=0,
                width=140,
                height=28,
                text=ACTION_LABELS.get(action, action),
                font="sans",
                font_size=14,
            )
            key_text = Text(
                x=0,
                y=0,
                width=120,
                height=28,
                text=_key_sym_to_name(self.pending_key_binds[action]),
                font="sans",
                font_size=14,
            )
            self._key_label_widgets[action] = key_text
            row.add_child(label_text)
            row.add_child(key_text)
            row.rearrange_blocks(flow="horizontal", padding=(4, 4, 4, 4), margin=4)
            panel.add_child(row)

        save_btn = SettingsButton(
            width=120,
            height=36,
            text="Save",
            font="sans",
            font_size=16,
        )
        save_btn.on_click = self._save
        discard_btn = SettingsButton(
            width=120,
            height=36,
            text="Discard",
            font="sans",
            font_size=16,
        )
        discard_btn.on_click = self._discard
        panel.add_child(save_btn)
        panel.add_child(discard_btn)
        panel.rearrange_blocks(flow="vertical", padding=(10, 10, 10, 10), margin=6)
        panel.x = (self.game.width - panel.width) // 2
        panel.y = (self.game.height - panel.height) // 2

        to_add: list[typing.Any] = [panel]
        for child in panel.children:
            to_add.append(child)
            if hasattr(child, "children") and child.children:
                to_add.extend(child.children)
        gui.add(*to_add)

    def _make_change_callback(self, action: str):
        def callback() -> None:
            self.listening_for_action = action
            if action in self._key_label_widgets:
                self._key_label_widgets[action].text = (
                    "Press a key... (Escape to cancel)"
                )

        return callback

    def _save(self) -> None:
        save_key_binds(self.pending_key_binds)
        if isinstance(self.context, MyContext):
            self.context.key_binds.update_from_dict(self.pending_key_binds)
        self.game.queue_scene_switch("main_menu")

    def _discard(self) -> None:
        self.game.queue_scene_switch("main_menu")

    def event(self, event: sdl2.SDL_Event) -> None:
        if self.listening_for_action is not None:
            if event.type == sdl2.SDL_KEYDOWN:
                sym = event.key.keysym.sym
                if sym == sdl2.SDLK_ESCAPE:
                    action = self.listening_for_action
                    self.listening_for_action = None
                    if action in self._key_label_widgets:
                        self._key_label_widgets[action].text = _key_sym_to_name(
                            self.pending_key_binds[action]
                        )
                else:
                    action = self.listening_for_action
                    self.pending_key_binds[action] = sym
                    if action in self._key_label_widgets:
                        self._key_label_widgets[action].text = _key_sym_to_name(sym)
                    self.listening_for_action = None
                return
        super().event(event)
