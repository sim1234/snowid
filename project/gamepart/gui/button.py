from __future__ import annotations

from collections.abc import Callable
from typing import Any

import sdl2


class OnClickMixin:
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

    def event_inside(self, event: sdl2.SDL_Event) -> Any:
        if event.type == self.event_type:
            if event.button.button == self.event_button:
                self._on_click(event)
        return False

    def _on_click(self, event: sdl2.SDL_Event) -> Any:
        if self.on_click:
            self.on_click()
        return self.on_click


class OnHoverMixin:
    hovered: bool = False
    contains_point: Callable[[int, int], bool]

    def __init__(
        self,
        *args: Any,
        on_hover: Callable[[], None] | None = None,
        on_unhover: Callable[[], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.on_hover: Callable[[], None] | None = on_hover
        self.on_unhover: Callable[[], None] | None = on_unhover

    def event(self, event: sdl2.SDL_Event) -> Any:
        if event.type == sdl2.SDL_MOUSEMOTION:
            x, y = event.motion.x, event.motion.y
            prev_hovered = self.hovered
            self.hovered = self.contains_point(x, y)
            if not prev_hovered and self.hovered:
                self._on_hover(event)
            if prev_hovered and not self.hovered:
                self._on_unhover(event)
        return None

    def _on_unhover(self, event: sdl2.SDL_Event) -> None:
        if self.on_unhover is not None:
            self.on_unhover()

    def _on_hover(self, event: sdl2.SDL_Event) -> None:
        if self.on_hover is not None:
            self.on_hover()
