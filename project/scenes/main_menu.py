import sdl2
from gamepart.context import Context
from gamepart.gui import Panel
from gamepart.gui.button import OnClickMixin, OnHoverMixin
from gamepart.gui.text import Text

from scenes.base import MyBaseScene


class MainMenuButton(OnClickMixin, OnHoverMixin, Text):
    def _on_hover(self, event: sdl2.SDL_Event) -> None:
        super()._on_hover(event)
        self.background_color = (80, 80, 80, 255)
        self.color = (255, 255, 255, 255)

    def _on_unhover(self, event: sdl2.SDL_Event) -> None:
        super()._on_unhover(event)
        self.background_color = None
        self.color = (0, 0, 0, 255)


class MainMenuScene(MyBaseScene):
    def start(self, context: Context) -> None:
        super().start(context)
        gui = self.gui
        game = self.game
        panel = Panel(
            x=(game.width - 200) // 2,
            y=(game.height - 180) // 2,
            width=200,
            height=180,
            background_color=(40, 40, 40, 255),
        )
        start_btn = MainMenuButton(
            text="Start Game",
            font="sans",
            font_size=16,
        )
        start_btn.on_click = lambda: game.queue_scene_switch("balls")
        settings_btn = MainMenuButton(
            text="Settings",
            font="sans",
            font_size=16,
        )
        settings_btn.on_click = lambda: game.queue_scene_switch("settings")
        quit_btn = MainMenuButton(
            text="Quit",
            font="sans",
            font_size=16,
        )
        quit_btn.on_click = lambda: game.queue_scene_switch("exit")
        for btn in [start_btn, settings_btn, quit_btn]:
            panel.add_child(btn)
            btn.init_gui_system(gui)
            btn.fit_to_text()
        panel.rearrange_blocks(flow="vertical", padding=(10, 10, 10, 10), margin=20)
        panel.x = (game.width - panel.width) // 2
        panel.y = (game.height - panel.height) // 2
        gui.add(panel, start_btn, settings_btn, quit_btn)
