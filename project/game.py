import os

import sdl2
import sdl2.ext

from gamepart import Game


class MyGame(Game):
    def get_config(self):
        config = super().get_config()
        config["max_fps"] = 120
        # config["fullscreen"] = True
        return config

    def init_font_manager(self):
        directory = os.path.dirname(os.path.abspath(__file__))
        self.font_manager = sdl2.ext.FontManager(
            os.path.join(directory, "resources", "PixelFJVerdana12pt.ttf")
        )

    def init_scenes(self):
        import scenes

        self.add_scene("test", scenes.TestScene)
        self.add_scene("balls", scenes.BallScene)
        super().init_scenes()
        self.queue_scene_switch("balls")
