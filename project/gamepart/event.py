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


class Dispatcher:
    """Callback storage and dispatcher"""

    def __init__(self):
        self.callbacks: typing.Dict[typing.Hashable, typing.List[typing.Callable]] = {}

    def on(self, key: typing.Hashable, callback: typing.Callable):
        if key not in self.callbacks:
            self.callbacks[key] = []
        self.callbacks[key].append(callback)

    def __call__(self, key: typing.Hashable, *args, **kwargs):
        for callback in self.callbacks.get(key, []):
            ret = callback(*args, **kwargs)
            if ret:  # Stop event propagation
                return ret


class EventDispatcher(Dispatcher):
    """Dispatcher for SDL_Events"""

    def __call__(self, event: sdl2.SDL_Event, *args, **kwargs):
        return super(EventDispatcher, self).__call__(event.type, event)


class KeyEventDispatcher(Dispatcher):
    """Dispatcher for keyboards event"""

    def __call__(self, event: sdl2.SDL_KeyboardEvent, *args, **kwargs):
        return super(KeyEventDispatcher, self).__call__(
            (event.type, event.key.keysym.sym), event
        )

    def on_up(self, key: sdl2.SDL_Keycode, callback: typing.Callable):
        return self.on((sdl2.SDL_KEYUP, key), callback)

    def on_down(self, key: sdl2.SDL_Keycode, callback: typing.Callable):
        return self.on((sdl2.SDL_KEYDOWN, key), callback)


class MouseEventDispatcher(Dispatcher):
    """Dispatcher for mouse button event"""

    def __call__(self, event: sdl2.SDL_MouseButtonEvent, *args, **kwargs):
        return super(MouseEventDispatcher, self).__call__(
            (event.type, event.button.button), event
        )

    def on_up(self, key: int, callback: typing.Callable):
        return self.on((sdl2.SDL_MOUSEBUTTONUP, key), callback)

    def on_down(self, key: int, callback: typing.Callable):
        return self.on((sdl2.SDL_MOUSEBUTTONDOWN, key), callback)
