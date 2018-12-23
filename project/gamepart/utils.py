import typing
import ctypes

import sdl2


def get_mouse_state() -> typing.Tuple[int, int, int]:
    """Returns current mouse x, y and button state"""

    x, y = ctypes.c_int(0), ctypes.c_int(0)
    button_state = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
    return x.value, y.value, button_state
