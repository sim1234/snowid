import ctypes
import functools
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

import sdl2

P = ParamSpec("P")
R = TypeVar("R")

EVENT_TYPE_NAMES: dict[int, str] = {
    sdl2.SDL_QUIT: "QUIT",
    sdl2.SDL_APP_TERMINATING: "APP_TERMINATING",
    sdl2.SDL_APP_LOWMEMORY: "APP_LOWMEMORY",
    sdl2.SDL_APP_WILLENTERBACKGROUND: "APP_WILLENTERBACKGROUND",
    sdl2.SDL_APP_DIDENTERBACKGROUND: "APP_DIDENTERBACKGROUND",
    sdl2.SDL_APP_WILLENTERFOREGROUND: "APP_WILLENTERFOREGROUND",
    sdl2.SDL_APP_DIDENTERFOREGROUND: "APP_DIDENTERFOREGROUND",
    sdl2.SDL_LOCALECHANGED: "LOCALECHANGED",
    sdl2.SDL_DISPLAYEVENT: "DISPLAYEVENT",
    sdl2.SDL_WINDOWEVENT: "WINDOWEVENT",
    sdl2.SDL_SYSWMEVENT: "SYSWMEVENT",
    sdl2.SDL_KEYDOWN: "KEYDOWN",
    sdl2.SDL_KEYUP: "KEYUP",
    sdl2.SDL_TEXTEDITING: "TEXTEDITING",
    sdl2.SDL_TEXTINPUT: "TEXTINPUT",
    sdl2.SDL_KEYMAPCHANGED: "KEYMAPCHANGED",
    sdl2.SDL_TEXTEDITING_EXT: "TEXTEDITING_EXT",
    sdl2.SDL_MOUSEMOTION: "MOUSEMOTION",
    sdl2.SDL_MOUSEBUTTONDOWN: "MOUSEBUTTONDOWN",
    sdl2.SDL_MOUSEBUTTONUP: "MOUSEBUTTONUP",
    sdl2.SDL_MOUSEWHEEL: "MOUSEWHEEL",
    sdl2.SDL_JOYAXISMOTION: "JOYAXISMOTION",
    sdl2.SDL_JOYBALLMOTION: "JOYBALLMOTION",
    sdl2.SDL_JOYHATMOTION: "JOYHATMOTION",
    sdl2.SDL_JOYBUTTONDOWN: "JOYBUTTONDOWN",
    sdl2.SDL_JOYBUTTONUP: "JOYBUTTONUP",
    sdl2.SDL_JOYDEVICEADDED: "JOYDEVICEADDED",
    sdl2.SDL_JOYDEVICEREMOVED: "JOYDEVICEREMOVED",
    sdl2.SDL_JOYBATTERYUPDATED: "JOYBATTERYUPDATED",
    sdl2.SDL_CONTROLLERAXISMOTION: "CONTROLLERAXISMOTION",
    sdl2.SDL_CONTROLLERBUTTONDOWN: "CONTROLLERBUTTONDOWN",
    sdl2.SDL_CONTROLLERBUTTONUP: "CONTROLLERBUTTONUP",
    sdl2.SDL_CONTROLLERDEVICEADDED: "CONTROLLERDEVICEADDED",
    sdl2.SDL_CONTROLLERDEVICEREMOVED: "CONTROLLERDEVICEREMOVED",
    sdl2.SDL_CONTROLLERDEVICEREMAPPED: "CONTROLLERDEVICEREMAPPED",
    sdl2.SDL_CONTROLLERTOUCHPADDOWN: "CONTROLLERTOUCHPADDOWN",
    sdl2.SDL_CONTROLLERTOUCHPADMOTION: "CONTROLLERTOUCHPADMOTION",
    sdl2.SDL_CONTROLLERTOUCHPADUP: "CONTROLLERTOUCHPADUP",
    sdl2.SDL_CONTROLLERSENSORUPDATE: "CONTROLLERSENSORUPDATE",
    sdl2.SDL_FINGERDOWN: "FINGERDOWN",
    sdl2.SDL_FINGERUP: "FINGERUP",
    sdl2.SDL_FINGERMOTION: "FINGERMOTION",
    sdl2.SDL_DOLLARGESTURE: "DOLLARGESTURE",
    sdl2.SDL_DOLLARRECORD: "DOLLARRECORD",
    sdl2.SDL_MULTIGESTURE: "MULTIGESTURE",
    sdl2.SDL_CLIPBOARDUPDATE: "CLIPBOARDUPDATE",
    sdl2.SDL_DROPFILE: "DROPFILE",
    sdl2.SDL_DROPTEXT: "DROPTEXT",
    sdl2.SDL_DROPBEGIN: "DROPBEGIN",
    sdl2.SDL_DROPCOMPLETE: "DROPCOMPLETE",
    sdl2.SDL_AUDIODEVICEADDED: "AUDIODEVICEADDED",
    sdl2.SDL_AUDIODEVICEREMOVED: "AUDIODEVICEREMOVED",
    sdl2.SDL_SENSORUPDATE: "SENSORUPDATE",
    sdl2.SDL_RENDER_TARGETS_RESET: "RENDER_TARGETS_RESET",
    sdl2.SDL_RENDER_DEVICE_RESET: "RENDER_DEVICE_RESET",
    sdl2.SDL_POLLSENTINEL: "POLLSENTINEL",
}

