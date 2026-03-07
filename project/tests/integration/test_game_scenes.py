"""Integration test: start game, each scene 5 frames; success if nothing fails."""

import typing

import pytest
from context import MyContext
from game import MyGame

FRAMES_PER_SCENE = 5


class HeadlessGame(MyGame):
    def get_config(self) -> dict[str, typing.Any]:
        config = super().get_config()
        config["hidden"] = True
        return config


@pytest.mark.integration
def test_all_scenes_render_five_frames_each() -> None:
    import main

    main.setup()
    game = HeadlessGame()
    game.fps_display_config.display = True
    scene_names = [name for name in game.scenes if name != "exit"]
    try:
        for _ in range(FRAMES_PER_SCENE):
            game.frame()
        for name in scene_names[1:]:
            game.queue_scene_switch(name)
            for _ in range(FRAMES_PER_SCENE):
                game.frame()
                assert isinstance(game.context, MyContext)
                if game.context.console is not None:
                    game.context.console.visible = True
    finally:
        game.stop()
