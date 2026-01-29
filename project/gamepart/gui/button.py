from __future__ import annotations

from collections.abc import Callable
from typing import Any

import sdl2


class ButtonMixin:
    def __init__(
        self,
        *args: Any,
        on_click: Callable[[], None] | None = None,
        event_type: int = sdl2.SDL_MOUSEBUTTONUP,
        event_button: int = sdl2.SDL_BUTTON_LEFT,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.on_click: Callable[[], None] | None = on_click
        self.event_type = event_type
        self.event_button = event_button

    def event_inside(self, event: sdl2.SDL_Event) -> bool:
        if event.type == self.event_type:
            if event.button.button == self.event_button:
                if self.on_click:
                    self.on_click()
                return True
        return False
