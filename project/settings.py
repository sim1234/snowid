import json
import os
from dataclasses import dataclass
from typing import Any, ClassVar

import sdl2


@dataclass
class KeyBinds:
    jump: int = sdl2.SDLK_w
    move_left: int = sdl2.SDLK_a
    move_right: int = sdl2.SDLK_d
    shoot: int = sdl2.SDLK_e
    console: int = sdl2.SDLK_F1
    toggle_fps: int = sdl2.SDLK_F3
    switch_scene: int = sdl2.SDLK_F2

    ACTION_ORDER: ClassVar[list[str]] = [
        "jump",
        "move_left",
        "move_right",
        "shoot",
        "console",
        "toggle_fps",
        "switch_scene",
    ]

    def get(self, action: str) -> int:
        return getattr(self, action, 0)

    def to_dict(self) -> dict[str, int]:
        return {action: getattr(self, action) for action in self.ACTION_ORDER}

    def update_from_dict(self, data: dict[str, int]) -> None:
        for action in self.ACTION_ORDER:
            if action in data:
                setattr(self, action, data[action])


def _config_path() -> str:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, "key_binds.json")


def load_key_binds(path: str | None = None) -> KeyBinds:
    filepath = path or _config_path()
    if not os.path.isfile(filepath):
        return KeyBinds()
    try:
        with open(filepath, encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)
    except (OSError, json.JSONDecodeError):
        return KeyBinds()
    result: dict[str, int] = {}
    for action, value in data.items():
        if action in KeyBinds.ACTION_ORDER and isinstance(value, int):
            result[action] = value
    defaults = KeyBinds()
    for action in KeyBinds.ACTION_ORDER:
        if action not in result:
            result[action] = getattr(defaults, action)
    return KeyBinds(**result)


def save_key_binds(
    key_binds: KeyBinds | dict[str, int], path: str | None = None
) -> None:
    binds = key_binds.to_dict() if isinstance(key_binds, KeyBinds) else key_binds
    filepath = path or _config_path()
    dirpath = os.path.dirname(filepath)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(binds, f, indent=2)
