import typing
from collections.abc import Callable

import sdl2
from context import MyContext
from gamepart.context import Context
from gamepart.gui import Panel
from gamepart.gui.button import OnClickMixin, OnHoverMixin, PrettyButton
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
        gui.add(panel)
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
        sub_panel = Panel(
            width=panel.width,
        )
        panel.add_child(sub_panel)

        save_btn = PrettyButton(
            text=Text(
                text="Save",
                font="sans",
                font_size=14,
                color=(0, 80, 0, 255),
                background_color=None,
            ),
            hover_color=(255, 255, 255, 255),
            hover_background_color=(80, 120, 80, 255),
            on_click=self._save,
        )
        discard_btn = PrettyButton(
            text=Text(
                text="Discard",
                font="sans",
                font_size=14,
                color=(80, 0, 0, 255),
                background_color=None,
            ),
            hover_color=(255, 255, 255, 255),
            hover_background_color=(120, 80, 80, 255),
            on_click=self._discard,
        )
        for btn in [save_btn, discard_btn]:
            sub_panel.add_child(btn)
            btn.fit_to_text(padding=(10, 50, 10, 50))
        sub_panel.rearrange_blocks(flow="horizontal", margin=10)
        panel.rearrange_blocks(flow="vertical", padding=(10, 10, 10, 10), margin=6)
        panel.x = (self.game.width - panel.width) // 2
        panel.y = (self.game.height - panel.height) // 2

        self.keyboard_event.on_up(
            sdl2.SDLK_ESCAPE, lambda e: self.game.queue_scene_switch("main_menu")
        )

    def _make_change_callback(self, action: str) -> Callable[[], None]:
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
