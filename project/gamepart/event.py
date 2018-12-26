import logging
import ctypes
import typing

import sdl2
import sdl2.ext


logger = logging.getLogger(__name__)


class UserEventType:
    """Factory for custom sdl2 event types"""

    def __init__(self):
        self.type: int = sdl2.SDL_RegisterEvents(1)
        logger.debug(f"New event type {self!r}")

    def emit(self, code: int = 0, data: typing.Any = None) -> sdl2.SDL_Event:
        event = sdl2.SDL_Event()
        sdl2.SDL_memset(ctypes.byref(event), 0, ctypes.sizeof(sdl2.SDL_Event))
        event.type = self.type
        event.user.code = code
        event.user.data1 = ctypes.cast(
            ctypes.pointer(ctypes.py_object(data)), ctypes.c_void_p
        )
        if sdl2.SDL_PushEvent(event) != 1:
            raise sdl2.ext.SDLError()
        return event

    def dereference_data(self, event: sdl2.SDL_Event) -> typing.Any:
        """Its broken probably due to using a 32 bit pointer with a 64 bit address :("""

        if event.type == self.type and event.user.data1:
            obj = ctypes.cast(event.user.data1, ctypes.POINTER(ctypes.py_object))
            return obj.contents.value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.type!r})"


T = typing.TypeVar("T", bound=typing.Hashable)
TD = typing.TypeVar("TD")


class Dispatcher(typing.Generic[T, TD]):
    """Callback storage and dispatcher"""

    def __init__(self):
        self.callbacks: typing.Dict[T, typing.List[typing.Callable]] = {}

    def on(self, key: T, callback: typing.Callable):
        if key not in self.callbacks:
            self.callbacks[key] = []
        self.callbacks[key].append(callback)

    @staticmethod
    def get_key(data: TD) -> T:
        return data  # type: ignore

    def __call__(self, data: TD, *args, **kwargs):
        key = self.get_key(data)
        for callback in self.callbacks.get(key, []):
            ret = callback(data, *args, **kwargs)
            if ret:  # Stop event propagation
                return ret

    def clear(self):
        self.callbacks.clear()


class EventDispatcher(Dispatcher[int, sdl2.SDL_Event]):
    """Dispatcher for SDL_Events"""

    @staticmethod
    def get_key(event: sdl2.SDL_Event):
        return event.type


class KeyEventDispatcher(Dispatcher[typing.Tuple[int, int], sdl2.SDL_KeyboardEvent]):
    """Dispatcher for keyboards event"""

    @staticmethod
    def get_key(event: sdl2.SDL_KeyboardEvent):
        return event.type, event.key.keysym.sym

    def on_up(self, key: sdl2.SDL_Keycode, callback: typing.Callable):
        return self.on((sdl2.SDL_KEYUP, key), callback)

    def on_down(self, key: sdl2.SDL_Keycode, callback: typing.Callable):
        return self.on((sdl2.SDL_KEYDOWN, key), callback)


class MouseEventDispatcher(
    Dispatcher[typing.Tuple[int, int], sdl2.SDL_MouseButtonEvent]
):
    """Dispatcher for mouse button event"""

    @staticmethod
    def get_key(event: sdl2.SDL_MouseButtonEvent):
        return event.type, event.button.button

    def on_up(self, key: int, callback: typing.Callable):
        return self.on((sdl2.SDL_MOUSEBUTTONUP, key), callback)

    def on_down(self, key: int, callback: typing.Callable):
        return self.on((sdl2.SDL_MOUSEBUTTONDOWN, key), callback)