EVENT_TYPE_TO_SUBEVENT: dict[int, tuple[str, tuple[str, ...]]] = {
    sdl2.SDL_DISPLAYEVENT: ("display", ("display", "event", "data1")),
    sdl2.SDL_WINDOWEVENT: ("window", ("windowID", "event", "data1", "data2")),
    sdl2.SDL_KEYDOWN: ("key", ("windowID", "state", "repeat", "keysym")),
    sdl2.SDL_KEYUP: ("key", ("windowID", "state", "repeat", "keysym")),
    sdl2.SDL_TEXTEDITING: ("edit", ("windowID", "text", "start", "length")),
    sdl2.SDL_TEXTEDITING_EXT: ("editExt", ("windowID", "text", "start", "length")),
    sdl2.SDL_TEXTINPUT: ("text", ("windowID", "text")),
    sdl2.SDL_MOUSEMOTION: (
        "motion",
        ("windowID", "which", "state", "x", "y", "xrel", "yrel"),
    ),
    sdl2.SDL_MOUSEBUTTONDOWN: (
        "button",
        ("windowID", "which", "button", "state", "clicks", "x", "y"),
    ),
    sdl2.SDL_MOUSEBUTTONUP: (
        "button",
        ("windowID", "which", "button", "state", "clicks", "x", "y"),
    ),
    sdl2.SDL_MOUSEWHEEL: ("wheel", ("windowID", "which", "x", "y", "direction")),
    sdl2.SDL_JOYAXISMOTION: ("jaxis", ("which", "axis", "value")),
    sdl2.SDL_JOYBALLMOTION: ("jball", ("which", "ball", "xrel", "yrel")),
    sdl2.SDL_JOYHATMOTION: ("jhat", ("which", "hat", "value")),
    sdl2.SDL_JOYBUTTONDOWN: ("jbutton", ("which", "button", "state")),
    sdl2.SDL_JOYBUTTONUP: ("jbutton", ("which", "button", "state")),
    sdl2.SDL_JOYDEVICEADDED: ("jdevice", ("which",)),
    sdl2.SDL_JOYDEVICEREMOVED: ("jdevice", ("which",)),
    sdl2.SDL_JOYBATTERYUPDATED: ("jbattery", ("which", "level")),
    sdl2.SDL_CONTROLLERAXISMOTION: ("caxis", ("which", "axis", "value")),
    sdl2.SDL_CONTROLLERBUTTONDOWN: ("cbutton", ("which", "button", "state")),
    sdl2.SDL_CONTROLLERBUTTONUP: ("cbutton", ("which", "button", "state")),
    sdl2.SDL_CONTROLLERDEVICEADDED: ("cdevice", ("which",)),
    sdl2.SDL_CONTROLLERDEVICEREMOVED: ("cdevice", ("which",)),
    sdl2.SDL_CONTROLLERDEVICEREMAPPED: ("cdevice", ("which",)),
    sdl2.SDL_CONTROLLERTOUCHPADDOWN: (
        "ctouchpad",
        ("which", "touchpad", "finger", "x", "y", "pressure"),
    ),
    sdl2.SDL_CONTROLLERTOUCHPADMOTION: (
        "ctouchpad",
        ("which", "touchpad", "finger", "x", "y", "pressure"),
    ),
    sdl2.SDL_CONTROLLERTOUCHPADUP: (
        "ctouchpad",
        ("which", "touchpad", "finger", "x", "y", "pressure"),
    ),
    sdl2.SDL_CONTROLLERSENSORUPDATE: ("csensor", ("which", "sensor", "data")),
    sdl2.SDL_AUDIODEVICEADDED: ("adevice", ("which", "iscapture")),
    sdl2.SDL_AUDIODEVICEREMOVED: ("adevice", ("which", "iscapture")),
    sdl2.SDL_SENSORUPDATE: ("sensor", ("which", "data")),
    sdl2.SDL_FINGERDOWN: (
        "tfinger",
        ("touchId", "fingerId", "x", "y", "dx", "dy", "pressure"),
    ),
    sdl2.SDL_FINGERUP: (
        "tfinger",
        ("touchId", "fingerId", "x", "y", "dx", "dy", "pressure"),
    ),
    sdl2.SDL_FINGERMOTION: (
        "tfinger",
        ("touchId", "fingerId", "x", "y", "dx", "dy", "pressure"),
    ),
    sdl2.SDL_MULTIGESTURE: (
        "mgesture",
        ("touchId", "dTheta", "dDist", "x", "y", "numFingers"),
    ),
    sdl2.SDL_DOLLARGESTURE: (
        "dgesture",
        ("touchId", "gestureId", "numFingers", "error", "x", "y"),
    ),
    sdl2.SDL_DOLLARRECORD: (
        "dgesture",
        ("touchId", "gestureId", "numFingers", "error", "x", "y"),
    ),
    sdl2.SDL_DROPFILE: ("drop", ("file", "windowID")),
    sdl2.SDL_DROPTEXT: ("drop", ("file", "windowID")),
    sdl2.SDL_DROPBEGIN: ("drop", ("windowID",)),
    sdl2.SDL_DROPCOMPLETE: ("drop", ("windowID",)),
}


