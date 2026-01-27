"""Simple 2D game engine built on top of PySDL2"""

from .game import Game
from .scene import ExitScene, Scene, SimpleScene

version_info = (0, 0, 2, "")
__version__ = f"{version_info[0]}.{version_info[1]}.{version_info[2]}{version_info[3]}"
__author__ = "Szymon Zmilczak"

__all__ = ["Game", "Scene", "ExitScene", "SimpleScene"]
