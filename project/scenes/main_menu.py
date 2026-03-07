from gamepart.context import Context
from gamepart.gui import Panel
from gamepart.gui.button import PrettyButton
from gamepart.gui.text import Text

from scenes.base import MyBaseScene


class MainMenuScene(MyBaseScene):
    def _make_button(self, text: str, scene: str) -> PrettyButton:
        return PrettyButton(
            text=Text(
                x=10,
                y=10,
                text=text,
                font="sans",
                font_size=16,
                color=(0, 0, 0, 255),
                background_color=None,
            ),
            hover_color=(255, 255, 255, 255),
            hover_background_color=(80, 80, 80, 255),
            on_click=lambda: self.game.queue_scene_switch(scene),
        )

    def start(self, context: Context) -> None:
        super().start(context)
        panel = Panel(
            background_color=(40, 40, 40, 255),
        )
        self.gui.add(panel)
        start_btn = self._make_button("Start game", "balls")
        start_game_2_btn = self._make_button("Start game 2", "balls")
        start_test_btn = self._make_button("Start test", "test")
        settings_btn = self._make_button("Settings", "settings")
        quit_btn = self._make_button("Quit", "exit")
        buttons = [
            start_btn,
            start_game_2_btn,
            start_test_btn,
            settings_btn,
            quit_btn,
        ]
        for btn in buttons:
            panel.add_child(btn)
            btn.fit_to_text(padding=(10, 50, 10, 50))
        panel.rearrange_blocks(flow="vertical", padding=(10, 10, 10, 10), margin=20)
        panel.x = (self.game.width - panel.width) // 2
        panel.y = (self.game.height - panel.height) // 2
        for btn in buttons:
            btn.width = panel.width - 20
            btn.text.x = btn.width // 2 - btn.text.width // 2
