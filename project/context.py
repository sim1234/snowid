import typing

from gamepart.context import Context
from settings import KeyBinds, load_key_binds


class MyContext(Context):
    console: typing.Any = None

    def __init__(
        self,
        last_scene: typing.Any,
        *,
        key_binds: KeyBinds | None = None,
    ) -> None:
        super().__init__(last_scene)
        self.key_binds: KeyBinds = key_binds or load_key_binds()
