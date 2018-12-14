"""Simple 2D game engine built on top of PySDL2"""

from .game import Game
from .scene import Scene, ExitScene, SimpleScene


version_info = (0, 0, 1, "")
__version__ = "%d.%d.%d%s" % version_info
__author__ = "Szymon Zmilczak"

__all__ = [Game, Scene, ExitScene, SimpleScene]
