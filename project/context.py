import typing

from gamepart.context import Context


class MyContext(Context):
    console: typing.Any = None
