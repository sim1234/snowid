import os

import sdl2
import sdl2.ext
from context import MyContext
from gamepart import Game

ROOT = os.path.dirname(os.path.abspath(__file__))
RESOURCES = os.path.join(ROOT, "resources")


class MyGame(Game):
    context_class = MyContext

    def get_config(self):
        config = super().get_config()
        config["max_fps"] = 120
        # config["fullscreen"] = True
        return config

    def init_font_manager(self):
        self.font_manager = sdl2.ext.FontManager(
            os.path.join(RESOURCES, "PixelFJVerdana12pt.ttf")
        )

    def init_heavy(self):
        self.font_manager.add(os.path.join(RESOURCES, "Hack-Regular.ttf"), "console")

    def init_scenes(self):
        import scenes

        self.add_scene("test", scenes.TestScene)
        self.add_scene("balls", scenes.BallScene)
        super().init_scenes()
        self.queue_scene_switch("balls")
