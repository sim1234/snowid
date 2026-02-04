import os
import typing

from context import MyContext
from gamepart import Game
from gamepart.font_manager import AdvancedFontManager

ROOT = os.path.dirname(os.path.abspath(__file__))
RESOURCES = os.path.join(ROOT, "resources")


class MyGame(Game):
    context_class = MyContext

    def get_config(self) -> dict[str, typing.Any]:
        config = super().get_config()
        config["max_fps"] = 120
        # config["fullscreen"] = True
        return config

    def init_font_manager(self) -> None:
        self.font_manager = AdvancedFontManager(
            os.path.join(RESOURCES, "PixelFJVerdana12pt.ttf")
        )

    def init_heavy(self) -> None:
        if self.font_manager is None:
            return
        self.font_manager.add(os.path.join(RESOURCES, "Hack-Regular.ttf"), "console")
        self.font_manager.add(os.path.join(RESOURCES, "OpenSans-Regular.ttf"), "sans")

    def init_scenes(self) -> None:
        import scenes

        self.add_scene("test", scenes.TestScene)
        self.add_scene("balls", scenes.BallScene)
        super().init_scenes()
        self.queue_scene_switch("balls")