KEYMOD_FLAGS: list[tuple[int, str]] = [
    (sdl2.KMOD_LSHIFT, "LShift"),
    (sdl2.KMOD_RSHIFT, "RShift"),
    (sdl2.KMOD_LCTRL, "LCtrl"),
    (sdl2.KMOD_RCTRL, "RCtrl"),
    (sdl2.KMOD_LALT, "LAlt"),
    (sdl2.KMOD_RALT, "RAlt"),
    (sdl2.KMOD_LGUI, "LGui"),
    (sdl2.KMOD_RGUI, "RGui"),
    (sdl2.KMOD_NUM, "Num"),
    (sdl2.KMOD_CAPS, "Caps"),
    (sdl2.KMOD_MODE, "Mode"),
    (sdl2.KMOD_SCROLL, "Scroll"),
]


def format_keymod(mod: int) -> str:
    if mod == 0:
        return ""
    active_mods = [name for flag, name in KEYMOD_FLAGS if mod & flag]
    return "+".join(active_mods) if active_mods else ""


def format_keysym(keysym: sdl2.SDL_Keysym) -> str:
    key_name_bytes = sdl2.SDL_GetKeyName(keysym.sym)
    if key_name_bytes:
        key_name = key_name_bytes.decode("utf-8", errors="replace")
    else:
        key_name = f"sym={keysym.sym}"
    mod_str = format_keymod(keysym.mod)
    if mod_str:
        return f"{mod_str}+{key_name}"
    return key_name


def format_event(event: sdl2.SDL_Event) -> str:
    event_type = event.type
    timestamp = event.common.timestamp

    type_name = EVENT_TYPE_NAMES.get(event_type)
    if type_name is None:
        if event_type >= sdl2.SDL_USEREVENT:
            type_name = f"USER({event_type})"
        else:
            type_name = f"UNKNOWN({event_type})"

    subevent_info = EVENT_TYPE_TO_SUBEVENT.get(event_type)
    if subevent_info is None:
        if event_type >= sdl2.SDL_USEREVENT:
            user_event = event.user
            return f"{type_name} @{timestamp} code={user_event.code}"
        return f"{type_name} @{timestamp}"

    attr_name, fields = subevent_info
    subevent = getattr(event, attr_name)

    field_parts = []
    for field in fields:
        value = getattr(subevent, field, None)
        if value is not None:
            if field == "keysym":
                formatted_value = format_keysym(value)
            elif field == "text" and isinstance(value, bytes):
                formatted_value = value.decode("utf-8", errors="replace")
            elif isinstance(value, bytes):
                formatted_value = value.decode("utf-8", errors="replace")
            else:
                formatted_value = str(value)
            field_parts.append(f"{field}={formatted_value}")

    return f"{type_name} @{timestamp} {' '.join(field_parts)}"


def get_mouse_state() -> tuple[int, int, int]:
    """Returns current mouse x, y and button state"""

    x, y = ctypes.c_int(0), ctypes.c_int(0)
    button_state = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
    return x.value, y.value, button_state


def get_clipboard_text(encoding: str = "utf-8") -> str:
    """Returns clipboard contents"""

    data = sdl2.SDL_GetClipboardText()
    if data is None:
        return ""
    try:
        return data.decode(encoding)
    except UnicodeDecodeError:
        return ""


def cached_depends_on(
    *depends_on: str,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        cache_key = f"__cache_depends_on__{func.__name__}"

        @functools.wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> R:
            cache: tuple[tuple[Any, ...], R] | None = getattr(self, cache_key, None)
            current_properties = tuple(getattr(self, prop) for prop in depends_on)
            if cache is None or current_properties != cache[0]:
                result = func(self, *args, **kwargs)
                setattr(self, cache_key, (current_properties, result))
                return result
            return cache[1]

        return wrapper  # type: ignore[return-value]

    return decorator
