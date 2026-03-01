"""Unit tests for project context (MyContext)."""

import sdl2
from context import MyContext
from gamepart.context import Context
from settings import KeyBinds


class TestMyContext:
    def test_extends_context(self) -> None:
        ctx = MyContext(last_scene=None)
        assert isinstance(ctx, Context)
        assert ctx.last_scene is None

    def test_default_console_is_none(self) -> None:
        ctx = MyContext(last_scene=None)
        assert ctx.console is None

    def test_uses_load_key_binds_when_key_binds_not_passed(self) -> None:
        ctx = MyContext(last_scene=None)
        assert isinstance(ctx.key_binds, KeyBinds)
        assert ctx.key_binds.jump == sdl2.SDLK_w

    def test_uses_passed_key_binds(self) -> None:
        custom = KeyBinds()
        custom.jump = 12345
        ctx = MyContext(last_scene=None, key_binds=custom)
        assert ctx.key_binds is custom
        assert ctx.key_binds.jump == 12345
