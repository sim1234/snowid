import ctypes
import itertools
import logging
import typing

import sdl2
import sdl2.ext

logger = logging.getLogger(__name__)


def _callback_name(callback: typing.Any) -> str:
    if hasattr(callback, "__self__") and hasattr(callback, "__name__"):
        return f"{type(callback.__self__).__name__}.{callback.__name__}"
    return getattr(callback, "__name__", repr(callback))


class UserEventType:
    """Factory for custom SDL2 user events.

    Each instance registers a unique event type that can be used to emit
    custom events into the SDL event queue.
    """

    def __init__(self) -> None:
        self.type: int = sdl2.SDL_RegisterEvents(1)
        logger.debug(f"New event type {self!r}")

    def emit(self, code: int = 0, data: typing.Any = None) -> sdl2.SDL_Event:
        """Push a custom event to the SDL event queue."""
        event = sdl2.SDL_Event()
        sdl2.SDL_memset(
            ctypes.byref(event),  # type: ignore[arg-type]
            0,
            ctypes.sizeof(sdl2.SDL_Event),
        )
        event.type = self.type
        event.user.code = code
        event.user.data1 = ctypes.cast(
            ctypes.pointer(ctypes.py_object(data)), ctypes.c_void_p
        ).value
        if sdl2.SDL_PushEvent(event) != 1:
            raise sdl2.ext.SDLError()
        return event

    def dereference_data(self, event: sdl2.SDL_Event) -> typing.Any:
        """Its broken probably due to using a 32 bit pointer with a 64 bit address :("""

        if event.type == self.type and event.user.data1:
            obj = ctypes.cast(event.user.data1, ctypes.POINTER(ctypes.py_object))
            return obj.contents.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.type!r})"


KeyT = typing.TypeVar("KeyT", bound=typing.Hashable)
DataT = typing.TypeVar("DataT")


class Dispatcher(typing.Generic[KeyT, DataT]):
    """Generic callback dispatcher with key-based routing and propagation control.

    Callbacks are invoked in registration order. A callback returning a truthy
    value stops propagation to subsequent callbacks.

    KeyT: Hashable type used to route data to specific callbacks.
    DataT: Type of data passed to callbacks when dispatching.
    """

    def __init__(self) -> None:
        self.before_chained: list[typing.Callable[[DataT], typing.Any]] = []
        self.callbacks: dict[KeyT, list[typing.Callable[[DataT], typing.Any]]] = {}
        self.after_chained: list[typing.Callable[[DataT], typing.Any]] = []

    def on(self, key: KeyT, callback: typing.Callable[[DataT], typing.Any]) -> None:
        """Register a callback for a specific key."""
        if key not in self.callbacks:
            self.callbacks[key] = []
        self.callbacks[key].append(callback)

    def chain_before(self, callback: typing.Callable[[DataT], typing.Any]) -> None:
        """Register a callback that runs for all data, before keyed callbacks."""
        self.before_chained.append(callback)

    def chain_after(self, callback: typing.Callable[[DataT], typing.Any]) -> None:
        """Register a callback that runs for all data, after keyed callbacks."""
        self.after_chained.append(callback)

    @staticmethod
    def get_key(data: DataT) -> KeyT:
        """Extract the routing key from data. Override in subclasses."""
        return data  # type: ignore

    def __call__(self, data: DataT) -> typing.Any:
        """Dispatch data to matching callbacks. Returns first truthy callback result."""
        key = self.get_key(data)
        for callback in itertools.chain(
            self.before_chained, self.callbacks.get(key, []), self.after_chained
        ):
            ret = callback(data)
            if ret:
                _name = _callback_name(callback)
                logger.debug(f"Event propagation stopped by {_name}: {ret!r}")
                return ret
        return None

    def clear(self) -> None:
        """Remove all registered callbacks."""
        self.before_chained.clear()
        self.callbacks.clear()
        self.after_chained.clear()

    def remove_key(self, key: KeyT) -> None:
        """Remove all callbacks registered for the given key."""
        self.callbacks.pop(key, None)

    def noop(self, data: DataT) -> None:
        """Callback placeholder that does nothing."""

    def stop(self, data: DataT) -> bool:
        """Callback that stops event propagation."""
        return True


class EventDispatcher(Dispatcher[int, sdl2.SDL_Event]):
    """Dispatcher routing SDL events by event type (e.g. SDL_KEYDOWN, SDL_QUIT)."""

    @staticmethod
    def get_key(event: sdl2.SDL_Event) -> int:
        return event.type


class KeyboardEventDispatcher(Dispatcher[tuple[int, int], sdl2.SDL_Event]):
    """Dispatcher routing keyboard events by (event_type, key_sym) tuple."""

    @staticmethod
    def get_key(event: sdl2.SDL_Event) -> tuple[int, int]:
        sub_event: sdl2.SDL_KeyboardEvent = event.key
        # TODO: make sure mypy picks this up
        return event.type, sub_event.keysym.sym

    def attach_to(self, dispatcher: EventDispatcher) -> None:
        """Register this dispatcher as a handler for keyboard events."""
        dispatcher.on(sdl2.SDL_KEYDOWN, self)
        dispatcher.on(sdl2.SDL_KEYUP, self)

    def on_up(
        self, key: int, callback: typing.Callable[[sdl2.SDL_Event], typing.Any]
    ) -> None:
        """Register a callback for key release events."""
        self.on((sdl2.SDL_KEYUP, key), callback)

    def on_down(
        self, key: int, callback: typing.Callable[[sdl2.SDL_Event], typing.Any]
    ) -> None:
        """Register a callback for key press events."""
        self.on((sdl2.SDL_KEYDOWN, key), callback)


class MouseButtonEventDispatcher(Dispatcher[tuple[int, int], sdl2.SDL_Event]):
    """Dispatcher routing mouse button events by (event_type, button) tuple."""

    @staticmethod
    def get_key(event: sdl2.SDL_Event) -> tuple[int, int]:
        sub_event: sdl2.SDL_MouseButtonEvent = event.button
        # TODO: make sure mypy picks this up
        return event.type, sub_event.button

    def attach_to(self, dispatcher: EventDispatcher) -> None:
        """Register this dispatcher as a handler for mouse button events."""
        dispatcher.on(sdl2.SDL_MOUSEBUTTONDOWN, self)
        dispatcher.on(sdl2.SDL_MOUSEBUTTONUP, self)

    def on_up(
        self, key: int, callback: typing.Callable[[sdl2.SDL_Event], typing.Any]
    ) -> None:
        """Register a callback for mouse button release events."""
        self.on((sdl2.SDL_MOUSEBUTTONUP, key), callback)

    def on_down(
        self, key: int, callback: typing.Callable[[sdl2.SDL_Event], typing.Any]
    ) -> None:
        """Register a callback for mouse button press events."""
        self.on((sdl2.SDL_MOUSEBUTTONDOWN, key), callback)
